from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class WorkerSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="NEURAL_HOUSE_WORKER_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    database_url: str = (
        "postgresql+asyncpg://postgres:postgres@localhost:5432/neural_house"
    )
    redis_url: str = "redis://localhost:6379/0"
    simulation_seed: int = 7
    simulation_tick_seconds: int = 10
    stream_name: str = "house:simulation:events"


@lru_cache(maxsize=1)
def get_settings() -> WorkerSettings:
    return WorkerSettings()
