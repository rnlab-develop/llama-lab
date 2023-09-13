import logging
from pathlib import Path

import psycopg2
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.responses import RedirectResponse
from dataclasses import asdict

from llama_app.env import configure_for_local_docker
configure_for_local_docker()


from llama_app.populate.populate_db import run_insert_dataset
from llama_app.settings import SETTINGS
from llama_app.endpoints import llm

logger = logging.getLogger(__name__)

app = FastAPI()

app.mount("/static", StaticFiles(directory="./llama_app/static"), name="static")


COMPONENT_ENDPOINTS = [llm.endpoint]


def _configure_routers(component: FastAPI) -> None:
    for endpoint in COMPONENT_ENDPOINTS:
        component.include_router(endpoint.router, prefix=endpoint.prefix)
    return


def _configure_db(_: FastAPI) -> None:
    with psycopg2.connect(**asdict(SETTINGS.connection)) as conn:
        logger.info("[!] Validating database connection")
        cur = conn.cursor()
        cur.execute(("SELECT 1"))
        conn.commit()
        logger.warn(f"[+] DB Connection succeeded!")
        logger.warn(f"[!] Trying to populate database")
        status = run_insert_dataset(conn=conn)
        logger.warn(f"[+] {status}")
    return


_configure_routers(app)
_configure_db(app)


# at root redirect to /static/index.html
@app.get("/")
def index():
    return RedirectResponse(url="/static/index.html")
