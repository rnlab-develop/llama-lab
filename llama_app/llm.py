import os
import requests
from pydantic import BaseModel
from dataclasses import dataclass
import google.auth
import google.auth.transport.requests
import google.oauth2
from typing import List

class Prompt(BaseModel):
    prompt: str

class LlamaRequest(BaseModel):
    instances: List[Prompt]

@dataclass
class VertexLLMConfig:
    project_id: str
    endpoint_id: str
    region: str

def get_gcp_token() -> str:
    try:
        creds = google.auth.default()[0]
    except Exception as e:
        raise Exception("error getting credentials")
    if not creds.token:
        try:
            creds.refresh(google.auth.transport.requests.Request())
        except Exception as e:
            raise e

    return creds.token

class GCPLlamaService:
    
    def __init__(self, vertex_config: VertexLLMConfig):
        self.project_id = vertex_config.project_id
        self.endpoint_id = vertex_config.endpoint_id
        self.region = vertex_config.region
        self.endpoint = f"https://us-central1-aiplatform.googleapis.com/v1/projects/{self.project_id}/locations/{self.region}/endpoints/{self.endpoint_id}:predict"

    def predict(self, prompt: LlamaRequest):
        try:
            token = get_gcp_token()

            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            x = {
                "instances": [{"prompt": "hello"}]
            }
            response = requests.post(self.endpoint, headers=headers, json=prompt.model_dump())
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"Error: {response.status_code}, {response.text}")
        except Exception as e:
            raise Exception(str(e))
        

class MockLLMService:

    def predict(self, input_data):
        # Simulate a successful API response
        return {
            'predictions': [
                [{'generated_text': "What are marge simpson's husband's name?\n\nAnswer: Marge Simpson's husband is Homer Simpson."}]
            ], 
            'deployedModelId': '5090134105207603200', 
            'model': 'projects/108524135261/locations/us-central1/models/llama2-7b-chat-001', 
            'modelDisplayName': 'llama2-7b-chat-001', 
            'modelVersionId': '1'
        }
