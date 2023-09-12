from faker import Faker

from llama_app.embeddings import Content, EmbedRequest, EmbeddingsService
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

def generate_dataset():
    data = []
    for _ in range(1000):  # Generate 1000 fake records
        text = generate_paragraph()
        vector = compute_embeddings(text)
        data.append((text, vector))
    return data