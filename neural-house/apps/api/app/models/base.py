from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class TimestampedMixin:
    created_at: Mapped[datetime] = mapped_column(default=utcnow)


class UpdatedTimestampedMixin(TimestampedMixin):
    updated_at: Mapped[datetime] = mapped_column(default=utcnow, onupdate=utcnow)

