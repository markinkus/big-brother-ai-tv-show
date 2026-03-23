from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.schemas.vip import VipSessionRead, VipSessionStartRequest, VipStateRead
from app.services.vip import build_vip_state, end_vip_session, start_vip_session
from app.websocket.manager import manager

router = APIRouter(prefix="/api", tags=["vip"])


@router.get("/seasons/{season_id}/vip/state", response_model=VipStateRead)
def get_vip_state(
    season_id: int,
    premium_user_id: int | None = Query(default=None),
    selected_room_code: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    if premium_user_id is None and not settings.vip_debug_bypass:
        raise HTTPException(status_code=403, detail="Premium access required")
    return build_vip_state(db, season_id, selected_room_code)


@router.get("/seasons/{season_id}/vip/rooms/{room_code}", response_model=VipStateRead)
def get_vip_room(season_id: int, room_code: str, db: Session = Depends(get_db)):
    return build_vip_state(db, season_id, room_code)


@router.post("/seasons/{season_id}/vip/session/start", response_model=VipSessionRead)
async def begin_vip_session(season_id: int, payload: VipSessionStartRequest, db: Session = Depends(get_db)):
    try:
        vip_session = start_vip_session(db, season_id, payload.premium_user_id, payload.selected_room_code)
    except ValueError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    await manager.broadcast(
        season_id,
        {
            "type": "vip.snapshot.updated",
            "season_id": season_id,
            "tick_number": None,
            "timestamp": vip_session.started_at.isoformat(),
            "payload": {"vip_session_id": vip_session.id, "selected_room_code": vip_session.selected_room_code},
        },
    )
    return vip_session


@router.post("/seasons/{season_id}/vip/session/end", response_model=VipSessionRead)
def finish_vip_session(season_id: int, session_id: int = Query(...), db: Session = Depends(get_db)):
    try:
        return end_vip_session(db, session_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

