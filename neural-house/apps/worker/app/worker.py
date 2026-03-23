from __future__ import annotations

import os

from redis import Redis
from rq import Worker


def main() -> None:
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    redis = Redis.from_url(redis_url)
    worker = Worker(["simulation", "newsroom", "persona", "vip"], connection=redis)
    worker.work()


if __name__ == "__main__":
    main()
