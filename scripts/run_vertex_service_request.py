import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
import requests
from llama_app.utilities import get_gcp_token


# https://cloud.google.com/vertex-ai/docs/reference/rest/v1/projects.locations.endpoints/predict
# https://www.pinecone.io/learn/llama-2/

token = get_gcp_token()
ENDPOINT_ID = 119840170357817344
PROJECT_ID = "production-397416"
REGION = "us-central1"
URL = f"https://{REGION}-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/us-central1/endpoints/{ENDPOINT_ID}:predict"

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json",
}

prompt = """
<s>[INST] <<SYS>>
You are a helpful, respectful and honest assistant. Always answer as helpfully as possible, while being safe.  
Your answers should not include any harmful, unethical, racist, sexist, toxic, dangerous, or illegal content. 
Please ensure that your responses are socially unbiased and positive in nature.

If a question does not make any sense, or is not factually coherent, 
explain why instead of answering something not correct. If you don't know the answer to a question, 
please don't share false information.
<</SYS>>

Write a 100-word article on 'Benefits of Open-Source in AI research'[/INST]"""


prompt = {
    "instances": [
        {"prompt": prompt},
    ]
}

response = requests.post(url=URL, headers=headers, json=prompt)
print(response.status_code)
print(response.text)
