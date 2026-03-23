from __future__ import annotations

import uuid
from dataclasses import dataclass

from sqlalchemy import Integer, String, Text, select
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class ContestantRecord(Base):
    __tablename__ = "contestants"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    canonical_name: Mapped[str] = mapped_column(String(120))
    display_name: Mapped[str] = mapped_column(String(120))
    archetype: Mapped[str] = mapped_column(String(80))
    status: Mapped[str] = mapped_column(
        ENUM("draft", "active", "evicted", "winner", name="contestant_status", create_type=False)
    )
    energy: Mapped[int] = mapped_column(Integer)
    sociability: Mapped[int] = mapped_column(Integer)
    strategy: Mapped[int] = mapped_column(Integer)
    volatility: Mapped[int] = mapped_column(Integer)
    biography: Mapped[str] = mapped_column(Text)
    simulation_seed: Mapped[int] = mapped_column(Integer)


contestant_projection = select(
    ContestantRecord.id,
    ContestantRecord.display_name,
    ContestantRecord.energy,
    ContestantRecord.sociability,
    ContestantRecord.strategy,
    ContestantRecord.volatility,
    ContestantRecord.simulation_seed,
).where(ContestantRecord.status == "active")


@dataclass(slots=True)
class ContestantState:
    contestant_id: str
    display_name: str
    tension_score: int
    alliance_score: int
