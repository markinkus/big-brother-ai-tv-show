from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class ContestantStateRead(BaseModel):
    contestant_id: int
    display_name: str
    room_id: int | None
    room_code: str | None
    room_name: str | None
    energy: float
    stress: float
    suspicion: float
    trust_baseline: float
    loneliness: float
    ambition: float
    confidence: float
    social_visibility: float
    current_focus: str
    status_effects_json: dict
    updated_at: datetime


class ObjectiveRead(BaseModel):
    id: int
    contestant_id: int
    contestant_name: str
    objective_type: str
    title: str
    description: str
    priority: float
    duration_ticks: int
    active: bool
    progress: float
    success_conditions_json: dict
    failure_conditions_json: dict
    reward_json: dict
    penalty_json: dict
    created_at: datetime
    updated_at: datetime


class MemoryRead(BaseModel):
    id: int
    contestant_id: int
    contestant_name: str
    memory_type: str
    summary: str
    salience: float
    emotional_valence: float
    strategic_value: float
    related_contestant_ids_json: list[int]
    related_event_id: int | None
    decay_rate: float
    created_at: datetime
    updated_at: datetime


class ConfessionalRead(BaseModel):
    id: int
    contestant_id: int
    contestant_name: str
    triggered_by_event_id: int | None
    public_transcript: str
    private_analysis: str
    shadow_flags_json: list[str]
    contradiction_flags_json: list[str]
    created_at: datetime


class HighlightRead(BaseModel):
    id: int
    season_id: int
    event_id: int
    category: str
    title: str
    summary: str
    score: float
    created_at: datetime
