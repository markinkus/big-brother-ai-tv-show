from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class PersonaCardGenerateRequest(BaseModel):
    requested_count: int = Field(default=3, ge=1, le=6)
    generator_mode: str = "safe_casting"
    dominant_archetypes: list[str] = Field(default_factory=list)


class PersonaCardRead(ORMModel):
    id: int
    season_id: int
    label: str
    status: str
    base_seed: int
    dominant_archetype: str
    synopsis: str
    public_pitch: str
    private_complexity_summary: str
    trustability_score: float
    manipulation_susceptibility: float
    generation_notes_json: dict
    created_at: datetime


class CreateContestantFromCardRequest(BaseModel):
    display_name_override: str | None = None
    speech_style_override: str | None = None

