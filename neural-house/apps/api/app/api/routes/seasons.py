from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.entities import Confessional, Contestant, Highlight, Room, Season, SimulationEvent
from app.schemas.season import RelationshipRead, RoomRead, SeasonCreate, SeasonRead, SimulationEventRead, SimulationStateRead
from app.schemas.simulation_core import ConfessionalRead, ContestantStateRead, HighlightRead, MemoryRead, ObjectiveRead
from app.services.confessionals import list_confessionals
from app.services.highlights import list_highlights
from app.services.memory import list_memories
from app.services.relationships import list_relationships
from app.services.simulation_state import list_contestant_states, list_objectives
from app.services.simulation import run_simulation_ticks, set_simulation_status
from app.websocket.manager import manager

router = APIRouter(prefix="/api", tags=["seasons"])


@router.get("/seasons", response_model=list[SeasonRead])
def list_seasons(db: Session = Depends(get_db)) -> list[Season]:
    return list(db.scalars(select(Season).order_by(Season.id)))


@router.post("/seasons", response_model=SeasonRead)
def create_season(payload: SeasonCreate, db: Session = Depends(get_db)) -> Season:
    season = Season(name=payload.name, status="draft", seed=payload.seed)
    db.add(season)
    db.commit()
    db.refresh(season)
    return season


@router.get("/seasons/{season_id}", response_model=SeasonRead)
def get_season(season_id: int, db: Session = Depends(get_db)) -> Season:
    season = db.get(Season, season_id)
    if season is None:
        raise HTTPException(status_code=404, detail="Season not found")
    return season


@router.get("/seasons/{season_id}/rooms", response_model=list[RoomRead])
def get_rooms(season_id: int, db: Session = Depends(get_db)) -> list[Room]:
    return list(db.scalars(select(Room).where(Room.season_id == season_id).order_by(Room.id)))


@router.get("/seasons/{season_id}/events", response_model=list[SimulationEventRead])
def get_events(season_id: int, db: Session = Depends(get_db)) -> list[SimulationEvent]:
    return list(db.scalars(select(SimulationEvent).where(SimulationEvent.season_id == season_id).order_by(SimulationEvent.tick_number.desc())))


@router.get("/seasons/{season_id}/relationships", response_model=list[RelationshipRead])
def get_relationships(season_id: int, db: Session = Depends(get_db)) -> list[RelationshipRead]:
    season = db.get(Season, season_id)
    if season is None:
        raise HTTPException(status_code=404, detail="Season not found")
    return list_relationships(db, season_id)


@router.get("/seasons/{season_id}/simulation/state", response_model=SimulationStateRead)
def get_simulation_state(season_id: int, db: Session = Depends(get_db)) -> SimulationStateRead:
    season = db.get(Season, season_id)
    if season is None:
        raise HTTPException(status_code=404, detail="Season not found")
    latest_event = db.scalar(
        select(SimulationEvent).where(SimulationEvent.season_id == season_id).order_by(SimulationEvent.tick_number.desc()).limit(1)
    )
    event_ids = list(
        db.scalars(select(SimulationEvent.id).where(SimulationEvent.season_id == season_id).order_by(SimulationEvent.tick_number.desc()).limit(5))
    )
    active_room_code = None
    if latest_event and latest_event.room_id:
        active_room_code = db.scalar(select(Room.code).where(Room.id == latest_event.room_id))
    highlight_ids = list(
        db.scalars(select(Highlight.id).where(Highlight.season_id == season_id).order_by(Highlight.created_at.desc()).limit(5))
    )
    confessional_ids = list(
        db.scalars(
            select(Confessional.id)
            .join(Contestant, Contestant.id == Confessional.contestant_id)
            .where(Contestant.season_id == season_id)
            .order_by(Confessional.created_at.desc())
            .limit(5)
        )
    )
    active_contestant_ids = latest_event.payload_json.get("actor_ids", []) if latest_event else []
    director_mode = latest_event.payload_json.get("director_mode") if latest_event else None
    recent_tension = list(
        db.scalars(select(SimulationEvent.tension_score).where(SimulationEvent.season_id == season_id).order_by(SimulationEvent.tick_number.desc()).limit(5))
    )
    current_tension = round(sum(recent_tension) / max(len(recent_tension), 1), 3)

    return SimulationStateRead(
        season_id=season_id,
        tick_number=latest_event.tick_number if latest_event else 0,
        status=season.status,
        active_room_code=active_room_code,
        recent_event_ids=event_ids,
        active_contestant_ids=active_contestant_ids,
        current_tension=current_tension,
        director_mode=director_mode,
        highlight_ids=highlight_ids,
        confessional_ids=confessional_ids,
    )


