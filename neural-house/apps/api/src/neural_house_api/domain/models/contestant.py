from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, Integer, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from neural_house_api.domain.contestants import ContestantStatus
from neural_house_api.infrastructure.db.base import Base


class Contestant(Base):
    __tablename__ = "contestants"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    canonical_name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    display_name: Mapped[str] = mapped_column(String(120), nullable=False)
    archetype: Mapped[str] = mapped_column(String(80), nullable=False)
    status: Mapped[ContestantStatus] = mapped_column(
        Enum(ContestantStatus, name="contestant_status"),
        nullable=False,
        default=ContestantStatus.DRAFT,
        index=True,
    )
    energy: Mapped[int] = mapped_column(Integer, nullable=False, default=50)
    sociability: Mapped[int] = mapped_column(Integer, nullable=False, default=50)
    strategy: Mapped[int] = mapped_column(Integer, nullable=False, default=50)
    volatility: Mapped[int] = mapped_column(Integer, nullable=False, default=50)
    biography: Mapped[str] = mapped_column(Text, nullable=False, default="")
    simulation_seed: Mapped[int] = mapped_column(Integer, nullable=False, default=7)
    metadata_json: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        onupdate=lambda: datetime.now(timezone.utc),
    )
