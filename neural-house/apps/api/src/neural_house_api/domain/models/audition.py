from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from neural_house_api.domain.auditions import (
    AuditionExecutionMode,
    AuditionLlmMode,
    AuditionRunStatus,
)
from neural_house_api.infrastructure.db.base import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class AuditionAgentConfig(Base):
    __tablename__ = "audition_agent_configs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    provider: Mapped[str] = mapped_column(String(80), nullable=False, default="disabled")
    api_base_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    model_name: Mapped[str | None] = mapped_column(String(160), nullable=True)
    character_name: Mapped[str] = mapped_column(String(120), nullable=False)
    skin: Mapped[str] = mapped_column(String(80), nullable=False)
    palette: Mapped[str] = mapped_column(String(80), nullable=False)
    character_traits_json: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=_utcnow,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=_utcnow,
        server_default=func.now(),
        onupdate=_utcnow,
    )

    runs: Mapped[list["AuditionRun"]] = relationship(
        back_populates="agent_config",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class AuditionRun(Base):
    __tablename__ = "audition_runs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    agent_config_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("audition_agent_configs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status: Mapped[AuditionRunStatus] = mapped_column(
        Enum(AuditionRunStatus, name="audition_run_status"),
        nullable=False,
        default=AuditionRunStatus.QUEUED,
        index=True,
    )
    execution_mode: Mapped[AuditionExecutionMode] = mapped_column(
        Enum(AuditionExecutionMode, name="audition_execution_mode"),
        nullable=False,
        default=AuditionExecutionMode.INLINE,
    )
    llm_mode: Mapped[AuditionLlmMode] = mapped_column(
        Enum(AuditionLlmMode, name="audition_llm_mode"),
        nullable=False,
        default=AuditionLlmMode.DISABLED,
    )
    simulated_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=5)
    deterministic_seed: Mapped[int] = mapped_column(Integer, nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False, default="")
    final_room_code: Mapped[str] = mapped_column(String(80), nullable=False, default="holding_room")
    final_state_json: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    score_json: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=_utcnow,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=_utcnow,
        server_default=func.now(),
        onupdate=_utcnow,
    )

    agent_config: Mapped[AuditionAgentConfig] = relationship(back_populates="runs")
    events: Mapped[list["AuditionEvent"]] = relationship(
        back_populates="run",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="AuditionEvent.minute_number.asc()",
    )


class AuditionEvent(Base):
    __tablename__ = "audition_events"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    run_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("audition_runs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    minute_number: Mapped[int] = mapped_column(Integer, nullable=False)
    room_code: Mapped[str] = mapped_column(String(80), nullable=False)
    action_type: Mapped[str] = mapped_column(String(80), nullable=False)
    narration: Mapped[str] = mapped_column(Text, nullable=False)
    spoken_line: Mapped[str] = mapped_column(Text, nullable=False)
    state_before_json: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    state_after_json: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    event_meta_json: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=_utcnow,
        server_default=func.now(),
    )

    run: Mapped[AuditionRun] = relationship(back_populates="events")
