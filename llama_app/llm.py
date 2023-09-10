import os
import requests
from pydantic import BaseModel
from dataclasses import dataclass

class Prompt(BaseModel):
    prompt: str

@dataclass
class VertexConfig:
    project_id: str
    endpoint_id: str
    region: str

class GCPLlamaService:
    
    def __init__(self, vertex_config: VertexConfig):
        self.project_id = vertex_config.project_id
        self.endpoint_id = vertex_config.endpoint_id
        self.region = vertex_config.region
        self.endpoint = f"https://us-central1-aiplatform.googleapis.com/v1/projects/{self.project_id}/locations/{self.region}/endpoints/{self.endpoint_id}:predict"

    def get_gcloud_token(self):
        try:
            token = os.popen('gcloud auth print-access-token').read().strip()
            return token
        except Exception as e:
            raise Exception("Error fetching gcloud token")

    def predict(self, input_data):
        try:
            token = self.get_gcloud_token()
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            response = requests.post(self.GCLOUD_ENDPOINT, headers=headers, json=input_data)
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
