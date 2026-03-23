from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def _default_database_url() -> str:
    repo_root = Path(__file__).resolve().parents[5]
    return f"sqlite+aiosqlite:///{repo_root / 'neural_house.db'}"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="NEURAL_HOUSE_API_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    service_name: str = "Neural House API"
    service_version: str = "0.1.0"
    api_prefix: str = "/api"
    database_url: str = Field(default_factory=_default_database_url)
    redis_url: str = "redis://localhost:6379/0"
    simulation_seed: int = 7
    audition_default_minutes: int = 5
    audition_max_minutes: int = 8
    audition_llm_timeout_seconds: float = 8.0
    cors_origins: list[str] = Field(default_factory=list)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
