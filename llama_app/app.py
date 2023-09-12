import logging
import os

from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from starlette.responses import RedirectResponse

from llama_app.embeddings import Content, EmbeddingsService, EmbedRequest
from llama_app.llm import (GCPLlamaService, LlamaRequest, MockLLMService,
                           Prompt, VertexLLMConfig)
from llama_app.settings import SETTINGS

logger = logging.getLogger(__name__)

app = FastAPI()

app.mount("/static", StaticFiles(directory="./llama_app/static"), name="static")

PROJECT_ID = os.environ.get("PROJECT_ID")
ENDPOINT_ID = os.environ.get("ENDPOINT_ID")
REGION = os.environ.get("REGION")

if not (PROJECT_ID and ENDPOINT_ID and REGION):
    raise Exception(
        "PROJECT_ID, ENDPOINT_ID, and REGION must be set as environment variables"
    )


if os.getenv("LLM_TYPE") == "mock":
    llm = MockLLMService()
else:
    config = VertexLLMConfig(
        project_id=PROJECT_ID, endpoint_id=ENDPOINT_ID, region=REGION
    )
    llm = GCPLlamaService(config)


gecko = EmbeddingsService(SETTINGS.embeddings)


def _configure_db(component: FastAPI) -> None:
    pass


_configure_db(app)


# TODO: Move these endpoint out of app.py file
@app.post("/predict")
async def predict(prompt: Prompt):
    request = LlamaRequest(instances=[prompt])
    try:
        response = llm.predict(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return response


@app.get("/liveness")
def liveness():
    return True


@app.post("/embeddings")
async def embeddngs(content: Content):
    payload = EmbedRequest(instances=[content])
    try:
        response = gecko.predict(payload)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return response


# at root redirect to /static/index.html
@app.get("/")
def index():
    return RedirectResponse(url="/static/index.html")
