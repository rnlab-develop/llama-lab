import functools
import json
import math
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Generator, List, Optional, Tuple

import numpy as np
import requests
from tqdm.auto import tqdm

from llama_app.clients.embeddings import (EmbedContent, EmbeddingsService,
                                          EmbedRequest, RetrievalType)
from llama_app.populate.html_prase import clean_html
from llama_app.settings import SETTINGS

gecko = EmbeddingsService(SETTINGS.embeddings)

# List of article titles you're interested in
ARTICLE_TITLES = [
    "Ludwig van Beethoven",
    "Wolfgang Amadeus Mozart",
    "Johann Sebastian Bach",
    "Franz Joseph Haydn",
    "George Frideric Handel",
    "Franz Schubert",
    "Frederic Chopin",
    "Pyotr Ilyich Tchaikovsky",
    "Antonio Vivaldi",
    "Johannes Brahms",
    "Giuseppe Verdi",
    "Richard Wagner",
    "Claude Debussy",
    "Igor Stravinsky",
    "Antonin Dvorak",
    "Gustav Mahler",
    "Joseph Haydn",
    "Robert Schumann",
    "George Gershwin",
    "Sergei Rachmaninoff",
]


# Generator function to yield batches of sentences
def generate_batches(
    sentences: List[str], batch_size: int
) -> Generator[List[str], None, None]:
    for i in range(0, len(sentences), batch_size):
        yield sentences[i : i + batch_size]


def encode_text_to_embedding_batched(
    sentences: List[str], api_calls_per_second: int = 10, batch_size: int = 5
) -> Tuple[List[bool], np.ndarray]:
    embeddings_list: List[List[float]] = []

    # Prepare the batches using a generator
    batches = generate_batches(sentences, batch_size)

    seconds_per_job = 1 / api_calls_per_second

    with ThreadPoolExecutor() as executor:
        futures = []
        for batch in tqdm(
            batches, total=math.ceil(len(sentences) / batch_size), position=0
        ):
            futures.append(
                executor.submit(functools.partial(compute_embeddings), batch)
            )
            time.sleep(seconds_per_job)

        for future in futures:
            embeddings_list.extend(future.result())

    is_successful = [
        embedding is not None for sentence, embedding in zip(sentences, embeddings_list)
    ]
    embeddings_list_successful = np.squeeze(
        np.stack([embedding for embedding in embeddings_list if embedding is not None])
    )
    return is_successful, embeddings_list_successful


def compute_embeddings(sentences: List[str]) -> List[Optional[List[float]]]:
    # The API accepts a maximum of 3,072 input tokens and outputs 768-dimensional vector embeddings.
    vector = gecko.predict(
        payload=EmbedRequest(
            instances=[
                EmbedContent(
                    content=sentence,
                    task_type=RetrievalType.RETRIEVAL_DOCUMENT.value,
                )
                for sentence in sentences
            ]
        )
    )
    return vector["predictions"][0]["embeddings"]["values"]


# we only want to run the data set if no
def import_has_run(conn):
    cur = conn.cursor()
    cur.execute("SELECT count(1) FROM embeddings")
    res = cur.fetchone()[0]
    return res != 0


def get_wikipedia_article(title):
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "titles": title,
        "prop": "extracts",  # Get the article text
        "exintro": True,  # Get only the introduction text
    }
    response = requests.get(url, params=params)
    data = response.json()
    page_id = list(data["query"]["pages"].keys())[0]
    extract = data["query"]["pages"][page_id].get("extract", "")
    return extract


def insert_into_embeddings(conn, text, vector):
    cur = conn.cursor()
    cur.execute("INSERT INTO embeddings (name, vector) VALUES (%s, %s)", (text, vector))
    conn.commit()


def run_insert_dataset(conn):
    if not import_has_run(conn):
        for title in ARTICLE_TITLES:  # Generate 1000 fake records
            text = clean_html(get_wikipedia_article(title))
            is_successful, vector = encode_text_to_embedding_batched(
                [f"Title: {title}. Body: {text}"]
            )
            if is_successful and text:
                insert_into_embeddings(conn, text, json.dumps(vector.tolist()))
    else:
        return "import already ran. success"
    return "success"
