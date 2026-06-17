import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    github_token: str
    log_level: str = "INFO"


def load_settings() -> Settings:
    load_dotenv()

    token = os.getenv("GITHUB_TOKEN")
    if not token:
        msg = "GITHUB_TOKEN не задан. Скопируйте .env.example в .env и укажите токен."
        raise ValueError(msg)

    return Settings(
        github_token=token,
        log_level=os.getenv("LOG_LEVEL", "INFO"),
    )
