from __future__ import annotations

from fastapi import APIRouter
from sqlalchemy import text

from neural_house_api.infrastructure.cache.redis import get_redis_client
from neural_house_api.infrastructure.db.session import SessionFactory

router = APIRouter()


@router.get("/health")
async def healthcheck() -> dict[str, object]:
    db_ok = False
    redis_ok = False

    try:
        async with SessionFactory() as session:
            await session.execute(text("SELECT 1"))
            db_ok = True
    except Exception:
        db_ok = False

    try:
        redis = await get_redis_client()
        redis_ok = bool(await redis.ping())
    except Exception:
        redis_ok = False

    return {
        "status": "ok" if db_ok and redis_ok else "degraded",
        "dependencies": {
            "postgresql": db_ok,
            "redis": redis_ok,
        },
    }
