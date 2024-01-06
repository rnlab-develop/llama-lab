from enum import Enum
from typing import Any, Dict, List, Optional, Union

import requests
from pydantic import BaseModel

from llama_app.settings import SETTINGS, VertexEmbedConfig
from llama_app.utilities import get_gcp_token


class RetrievalType(str, Enum):
    RETRIEVAL_QUERY = "RETRIEVAL_QUERY"
    RETRIEVAL_DOCUMENT = "RETRIEVAL_DOCUMENT"
    SEMANTIC_SIMILARITY = "SEMANTIC_SIMILARITY"
    CLASSIFICATION = "CLASSIFICATION"
    CLUSTERING = "CLUSTERING"


class EmbedContent(BaseModel):
    content: str
    title: Optional[str] = None
    task_type: Optional[RetrievalType]


class EmbedRequest(BaseModel):
    instances: List[EmbedContent]


class EmbeddingsService:
    BASE_URL: str = "https://{REGION}-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/{REGION}/publishers/google/models/{EMBED_ENDPOINT_ID}:predict"

    def __init__(self, vertex_config: VertexEmbedConfig, token: str = None) -> None:
        self.project_id: str = vertex_config.project_id
        self.region: str = vertex_config.region
        self.endpoint: str = vertex_config.endpoint_id

    def predict(
        self,
        payload: EmbedRequest,
    ) -> Union[Dict[str, Any], Any]:
        token = get_gcp_token()
        headers: Dict[str, str] = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        """
        Makes a prediction to get embeddings for the provided text.
        """
        response: requests.Response = requests.post(
            self.BASE_URL.format(
                PROJECT_ID=self.project_id,
                REGION=self.region,
                EMBED_ENDPOINT_ID=self.endpoint,
            ),
            json=payload.model_dump(),
            headers=headers,
        )

        if response.status_code != 200:
            raise Exception(f"Error {response.status_code}: {response.text}")

        return response.json()


gecko = EmbeddingsService(SETTINGS.embeddings)
