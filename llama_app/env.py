import os
from pathlib import Path

CREDENTIALS_ENV_VAR = "GOOGLE_APPLICATION_CREDENTIALS_JSON"


def is_local_docker_env():
    is_local = os.environ.get("ENV").lower() == "docker"
    return is_local


def write_credentials():
    path = Path("~/.config/gcloud/application_default_credentials.json").expanduser()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.touch()
    with path.open("w") as file:
        file.write(os.environ.get(CREDENTIALS_ENV_VAR))


def configure_for_local_docker():
    if is_local_docker_env():
        write_credentials()
