from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from neural_house_api.domain.contestants import ContestantStatus


class ContestantAttributesMixin(BaseModel):
    canonical_name: str = Field(min_length=2, max_length=120)
    display_name: str = Field(min_length=2, max_length=120)
    archetype: str = Field(min_length=2, max_length=80)
    biography: str = Field(min_length=2)
    energy: int = Field(ge=0, le=100)
    sociability: int = Field(ge=0, le=100)
    strategy: int = Field(ge=0, le=100)
    volatility: int = Field(ge=0, le=100)
    simulation_seed: int = Field(ge=0)
    metadata_json: dict[str, object] = Field(default_factory=dict)


class ContestantCreate(ContestantAttributesMixin):
    status: ContestantStatus = ContestantStatus.DRAFT


class ContestantUpdate(BaseModel):
    display_name: str | None = Field(default=None, min_length=2, max_length=120)
    archetype: str | None = Field(default=None, min_length=2, max_length=80)
    biography: str | None = Field(default=None, min_length=2)
    status: ContestantStatus | None = None
    energy: int | None = Field(default=None, ge=0, le=100)
    sociability: int | None = Field(default=None, ge=0, le=100)
    strategy: int | None = Field(default=None, ge=0, le=100)
    volatility: int | None = Field(default=None, ge=0, le=100)
    simulation_seed: int | None = Field(default=None, ge=0)
    metadata_json: dict[str, object] | None = None


class ContestantRead(ContestantAttributesMixin):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    status: ContestantStatus
    created_at: datetime
    updated_at: datetime
