from __future__ import annotations

import asyncio
import json

from neural_house_worker.config import get_settings
from neural_house_worker.db import SessionFactory, engine
from neural_house_worker.redis_bus import close_redis, get_redis
from neural_house_worker.simulation import build_engine


async def run_forever() -> None:
    settings = get_settings()
    simulation = build_engine()
    redis = await get_redis()

    try:
        while True:
            async with SessionFactory() as session:
                payload = await simulation.run_tick(session)
            await redis.publish(settings.stream_name, json.dumps(payload))
            await asyncio.sleep(settings.simulation_tick_seconds)
    finally:
        await close_redis()
        await engine.dispose()


def main() -> None:
    asyncio.run(run_forever())


if __name__ == "__main__":
    main()
