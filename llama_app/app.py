from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import requests
import os

app = FastAPI()

app.mount("/static", StaticFiles(directory="./llama_app/static"), name="static")

PROJECT_ID = "108524135261"
ENDPOINT_ID = "8443336706668625920"
REGION = "us-central1"
INPUT_DATA_FILE = "scripts/input.json"

GCLOUD_ENDPOINT = f"https://us-central1-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/{REGION}/endpoints/{ENDPOINT_ID}:predict"

def get_gcloud_token():
    try:
        token = os.popen('gcloud auth print-access-token').read().strip()
        return token
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error fetching gcloud token")
    
class Prompt(BaseModel):
    prompt: str


@app.post("/predict")
async def predict(prompt: Prompt):
    try:
        token = get_gcloud_token()

        payload = {
            "instances": [
                {"prompt": prompt.prompt},
            ]
        }
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        response = requests.post(GCLOUD_ENDPOINT, json=payload, headers=headers)

        print(response)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(status_code=response.status_code, detail=response.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
