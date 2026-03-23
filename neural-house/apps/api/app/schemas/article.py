from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from app.schemas.common import ORMModel


class JournalistRead(ORMModel):
    id: int
    season_id: int
    display_name: str
    style: str
    ideology: str
    sensationalism: float
    empathy: float
    bias_profile_json: dict
    activity_interval_ticks: int
    active: bool


class ArticleRead(ORMModel):
    id: int
    season_id: int
    journalist_id: int
    title: str
    dek: str
    body: str
    tone: str
    stance: str
    referenced_event_ids_json: list[int]
    referenced_contestant_ids_json: list[int]
    published_at: datetime
    visibility_scope: str


class RunNewsroomCycleResponse(BaseModel):
    published_article_ids: list[int]

