from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class ApiEnvelope(BaseModel):
    status: str = "ok"


class WebSocketEvent(BaseModel):
    type: str
    season_id: int
    tick_number: int | None = None
    timestamp: datetime
    payload: dict

