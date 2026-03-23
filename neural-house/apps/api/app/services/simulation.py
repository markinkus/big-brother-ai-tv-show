from __future__ import annotations

from random import Random

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.entities import Contestant, Room, Season, SimulationEvent
from app.services.confessionals import create_confessionals_for_event
from app.services.highlights import create_highlight_for_event
from app.services.house_director import DirectorPlan, choose_director_plan
from app.services.memory import create_memories_for_event
from app.services.relationships import apply_event_relationship_updates, ensure_relationship_graph
from app.services.simulation_state import (
    apply_objective_progress,
    apply_tick_state_transitions,
    ensure_contestant_states,
    ensure_objectives,
    top_objectives_by_contestant,
)

EVENT_LIBRARY = {
    "living_room": [
        ("alliance_probe", "{a} tests {b}'s loyalty with a soft alliance probe."),
        ("status_game", "{a} takes control of the couch rhythm while {b} measures the optics."),
    ],
    "kitchen": [
        ("kitchen_strategy", "{a} turns casual kitchen chatter into a strategic read on {b}."),
        ("comfort_scene", "{a} offers cover to {b} while the cameras stay close."),
    ],
    "garden": [
        ("garden_tension", "{a} and {b} drift into a tense low-voice exchange in the garden."),
        ("romance_tease", "{a} leans into a playful beat with {b} under the night lights."),
    ],
    "bedroom": [
        ("bedroom_whisper", "{a} tries to lock a private read with {b} before the room wakes up."),
        ("late_night_paranoia", "{a} feeds late-night suspicion into {b}'s earshot."),
    ],
    "confessional": [
        ("confessional_request", "{a} asks for a confessional after a pressure spike."),
        ("contradiction_watch", "{a} rehearses a cleaner public line before facing the cameras again."),
    ],
}

TENSION_BY_EVENT = {
    "alliance_probe": 0.42,
    "status_game": 0.36,
    "kitchen_strategy": 0.39,
    "comfort_scene": 0.24,
    "garden_tension": 0.64,
    "romance_tease": 0.28,
    "bedroom_whisper": 0.47,
    "late_night_paranoia": 0.72,
    "confessional_request": 0.31,
    "contradiction_watch": 0.55,
    "rumor_drop": 0.76,
    "forced_dinner": 0.61,
    "truth_lie_test": 0.78,
    "trust_test": 0.66,
}


def _next_tick(session: Session, season_id: int) -> int:
    latest = session.scalar(select(func.max(SimulationEvent.tick_number)).where(SimulationEvent.season_id == season_id))
    return (latest or 0) + 1


def _event_novelty(session: Session, season_id: int, event_type: str) -> float:
    recent_types = list(
        session.scalars(select(SimulationEvent.event_type).where(SimulationEvent.season_id == season_id).order_by(SimulationEvent.tick_number.desc()).limit(5))
    )
    return 1.0 if event_type not in recent_types else 0.35


