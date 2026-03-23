from __future__ import annotations

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from neural_house_api.infrastructure.websocket.hub import websocket_hub

router = APIRouter()


@router.websocket("/ws/house")
async def house_event_stream(websocket: WebSocket) -> None:
    await websocket_hub.connect(websocket)
    try:
        await websocket.send_json(
            {
                "type": "simulation.stub",
                "message": "Realtime simulation events will flow here.",
            }
        )
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        await websocket_hub.disconnect(websocket)
