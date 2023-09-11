from dataclasses import dataclass
from typing import Any, Dict, List, Union

import requests
from pydantic import BaseModel

from llama_app.settings import VertexEmbedConfig
from llama_app.utilities import get_gcp_token


class Content(BaseModel):
    content: str


class EmbedRequest(BaseModel):
    instances: List[Content]


class EmbeddingsService:
    BASE_URL: str = "https://{REGION}-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/{REGION}/publishers/google/models/{EMBED_ENDPOINT_ID}:predict"

    def __init__(self, vertex_config: VertexEmbedConfig, token: str = None) -> None:
        self.project_id: str = vertex_config.project_id
        self.region: str = vertex_config.region
        self.endpoint: str = vertex_config.endpoint_id

    def predict(
        self,
        payload: str,
    ) -> Union[Dict[str, Any], Any]:
        token = get_gcp_token()
        headers: Dict[str, str] = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        """
        Makes a prediction to get embeddings for the provided text.
        """
        print(payload)
        response: requests.Response = requests.post(
            self.BASE_URL.format(
                PROJECT_ID=self.project_id,
                REGION=self.region,
                EMBED_ENDPOINT_ID=self.endpoint,
            ),
            json=payload,
            headers=headers,
        )

        if response.status_code != 200:
            raise Exception(f"Error {response.status_code}: {response.text}")

        return response.json()
