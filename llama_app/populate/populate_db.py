from faker import Faker
import psycopg2
import json
import os

from llama_app.embeddings import Content, EmbeddingsService, EmbedRequest
from llama_app.settings import SETTINGS
from dataclasses import asdict

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


def run_insert_dataset(conn):
    filepath = os.path.join(os.path.dirname(os.path.realpath(__file__)), ".db.lock")
    if os.path.exists(filepath):
        return "Database is already populated. Skipping"
    for _ in range(10):  # Generate 1000 fake records
        text = generate_paragraph()
        vector = compute_embeddings(text)["predictions"][0]["embeddings"]["values"]
        insert_into_embeddings(conn, text, json.dumps(vector))
    with open(filepath, "w+") as f:
        json.dump("Data load succeeded!", f)
    return "success"
