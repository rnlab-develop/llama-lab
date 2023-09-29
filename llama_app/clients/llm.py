from dataclasses import dataclass
from typing import List

import requests
from pydantic import BaseModel

import llama_app.settings as settings
from llama_app.utilities import get_gcp_token


class Prompt(BaseModel):
    prompt: str
    top_k : int
    max_length: int


class VertexRequest(BaseModel):
    instances: List[Prompt]


def get_llm_from_settings(settings: settings.Settings):
    llm_config = settings.llm
    if llm_config.llm_type == settings.LLMType.MOCK:
        return MockLLMService()
    elif llm_config.llm_type == settings.LLMType.LLAMA_VERTEX:
        return GCPLlamaService(
            llm_config.config.project_id,
            llm_config.config.region,
            llm_config.config.endpoint_id,
        )


@dataclass
class VertexLLMConfig:
    project_id: str
    endpoint_id: str
    region: str


class BaseLLMService:
    def predict(self, prompt: VertexRequest):
        raise NotImplementedError()


class GCPLlamaService(BaseLLMService):
    def __init__(self, project_id, region, endpoint_id):
        self.project_id = project_id
        self.endpoint_id = endpoint_id
        self.region = region
        self.endpoint = f"https://us-central1-aiplatform.googleapis.com/v1/projects/{self.project_id}/locations/{self.region}/endpoints/{self.endpoint_id}:predict"

    def predict(self, prompt: VertexRequest):
        try:
            token = get_gcp_token()

            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            }
            # x = {"instances": [{"prompt": "hello"}]}
            print(self.endpoint)
            response = requests.post(
                self.endpoint, headers=headers, json=prompt.model_dump()
            )
            print(response)
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"Error: {response.status_code}, {response.text}")
        except Exception as e:
            raise Exception(str(e))


class MockLLMService(BaseLLMService):
    def predict(self, input_data):
        # Simulate a successful API response
        return {
            "predictions": [
                [
                    {
                        "generated_text": "What are marge simpson's husband's name?\n\nAnswer: Marge Simpson's husband is Homer Simpson."
                    }
                ]
            ],
            "deployedModelId": "5090134105207603200",
            "model": "projects/108524135261/locations/us-central1/models/llama2-7b-chat-001",
            "modelDisplayName": "llama2-7b-chat-001",
            "modelVersionId": "1",
        }
