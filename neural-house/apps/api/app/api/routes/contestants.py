from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.contestants import create_contestant, get_contestant, list_contestants, update_contestant
from app.schemas.contestant import ContestantCreate, ContestantRead, ContestantUpdate
from app.websocket.manager import manager

router = APIRouter(prefix="/api", tags=["contestants"])


@router.get("/seasons/{season_id}/contestants", response_model=list[ContestantRead])
def get_season_contestants(season_id: int, db: Session = Depends(get_db)):
    return list_contestants(db, season_id)


@router.post("/seasons/{season_id}/contestants", response_model=ContestantRead)
async def create_season_contestant(season_id: int, payload: ContestantCreate, db: Session = Depends(get_db)):
    contestant = create_contestant(db, season_id, payload)
    await manager.broadcast(
        season_id,
        {
            "type": "contestant.state_changed",
            "season_id": season_id,
            "tick_number": None,
            "timestamp": contestant.created_at.isoformat(),
            "payload": {"contestant_id": contestant.id, "display_name": contestant.display_name},
        },
    )
    return contestant


@router.get("/contestants/{contestant_id}", response_model=ContestantRead)
def get_single_contestant(contestant_id: int, db: Session = Depends(get_db)):
    contestant = get_contestant(db, contestant_id)
    if contestant is None:
        raise HTTPException(status_code=404, detail="Contestant not found")
    return contestant


@router.patch("/contestants/{contestant_id}", response_model=ContestantRead)
async def patch_contestant(contestant_id: int, payload: ContestantUpdate, db: Session = Depends(get_db)):
    contestant = get_contestant(db, contestant_id)
    if contestant is None:
        raise HTTPException(status_code=404, detail="Contestant not found")
    contestant = update_contestant(db, contestant, payload)
    await manager.broadcast(
        contestant.season_id,
        {
            "type": "contestant.state_changed",
            "season_id": contestant.season_id,
            "tick_number": None,
            "timestamp": contestant.created_at.isoformat(),
            "payload": {"contestant_id": contestant.id, "display_name": contestant.display_name},
        },
    )
    return contestant

