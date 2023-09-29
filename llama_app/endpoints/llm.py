from dataclasses import asdict, dataclass, field

from fastapi import APIRouter, Depends, HTTPException
import psycopg2
from psycopg2 import sql
from contextlib import closing
from datetime import datetime
import json

from llama_app.clients.embeddings import EmbedContent, EmbedRequest, gecko
from llama_app.clients.llm import (
    BaseLLMService,
    GCPLlamaService,
    MockLLMService,
    Prompt,
    VertexRequest,
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
    request = VertexRequest(instances=[prompt])

    try:
        response = llm.predict(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # message = [
    #     {"role": "user", "content": prompt.model_dump()},
    #     {"role": "assistant", "content": "it's going to be 4"},
    # ]

    # with closing(psycopg2.connect(**asdict(SETTINGS.connection))) as conn:
    #     with closing(conn.cursor()) as cursor:
    #         query = sql.SQL(
    #             """
    #                 INSERT INTO tbl_chat_history (user_id, room_id, timestamp, message)
    #                 VALUES (%s, %s, %s, %s)
    #                 RETURNING id;
    #             """
    #         )
    #         cursor.execute(query, (1, 1, datetime.now(), json.dumps(message)))
    #         conn.commit()

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
