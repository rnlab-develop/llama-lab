from dataclasses import dataclass, field, asdict
from fastapi import APIRouter, HTTPException, Depends
from dataclasses import asdict


from llama_app.clients.embeddings import EmbedContent, EmbedRequest, gecko
from llama_app.clients.llm import (
    GCPLlamaService,
    VertexRequest,
    MockLLMService,
    Prompt,
    BaseLLMService,
)

from llama_app.clients.search import embeddings_search_engine
from llama_app.models.search import SearchRequest, SearchResponse

from llama_app.settings import SETTINGS, LLMType, SettingsException


@dataclass
class Endpoint:
    prefix: str
    router: APIRouter = field(default_factory=APIRouter)


endpoint = Endpoint(prefix="/api")


def get_llm_from_settings():
    if SETTINGS.llm.llm_type == LLMType.MOCK:
        return MockLLMService()
    elif SETTINGS.llm.llm_type == LLMType.LLAMA_VERTEX:
        vertex_config = SETTINGS.llm.config
        if not (
            vertex_config.project_id
            and vertex_config.region
            and vertex_config.endpoint_id
        ):
            raise SettingsException(
                "vertex config requires project_id, region and endpoint_id"
            )
        return GCPLlamaService(**asdict(SETTINGS.llm.config))
    else:
        raise SettingsException("LLM type not supported")


def get_llm() -> BaseLLMService:
    return get_llm_from_settings()


@endpoint.router.get("/liveness")
def liveness():
    return True


# TODO: Move these endpoint out of app.py file
@endpoint.router.post("/predict")
async def predict(prompt: Prompt, llm: BaseLLMService = Depends(get_llm)):
    response = embeddings_search_engine.find_similar_by_text(prompt.prompt)
    print("hello")
    print(response)
    documents = response

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
