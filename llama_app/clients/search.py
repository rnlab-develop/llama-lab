from dataclasses import asdict
from typing import List

import psycopg2

from llama_app.clients.embeddings import EmbedContent, EmbedRequest, gecko
from llama_app.models.search import Document
from llama_app.settings import SETTINGS


class EmbeddingsSearchEngine:
    def __init__(self, connection_settings, embeddings_service):
        self.connection_settings = connection_settings
        self.embeddings_service = embeddings_service

    def _fetch_embeddings_from_service(self, text: str) -> List[float]:
        payload = EmbedRequest(instances=[EmbedContent(content=text)])
        return self.embeddings_service.predict(payload)["predictions"][0]["embeddings"][
            "values"
        ]

    def _query_similar_documents_from_db(
        self, embeddings: List[float]
    ) -> List[Document]:
        documents = []
        with psycopg2.connect(**asdict(self.connection_settings)) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT id, name FROM embeddings ORDER BY vector <-> %s::vector LIMIT 1",
                    (embeddings,),
                )
                result = cur.fetchall()
                documents = [Document(id=row[0], name=row[1]) for row in result]
        return documents

    def find_similar_by_text(self, text: str) -> List[Document]:
        embeddings = self._fetch_embeddings_from_service(text)
        return self._query_similar_documents_from_db(embeddings)


embeddings_search_engine = EmbeddingsSearchEngine(SETTINGS.connection, gecko)
