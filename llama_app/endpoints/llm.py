from dataclasses import dataclass, field, asdict
from fastapi import APIRouter, HTTPException
import psycopg2


from llama_app.clients.embeddings import EmbedContent, EmbedRequest, gecko
from llama_app.clients.llm import (
    GCPLlamaService,
    VertexRequest,
    MockLLMService,
    Prompt,
    BaseLLMService
)

import os
from llama_app.clients.search import embeddings_search_engine
from llama_app.models.search import SearchRequest, SearchResponse

from llama_app.settings import SETTINGS, LLMType


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


def get_llm_from_settings():
    if SETTINGS.llm.llm_type == LLMType.MOCK:
        return MockLLMService()
    elif SETTINGS.llm.llm_type == LLMType.LLAMA_VERTEX:
        return GCPLlamaService(SETTINGS.llm.config)
    else:
        raise Exception("LLM type not supported")
    
def get_llm() -> BaseLLMService:
    return get_llm_from_settings()

@endpoint.router.get("/liveness")
def liveness():
    return True


# TODO: Move these endpoint out of app.py file
@endpoint.router.post("/predict")
async def predict(prompt: Prompt, llm: BaseLLMService = get_llm()):
    response = embeddings_search_engine.find_similar_by_text(prompt.prompt)
    documents = response.get("documents") or []

    # Logic to add system message:
    # goes here
    
    request = VertexRequest(instances=[prompt])
    try:
        response = llm.predict(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return response


@endpoint.router.post("/search")
async def search(query: SearchRequest):
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
