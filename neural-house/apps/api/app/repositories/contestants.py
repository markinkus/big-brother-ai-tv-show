from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.entities import Contestant
from app.schemas.contestant import ContestantCreate, ContestantUpdate
from app.services.relationships import ensure_relationships_for_contestant


def list_contestants(session: Session, season_id: int) -> list[Contestant]:
    return list(session.scalars(select(Contestant).where(Contestant.season_id == season_id).order_by(Contestant.id)))


def get_contestant(session: Session, contestant_id: int) -> Contestant | None:
    return session.get(Contestant, contestant_id)


def create_contestant(session: Session, season_id: int, payload: ContestantCreate) -> Contestant:
    contestant = Contestant(season_id=season_id, **payload.model_dump())
    session.add(contestant)
    session.flush()
    ensure_relationships_for_contestant(session, season_id, contestant)
    session.commit()
    session.refresh(contestant)
    return contestant


def update_contestant(session: Session, contestant: Contestant, payload: ContestantUpdate) -> Contestant:
    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(contestant, field, value)
    session.add(contestant)
    session.commit()
    session.refresh(contestant)
    return contestant
