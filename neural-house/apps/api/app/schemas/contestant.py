from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from app.schemas.common import ORMModel


class ContestantCreate(BaseModel):
    display_name: str
    archetype: str
    skin_palette: str = "studio_blue"
    skin_accent: str = "gold"
    skin_silhouette: str = "host-ready"
    hair_style: str = "crown"
    public_bio: str
    public_goal: str
    hidden_goal_summary: str
    speech_style: str
    avatar_seed: int = 0
    persona_card_id: int | None = None


class ContestantUpdate(BaseModel):
    display_name: str | None = None
    archetype: str | None = None
    skin_palette: str | None = None
    skin_accent: str | None = None
    skin_silhouette: str | None = None
    hair_style: str | None = None
    public_bio: str | None = None
    public_goal: str | None = None
    hidden_goal_summary: str | None = None
    speech_style: str | None = None
    avatar_seed: int | None = None
    persona_card_id: int | None = None
    active: bool | None = None


class ContestantRead(ORMModel):
    id: int
    season_id: int
    display_name: str
    archetype: str
    avatar_seed: int
    skin_palette: str
    skin_accent: str
    skin_silhouette: str
    hair_style: str
    public_bio: str
    public_goal: str
    hidden_goal_summary: str
    speech_style: str
    persona_card_id: int | None
    active: bool
    created_at: datetime
