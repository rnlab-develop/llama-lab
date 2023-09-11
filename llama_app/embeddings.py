from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union

import requests
from pydantic import BaseModel

from llama_app.enums import TaskType
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
        self.token: str = token or get_gcp_token()
        self.region: str = vertex_config.region
        self.endpoint: str = vertex_config.endpoint_id
        self.headers: Dict[str, str] = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

    def predict(
        self,
        content: str,
        title: Optional[str] = None,
        task_type: TaskType = TaskType.RETRIEVAL_DOCUMENT,
    ) -> Union[Dict[str, Any], Any]:
        """
        Makes a prediction to get embeddings for the provided text.
        """
        if not isinstance(task_type, TaskType):
            raise ValueError("Invalid task_type. Use values from TaskType Enum.")

        payload: Dict[str, Any] = {
            "instances": [
                {
                    "task_type": task_type.value,
                    "content": content,
                }
            ]
        }

        # Optional title
        if title:
            payload["instances"][0]["title"] = title

        response: requests.Response = requests.post(
            self.BASE_URL.format(
                PROJECT_ID=self.project_id,
                REGION=self.region,
                EMBED_ENDPOINT_ID=self.endpoint,
            ),
            json=payload,
            headers=self.headers,
        )

        if response.status_code != 200:
            raise Exception(f"Error {response.status_code}: {response.text}")

        return response.json()
