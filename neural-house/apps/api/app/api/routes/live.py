from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.entities import Season, SimulationEvent
from app.schemas.live import WeeklyLiveRead
from app.services.live_show import build_weekly_live
from app.websocket.manager import manager

router = APIRouter(prefix="/api", tags=["live"])


@router.get("/seasons/{season_id}/live/latest", response_model=WeeklyLiveRead)
def get_latest_live(season_id: int, db: Session = Depends(get_db)) -> WeeklyLiveRead:
    if db.get(Season, season_id) is None:
        raise HTTPException(status_code=404, detail="Season not found")
    try:
        return build_weekly_live(db, season_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/seasons/{season_id}/live/run-weekly-show", response_model=WeeklyLiveRead)
async def run_weekly_show(season_id: int, db: Session = Depends(get_db)) -> WeeklyLiveRead:
    season = db.get(Season, season_id)
    if season is None:
        raise HTTPException(status_code=404, detail="Season not found")
    live_pack = build_weekly_live(db, season_id)
    event = SimulationEvent(
        season_id=season_id,
        tick_number=live_pack.tick_number,
        event_type="weekly_live_run",
        room_id=None,
        summary="The weekly live pack reframed the current season state for the public show layer.",
        payload_json={"segments": [segment.headline for segment in live_pack.segments[:4]]},
        tension_score=0.45,
    )
    db.add(event)
    db.commit()
    await manager.broadcast(
        season_id,
        {
            "type": "live.started",
            "season_id": season_id,
            "tick_number": live_pack.tick_number,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "payload": {"segment_count": len(live_pack.segments)},
        },
    )
    return live_pack
