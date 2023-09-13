from dataclasses import dataclass, field, asdict
from fastapi import APIRouter, HTTPException
import psycopg2


from llama_app.clients.embeddings import EmbedContent, EmbedRequest, gecko
from llama_app.clients.llm import (
    GCPLlamaService,
    LlamaRequest,
    MockLLMService,
    Prompt,
    VertexLLMConfig,
)

import os
from llama_app.clients.search import EmbeddingsSearchEngine
from llama_app.models.search import SearchRequest, SearchResponse

from llama_app.settings import SETTINGS


@dataclass
class Endpoint:
    prefix: str
    router: APIRouter = field(default_factory=APIRouter)


endpoint = Endpoint(prefix="/api")

# TODO: Move these to the settings; add MOCK as an environment
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


@endpoint.router.get("/liveness")
def liveness():
    return True


# TODO: Move these endpoint out of app.py file
@endpoint.router.post("/predict")
async def predict(prompt: Prompt):
    request = LlamaRequest(instances=[prompt])
    try:
        response = llm.predict(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return response


@endpoint.router.post("/search")
async def search(query: SearchRequest):
    embeddings_search_engine = EmbeddingsSearchEngine(SETTINGS.connection, gecko)
    documents = embeddings_search_engine.find_similar_by_text(query.text)
    return SearchResponse(documents=documents)


# TODO: We should split model and embeddings into sub-routes and both should have predict end-point
@endpoint.router.post("/embeddings")
async def embeddngs(content: EmbedContent):
    payload = EmbedRequest(instances=[content])
    try:
        response = gecko.predict(payload)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return response
