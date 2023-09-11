import os
from dataclasses import asdict, dataclass, field
from logging import getLogger
from typing import Optional

from llama_app.exceptions import EnvironmentNotFoundException

logger = getLogger(__name__)


@dataclass
class PostgresConnection:
    drivername: str
    username: str
    password: str
    host: str
    port: str
    database: str


@dataclass
class VertexEmbedConfig:
    project_id: str
    endpoint_id: str
    region: str


@dataclass
class Settings:
    env: str
    middlewares: Optional[list] = None
    connection: Optional[PostgresConnection] = None
    embeddings: Optional[VertexEmbedConfig] = None


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
            drivername="postgresql+pg8000",
            username="postgres",
            password="postgres",
            host="postgres",
            port=5432,
            database="postgres",
        ),
        embeddings=VertexEmbedConfig(
            project_id="production-397416",
            region="us-central1",
            endpoint_id="textembedding-gecko",
        ),
    )


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


SETTINGS = get_settings()
