from faker import Faker
import json

from llama_app.clients.embeddings import Content, EmbeddingsService, EmbedRequest
from llama_app.settings import SETTINGS

gecko = EmbeddingsService(SETTINGS.embeddings)

# Set up the Faker instance
fake = Faker()


def generate_paragraph():
    """Generate a fake paragraph."""
    return fake.paragraph()


def compute_embeddings(text):
    vector = gecko.predict(payload=EmbedRequest(instances=[Content(content=text)]))
    return vector


def insert_into_embeddings(conn, text, vector):
    cur = conn.cursor()
    cur.execute("INSERT INTO embeddings (name, vector) VALUES (%s, %s)", (text, vector))
    conn.commit()

# we only want to run the data set if no
def import_has_run(conn):
    cur = conn.cursor()
    cur.execute("SELECT count(1) FROM embeddings")
    res = cur.fetchone()[0]
    return res != 0


def run_insert_dataset(conn):
    if not import_has_run(conn):
        for _ in range(10):  # Generate 1000 fake records
            text = generate_paragraph()
            vector = compute_embeddings(text)["predictions"][0]["embeddings"]["values"]
            insert_into_embeddings(conn, text, json.dumps(vector))
    return "success"
