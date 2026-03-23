from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from app.schemas.common import ORMModel
from app.schemas.season import RoomRead


class VipRoomSummaryRead(BaseModel):
    room_code: str
    room_name: str
    occupant_names: list[str]
    activity_summary: str
    tension: float


class VipStateRead(BaseModel):
    season_id: int
    tick_number: int
    selected_room_code: str | None
    tension: float
    active_alliances: list[str]
    active_conflicts: list[str]
    recent_events: list[str]
    recent_highlights: list[str]
    last_change_digest: list[str]
    room_summaries: list[VipRoomSummaryRead]
    visibility_policy: str
    rooms: list[RoomRead]


class VipSessionStartRequest(BaseModel):
    premium_user_id: int
    selected_room_code: str | None = None


class VipSessionRead(ORMModel):
    id: int
    premium_user_id: int
    season_id: int
    started_at: datetime
    ended_at: datetime | None
    selected_room_code: str | None
    session_meta_json: dict
