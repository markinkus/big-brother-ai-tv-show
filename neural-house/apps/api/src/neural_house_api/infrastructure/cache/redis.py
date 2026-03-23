from __future__ import annotations

from redis.asyncio import Redis

from neural_house_api.core.settings import get_settings

_redis_client: Redis | None = None


async def warm_redis_pool() -> Redis:
    global _redis_client
    if _redis_client is None:
        settings = get_settings()
        _redis_client = Redis.from_url(settings.redis_url, decode_responses=True)
    return _redis_client


async def get_redis_client() -> Redis:
    client = await warm_redis_pool()
    return client


async def close_redis_pool() -> None:
    global _redis_client
    if _redis_client is not None:
        await _redis_client.aclose()
        _redis_client = None
