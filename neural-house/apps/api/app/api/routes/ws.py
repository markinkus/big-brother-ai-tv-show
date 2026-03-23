from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.websocket.manager import manager

router = APIRouter(tags=["ws"])


@router.websocket("/ws/seasons/{season_id}")
async def season_events(websocket: WebSocket, season_id: int) -> None:
    await manager.connect(season_id, websocket)
    await websocket.send_json(
        {
            "type": "simulation.started",
            "season_id": season_id,
            "tick_number": 0,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "payload": {"message": "WebSocket channel connected"},
        }
    )
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_json(
                {
                    "type": "event.created",
                    "season_id": season_id,
                    "tick_number": None,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "payload": {"echo": data},
                }
            )
    except WebSocketDisconnect:
        manager.disconnect(season_id, websocket)

