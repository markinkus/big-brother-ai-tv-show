from __future__ import annotations

from dataclasses import dataclass
from random import Random

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.entities import Room, SimulationEvent


@dataclass(frozen=True)
class DirectorPlan:
    mode: str
    event_type: str
    room_id: int | None
    room_code: str | None
    template: str
    reason: str
    category: str


DIRECTOR_LIBRARY: dict[str, list[tuple[str, str, str]]] = {
    "pressure_spike": [
        ("rumor_drop", "{a} hears a rumor drop about {b}, and the room tightens instantly.", "chaotic"),
        ("truth_lie_test", "{a} is pushed into a truth-and-lie test while {b} watches for cracks.", "moral_dilemma"),
    ],
    "stagnation_break": [
        ("forced_dinner", "{a} and {b} are forced into a visible dinner pairing the house cannot ignore.", "social"),
        ("trust_test", "{a} faces a public trust test with {b} as the deciding witness.", "competitive"),
    ],
    "contradiction_hunt": [
        ("contradiction_watch", "{a} is cornered into cleaning up a contradiction while {b} keeps score.", "strategic"),
        ("confessional_request", "{a} is called to explain a shaky public line before {b} can weaponize it.", "emotional"),
    ],
    "house_reset": [
        ("comfort_scene", "{a} and {b} are nudged into a softer scene to stop the floor from splitting apart.", "emotional"),
    ],
}


def choose_director_plan(
    session: Session,
    season_id: int,
    tick_number: int,
    rng: Random,
) -> DirectorPlan | None:
    recent_events = list(
        session.scalars(
            select(SimulationEvent).where(SimulationEvent.season_id == season_id).order_by(SimulationEvent.tick_number.desc()).limit(6)
        )
    )
    rooms = list(session.scalars(select(Room).where(Room.season_id == season_id).order_by(Room.id)))
    if not rooms:
        return None

    average_tension = sum(event.tension_score for event in recent_events) / max(len(recent_events), 1)
    repeated_room_pressure = len({event.room_id for event in recent_events[:3] if event.room_id is not None}) <= 1 and len(recent_events) >= 3
    contradiction_density = sum(1 for event in recent_events if event.event_type in {"contradiction_watch", "late_night_paranoia"}) >= 2

    if tick_number <= 2 or average_tension < 0.34:
        mode = "stagnation_break"
        reason = "Recent house rhythm is too flat; the director injects an externally visible pressure beat."
    elif contradiction_density:
        mode = "house_reset"
        reason = "Contradiction pressure is saturating the floor; the director softens the texture to preserve pacing."
    elif average_tension > 0.62 or repeated_room_pressure:
        mode = "contradiction_hunt"
        reason = "The current state is hot enough to justify an exposure beat."
    elif tick_number % 5 == 0:
        mode = "pressure_spike"
        reason = "Scheduled pacing intervention to avoid comfortable loops."
    else:
        return None

    event_type, template, category = rng.choice(DIRECTOR_LIBRARY[mode])
    room = rooms[rng.randrange(len(rooms))]
    return DirectorPlan(
        mode=mode,
        event_type=event_type,
        room_id=room.id,
        room_code=room.code,
        template=template,
        reason=reason,
        category=category,
    )
