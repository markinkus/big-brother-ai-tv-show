from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from app.schemas.common import ORMModel


class SeasonCreate(BaseModel):
    name: str
    seed: int = 1337


class SeasonRead(ORMModel):
    id: int
    name: str
    status: str
    seed: int
    created_at: datetime
    updated_at: datetime


class RoomRead(ORMModel):
    id: int
    season_id: int
    code: str
    name: str
    x: int
    y: int
    width: int
    height: int


class SimulationEventRead(ORMModel):
    id: int
    season_id: int
    tick_number: int
    event_type: str
    room_id: int | None = None
    summary: str
    payload_json: dict
    tension_score: float
    created_at: datetime


class SimulationStateRead(BaseModel):
    season_id: int
    tick_number: int
    status: str
    active_room_code: str | None
    recent_event_ids: list[int]
    active_contestant_ids: list[int]
    current_tension: float
    director_mode: str | None
    highlight_ids: list[int]
    confessional_ids: list[int]


class RelationshipRead(BaseModel):
    id: int
    season_id: int
    source_contestant_id: int
    target_contestant_id: int
    source_name: str
    target_name: str
    trust: float
    attraction: float
    rivalry: float
    fear: float
    respect: float
    manipulation: float
    familiarity: float
    last_significant_change_at: datetime