def _build_event(
    session: Session,
    season: Season,
    tick_number: int,
) -> tuple[SimulationEvent, list[Contestant], Room, DirectorPlan | None]:
    contestants = list(session.scalars(select(Contestant).where(Contestant.season_id == season.id, Contestant.active.is_(True)).order_by(Contestant.id)))
    rooms = list(session.scalars(select(Room).where(Room.season_id == season.id).order_by(Room.id)))
    if len(contestants) < 2 or not rooms:
        raise ValueError("Season requires at least two active contestants and one room")

    rng = Random((season.seed * 10_000) + tick_number)
    director_plan = choose_director_plan(session, season.id, tick_number, rng)
    room = next((item for item in rooms if item.id == director_plan.room_id), rooms[0]) if director_plan else rooms[rng.randrange(len(rooms))]
    active_count = min(len(contestants), max(2, rng.randint(2, 4)))
    active_contestants = rng.sample(contestants, active_count)
    primary = active_contestants[0]
    secondary = active_contestants[1]
    objective_map = top_objectives_by_contestant(session, [contestant.id for contestant in active_contestants], limit=1)

    if director_plan is not None:
        event_type = director_plan.event_type
        template = director_plan.template
        room = next((item for item in rooms if item.id == director_plan.room_id), room)
    else:
        event_type, template = rng.choice(EVENT_LIBRARY[room.code])

    summary = template.format(a=primary.display_name, b=secondary.display_name)
    payload = {
        "room_code": room.code,
        "room_name": room.name,
        "actor_ids": [contestant.id for contestant in active_contestants],
        "actor_names": [contestant.display_name for contestant in active_contestants],
        "visibility": "public",
        "beat_kind": event_type,
        "director_mode": director_plan.mode if director_plan else None,
        "director_reason": director_plan.reason if director_plan else None,
        "objective_focus": {
            str(contestant_id): [objective.title for objective in objectives]
            for contestant_id, objectives in objective_map.items()
        },
    }
    return (
        SimulationEvent(
            season_id=season.id,
            tick_number=tick_number,
            event_type=event_type,
            room_id=room.id,
            summary=summary,
            payload_json=payload,
            tension_score=TENSION_BY_EVENT[event_type],
        ),
        active_contestants,
        room,
        director_plan,
    )


def set_simulation_status(session: Session, season_id: int, status: str) -> Season:
    season = session.get(Season, season_id)
    if season is None:
        raise ValueError("Season not found")
    season.status = status
    session.add(season)
    session.commit()
    session.refresh(season)
    return season


def run_simulation_ticks(session: Session, season_id: int, count: int) -> list[SimulationEvent]:
    season = session.get(Season, season_id)
    if season is None:
        raise ValueError("Season not found")
    ensure_relationship_graph(session, season_id)
    ensure_contestant_states(session, season_id, seed=season.seed)
    ensure_objectives(session, season_id)

    events: list[SimulationEvent] = []
    for _ in range(count):
        tick_number = _next_tick(session, season_id)
        event, active_contestants, room, director_plan = _build_event(session, season, tick_number)
        actor_ids = [contestant.id for contestant in active_contestants]
        session.add(event)
        session.flush()

        relationship_delta = apply_event_relationship_updates(
            session,
            season_id,
            event.event_type,
            event.payload_json,
            event.created_at,
        )
        state_updates = apply_tick_state_transitions(
            session,
            season_id,
            event.event_type,
            room.id,
            actor_ids,
            director_plan.mode if director_plan else None,
        )
        objective_updates = apply_objective_progress(session, actor_ids, event.event_type, event.tension_score)
        objective_map = top_objectives_by_contestant(session, actor_ids, limit=3)
        novelty = _event_novelty(session, season_id, event.event_type)
        memory_ids = create_memories_for_event(
            session,
            season_id,
            event.id,
            event.event_type,
            event.summary,
            actor_ids,
            float(relationship_delta.get("total_delta", 0.0)),
            objective_map,
            state_updates,
            novelty,
            event.tension_score,
        )
        confessional_ids = create_confessionals_for_event(
            session,
            season_id,
            event.id,
            event.event_type,
            actor_ids,
            state_updates,
            director_plan.mode if director_plan else None,
        )
        highlight_id = create_highlight_for_event(
            session,
            season_id,
            event,
            float(relationship_delta.get("total_delta", 0.0)),
            state_updates,
            objective_updates,
            len(confessional_ids),
        )

        event.payload_json = {
            **event.payload_json,
            "relationship_delta": relationship_delta,
            "state_changes": {
                str(contestant_id): {
                    "focus": update["focus"],
                    "room_id": update["room_id"],
                    "after": update["after"],
                }
                for contestant_id, update in state_updates.items()
                if contestant_id in actor_ids
            },
            "objective_updates": objective_updates,
            "memory_ids": memory_ids,
            "confessional_ids": confessional_ids,
            "highlight_id": highlight_id,
        }
        session.add(event)
        session.flush()
        events.append(event)

    season.status = "running"
    session.add(season)
    session.commit()
    for event in events:
        session.refresh(event)
    return events
