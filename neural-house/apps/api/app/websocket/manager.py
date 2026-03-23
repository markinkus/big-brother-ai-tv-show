from __future__ import annotations

from collections import defaultdict

from fastapi import WebSocket


class SeasonWebSocketManager:
    def __init__(self) -> None:
        self._connections: dict[int, list[WebSocket]] = defaultdict(list)

    async def connect(self, season_id: int, websocket: WebSocket) -> None:
        await websocket.accept()
        self._connections[season_id].append(websocket)

    def disconnect(self, season_id: int, websocket: WebSocket) -> None:
        if websocket in self._connections[season_id]:
            self._connections[season_id].remove(websocket)

    async def broadcast(self, season_id: int, message: dict) -> None:
        stale: list[WebSocket] = []
        for websocket in self._connections[season_id]:
            try:
                await websocket.send_json(message)
            except RuntimeError:
                stale.append(websocket)
        for websocket in stale:
            self.disconnect(season_id, websocket)


manager = SeasonWebSocketManager()

