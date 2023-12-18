import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
import requests

from llama_app.utilities import get_gcp_token

# https://cloud.google.com/vertex-ai/docs/reference/rest/v1/projects.locations.endpoints/predict
# https://www.pinecone.io/learn/llama-2/


token = get_gcp_token()
ENDPOINT_ID = os.environ.get("ENDPOINT_ID", "4977429765314052096")
PROJECT_ID = os.environ.get("PROJECT_ID", "production-397416")
REGION = "us-central1"
URL = f"https://{REGION}-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/us-central1/endpoints/{ENDPOINT_ID}:predict"

LOCAL_URL = f"http://localhost:5000/api/predict"

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json",
}

prompt_text = """
<s> [INST] <<SYS>>
 You are a helpful ASSISTANT to USER and you pay close attention to everything 
                            that is said in a conversation before giving a response. You should answer as 
                            succinctly as possible, while being safe. There is no need to act conversational, 
                            you can just give a curt and correct response. 
<</SYS>>
Hi There! [/INST] Hi. How can I help? </s> 
<s>[INST]what is 2+2?[/INST]it's going to be 4 </s>
<s>[INST]multiply that by 3[/INST]the answer is 12 </s>
<s> [INST] can you now subtract 2? [/INST]
"""

prompt = {
    "instances": [
        {"prompt": prompt_text, "top_k": 40, "max_lengh": 600},
    ],
}

local_prompt = {
    "prompt": prompt_text
}

response = requests.post(url=LOCAL_URL, headers=headers, json=local_prompt)
print(response.status_code)
r = response.json()["predictions"][0][0]["generated_text"]

print(r.replace(prompt_text,""))
