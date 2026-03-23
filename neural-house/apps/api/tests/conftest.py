from __future__ import annotations

from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.db.session import get_db
from app.main import app
from app.models.base import Base
from app.models.entities import AuditionEvent, AuditionSession, Contestant, Room, Season


@pytest.fixture()
def sqlite_session_factory(tmp_path: Path) -> sessionmaker[Session]:
    database_path = tmp_path / "neural-house-test.db"
    engine = create_engine(
        f"sqlite+pysqlite:///{database_path}",
        future=True,
        connect_args={"check_same_thread": False},
    )
    _ = AuditionSession, AuditionEvent
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


@pytest.fixture()
def client(sqlite_session_factory: sessionmaker[Session]) -> Generator[TestClient, None, None]:
    def override_get_db() -> Generator[Session, None, None]:
        db = sqlite_session_factory()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


@pytest.fixture()
def seeded_season(sqlite_session_factory: sessionmaker[Session]) -> int:
    db = sqlite_session_factory()
    try:
        season = Season(name="Smoke Test Season", status="ready", seed=424242)
        db.add(season)
        db.flush()

        rooms = [
            Room(season_id=season.id, code="living_room", name="Living Room", x=1, y=1, width=8, height=6),
            Room(season_id=season.id, code="kitchen", name="Kitchen", x=10, y=1, width=6, height=5),
            Room(season_id=season.id, code="garden", name="Garden", x=1, y=8, width=10, height=5),
            Room(season_id=season.id, code="bedroom", name="Bedroom", x=12, y=8, width=7, height=5),
            Room(season_id=season.id, code="confessional", name="Confessional", x=18, y=2, width=4, height=4),
        ]
        db.add_all(rooms)
        db.flush()

        contestants = [
            Contestant(
                season_id=season.id,
                display_name="Mara",
                archetype="Diplomat",
                avatar_seed=11,
                public_bio="Test seed contestant.",
                public_goal="Keep the peace.",
                hidden_goal_summary="Stay central.",
                speech_style="measured",
                active=True,
            ),
            Contestant(
                season_id=season.id,
                display_name="Rico",
                archetype="Manipulator",
                avatar_seed=22,
                public_bio="Test seed contestant.",
                public_goal="Stay safe.",
                hidden_goal_summary="Break alliances.",
                speech_style="smooth",
                active=True,
            ),
            Contestant(
                season_id=season.id,
                display_name="Lea",
                archetype="Romantic",
                avatar_seed=33,
                public_bio="Test seed contestant.",
                public_goal="Find a bond.",
                hidden_goal_summary="Use intimacy as cover.",
                speech_style="warm",
                active=True,
            ),
        ]
        db.add_all(contestants)
        db.commit()
        return season.id
    finally:
        db.close()