@router.get("/seasons/{season_id}/contestant-states", response_model=list[ContestantStateRead])
def get_contestant_states(season_id: int, db: Session = Depends(get_db)) -> list[ContestantStateRead]:
    season = db.get(Season, season_id)
    if season is None:
        raise HTTPException(status_code=404, detail="Season not found")
    return list_contestant_states(db, season_id)


@router.get("/seasons/{season_id}/objectives", response_model=list[ObjectiveRead])
def get_objectives(season_id: int, db: Session = Depends(get_db)) -> list[ObjectiveRead]:
    season = db.get(Season, season_id)
    if season is None:
        raise HTTPException(status_code=404, detail="Season not found")
    return list_objectives(db, season_id, active_only=False)


@router.get("/seasons/{season_id}/memories", response_model=list[MemoryRead])
def get_memories(season_id: int, db: Session = Depends(get_db)) -> list[MemoryRead]:
    season = db.get(Season, season_id)
    if season is None:
        raise HTTPException(status_code=404, detail="Season not found")
    return list_memories(db, season_id)


@router.get("/seasons/{season_id}/highlights", response_model=list[HighlightRead])
def get_highlights(season_id: int, db: Session = Depends(get_db)) -> list[HighlightRead]:
    season = db.get(Season, season_id)
    if season is None:
        raise HTTPException(status_code=404, detail="Season not found")
    return list_highlights(db, season_id)


@router.get("/seasons/{season_id}/confessionals", response_model=list[ConfessionalRead])
def get_confessionals(season_id: int, db: Session = Depends(get_db)) -> list[ConfessionalRead]:
    season = db.get(Season, season_id)
    if season is None:
        raise HTTPException(status_code=404, detail="Season not found")
    return list_confessionals(db, season_id)


@router.post("/seasons/{season_id}/simulation/start", response_model=SimulationStateRead)
async def start_simulation(season_id: int, db: Session = Depends(get_db)) -> SimulationStateRead:
    season = set_simulation_status(db, season_id, "running")
    await manager.broadcast(
        season_id,
        {
            "type": "simulation.started",
            "season_id": season_id,
            "tick_number": None,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "payload": {"status": season.status},
        },
    )
    return get_simulation_state(season_id, db)


@router.post("/seasons/{season_id}/simulation/pause", response_model=SimulationStateRead)
async def pause_simulation(season_id: int, db: Session = Depends(get_db)) -> SimulationStateRead:
    season = set_simulation_status(db, season_id, "paused")
    await manager.broadcast(
        season_id,
        {
            "type": "simulation.paused",
            "season_id": season_id,
            "tick_number": None,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "payload": {"status": season.status},
        },
    )
    return get_simulation_state(season_id, db)


@router.post("/seasons/{season_id}/simulation/resume", response_model=SimulationStateRead)
async def resume_simulation(season_id: int, db: Session = Depends(get_db)) -> SimulationStateRead:
    season = set_simulation_status(db, season_id, "running")
    await manager.broadcast(
        season_id,
        {
            "type": "simulation.resumed",
            "season_id": season_id,
            "tick_number": None,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "payload": {"status": season.status},
        },
    )
    return get_simulation_state(season_id, db)


@router.post("/seasons/{season_id}/simulation/tick", response_model=SimulationEventRead)
async def tick_simulation(season_id: int, db: Session = Depends(get_db)) -> SimulationEventRead:
    try:
        event = run_simulation_ticks(db, season_id, 1)[0]
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    await manager.broadcast(
        season_id,
        {
            "type": "simulation.tick_completed",
            "season_id": season_id,
            "tick_number": event.tick_number,
            "timestamp": event.created_at.isoformat(),
            "payload": {"event_id": event.id, "event_type": event.event_type},
        },
    )
    return event


@router.post("/seasons/{season_id}/simulation/ticks/{count}", response_model=list[SimulationEventRead])
async def tick_simulation_many(season_id: int, count: int, db: Session = Depends(get_db)) -> list[SimulationEventRead]:
    try:
        events = run_simulation_ticks(db, season_id, max(1, min(count, 24)))
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    for event in events:
        await manager.broadcast(
            season_id,
            {
                "type": "simulation.tick_completed",
                "season_id": season_id,
                "tick_number": event.tick_number,
                "timestamp": event.created_at.isoformat(),
                "payload": {"event_id": event.id, "event_type": event.event_type},
            },
        )
    return events
