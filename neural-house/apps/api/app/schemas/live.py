from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class LiveSegmentRead(BaseModel):
    slot: str
    headline: str
    summary: str
    tone: str
    target_names: list[str]


class AudiencePulseRead(BaseModel):
    cluster: str
    leaning: str
    mood: str
    intensity: float


class WeeklyLiveRead(BaseModel):
    season_id: int
    tick_number: int
    generated_at: datetime
    presenter_intro: str
    commentator_panels: list[str]
    segments: list[LiveSegmentRead]
    audience_pulse: list[AudiencePulseRead]
    scoreboard: list[str]
