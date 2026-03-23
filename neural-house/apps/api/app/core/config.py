from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Neural House API"
    api_prefix: str = "/api"
    api_host: str = Field(default="0.0.0.0", alias="API_HOST")
    api_port: int = Field(default=8000, alias="API_PORT")
    database_url: str = Field(
        default="postgresql+psycopg://neural_house:neural_house@localhost:5432/neural_house",
        alias="DATABASE_URL",
    )
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")
    cors_origins: list[str] | str = Field(
        default=["http://localhost:3000", "http://127.0.0.1:3000"],
        alias="CORS_ORIGINS",
    )
    vip_debug_bypass: bool = Field(default=True, alias="VIP_DEBUG_BYPASS")


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    if isinstance(settings.cors_origins, str):
        settings.cors_origins = [origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()]
    return settings


settings = get_settings()
