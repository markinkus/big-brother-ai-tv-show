#!/usr/bin/env python3
from __future__ import annotations

import os
import socket
import time
from urllib.parse import urlparse


def _check_tcp(url: str) -> str:
    parsed = urlparse(url)
    host = parsed.hostname
    port = parsed.port
    if not host or not port:
        return "unknown"
    try:
        with socket.create_connection((host, port), timeout=1):
            return "up"
    except OSError:
        return "down"


def main() -> None:
    worker_name = os.environ.get("WORKER_NAME", "worker")
    database_url = os.environ.get("DATABASE_URL", "")
    redis_url = os.environ.get("REDIS_URL", "")

    print(f"{worker_name} started", flush=True)
    while True:
        db_state = _check_tcp(database_url) if database_url else "missing"
        redis_state = _check_tcp(redis_url) if redis_url else "missing"
        print(f"{worker_name} heartbeat db={db_state} redis={redis_state}", flush=True)
        time.sleep(15)


if __name__ == "__main__":
    main()

