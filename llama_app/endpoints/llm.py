from dataclasses import asdict, dataclass, field

from fastapi import APIRouter, Depends, HTTPException, Request
import psycopg2
from psycopg2 import sql
from contextlib import closing
from datetime import datetime
import json
import itertools

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
from llama_app.templates.prompt import generate_prompt


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
    r = embeddings_search_engine.find_similar_by_text(prompt.prompt)

    # Get chat context
    context = []
    with closing(psycopg2.connect(**asdict(SETTINGS.connection))) as conn:
        with closing(conn.cursor()) as cursor:
            query = sql.SQL(
                """
                SELECT message
                FROM tbl_chat_history 
                WHERE user_id = 1 and room_id = 1
                ORDER BY timestamp DESC
                LIMIT 2;
                """
            )
            cursor.execute(query)
            results = cursor.fetchall()
            for row in results:
                context.append(row[0])

            # append system messages
            for s in [doc.body for doc in r]:
                context.append([{"role": "system", "content": s}])

    generated = generate_prompt(
        new_prompt=prompt.prompt,
        history=list(itertools.chain.from_iterable(reversed(context))),
    )
    # Validate payload
    request = VertexRequest(instances=[Prompt(prompt=generated)])

    try:
        response = llm.predict(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    prompt_text = prompt.model_dump()["prompt"]

    answer = response["predictions"][0][0]["generated_text"].replace(generated, "")

    message = [
        {"role": "user", "content": prompt_text},
        {"role": "assistant", "content": answer},
    ]

    print(f"Generated: {generated}")

    with closing(psycopg2.connect(**asdict(SETTINGS.connection))) as conn:
        with closing(conn.cursor()) as cursor:
            query = sql.SQL(
                """
                    INSERT INTO tbl_chat_history (user_id, room_id, timestamp, message)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id;
                """
            )
            cursor.execute(query, (1, 1, datetime.now(), json.dumps(message)))
            conn.commit()

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
