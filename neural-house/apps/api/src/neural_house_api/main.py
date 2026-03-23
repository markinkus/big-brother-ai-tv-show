from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from neural_house_api.api.router import api_router, health_router_group
from neural_house_api.core.settings import get_settings
from neural_house_api.infrastructure.cache.redis import close_redis_pool, warm_redis_pool
from neural_house_api.infrastructure.db.session import ensure_database_schema, engine


@asynccontextmanager
async def lifespan(_: FastAPI):
    await ensure_database_schema()
    await warm_redis_pool()
    try:
        yield
    finally:
        await close_redis_pool()
        await engine.dispose()


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.service_name,
        version=settings.service_version,
        lifespan=lifespan,
    )
    app.include_router(health_router_group)
    app.include_router(api_router, prefix=settings.api_prefix)
    return app


app = create_app()
