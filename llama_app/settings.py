import enum
import os
from dataclasses import dataclass, field
from logging import getLogger
from typing import Any, Optional

from llama_app.exceptions import EnvironmentNotFoundException

logger = getLogger(__name__)


@dataclass
class PostgresConnection:
    user: str
    password: str
    host: str
    port: str
    dbname: str


@dataclass
class VertexEmbedConfig:
    project_id: str
    endpoint_id: str
    region: str


@dataclass
class GCPLlamaEndpointConfig:
    project_id: str
    endpoint_id: str
    region: str


class LLMType(enum.Enum):
    MOCK: str = "mock"
    LLAMA_VERTEX: str = "vertex"


@dataclass
class LLMConfig:
    llm_type: LLMType
    config: Optional[Any] = None


@dataclass
class Settings:
    env: str
    middlewares: Optional[list] = None
    connection: Optional[PostgresConnection] = None
    embeddings: Optional[VertexEmbedConfig] = None
    llm: Optional[GCPLlamaEndpointConfig] = None


def ProductionSettings() -> Settings:
    return Settings(
        env="prod",
        middlewares=[],
    )


def DevelopmentSettings() -> Settings:
    return Settings(
        env="dev",
        middlewares=[],
    )


def DockerSettings() -> Settings:
    return Settings(
        env="docker",
        middlewares=[],
        connection=PostgresConnection(
            user="postgres",
            password="postgres",
            host="pgvector",
            port=5432,
            dbname="postgres",
        ),
        embeddings=VertexEmbedConfig(
            project_id=os.environ.get("PROJECT_ID", "production-397416"),
            region="us-central1",
            endpoint_id="textembedding-gecko@latest",
        ),
        llm=LLMConfig(
            llm_type=LLMType.LLAMA_VERTEX,
            config=GCPLlamaEndpointConfig(
                project_id=os.environ.get("PROJECT_ID", "production-397416"),
                region="us-central1",
                endpoint_id=os.environ.get("ENDPOINT_ID", "119840170357817344"),
            ),
        ),
    )


def MockSettings() -> Settings:
    settings = DockerSettings()
    settings.llm = LLMConfig(llm_type=LLMType.MOCK)


@dataclass
class Environments:
    prod: Settings = field(default_factory=ProductionSettings())
    dev: Settings = field(default_factory=DevelopmentSettings())
    docker: Settings = field(default_factory=DockerSettings())


def _get_environments() -> Environments:
    return Environments(
        prod=ProductionSettings(),
        dev=DevelopmentSettings(),
        docker=DockerSettings(),
    )


def get_settings(env: str = None) -> Settings:
    environments = _get_environments()
    if env:
        try:
            return getattr(environments, env)
        except AttributeError:
            raise EnvironmentNotFoundException("Requested environment does not exist.")
    try:
        e = os.environ["ENV"]
        return getattr(environments, e)
    except KeyError:
        logger.warning("[!] Environment is not defined, defaulting to docker")
        return DockerSettings()


class SettingsException(Exception):
    pass


SETTINGS = get_settings()
