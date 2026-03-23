from __future__ import annotations

from collections import defaultdict
from random import Random

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.entities import Contestant, ContestantState, Objective, Relationship, Room
from app.schemas.simulation_core import ContestantStateRead, ObjectiveRead

STATE_BASELINES: dict[str, dict[str, float]] = {
    "Diplomat": {"energy": 74.0, "stress": 22.0, "suspicion": 16.0, "ambition": 58.0, "confidence": 56.0, "loneliness": 18.0},
    "Manipulator": {"energy": 68.0, "stress": 28.0, "suspicion": 34.0, "ambition": 72.0, "confidence": 62.0, "loneliness": 26.0},
    "Romantic": {"energy": 72.0, "stress": 24.0, "suspicion": 15.0, "ambition": 48.0, "confidence": 54.0, "loneliness": 31.0},
    "Analyst": {"energy": 66.0, "stress": 26.0, "suspicion": 28.0, "ambition": 64.0, "confidence": 48.0, "loneliness": 28.0},
    "Chaotic": {"energy": 78.0, "stress": 32.0, "suspicion": 18.0, "ambition": 68.0, "confidence": 60.0, "loneliness": 22.0},
    "Outsider": {"energy": 64.0, "stress": 29.0, "suspicion": 30.0, "ambition": 61.0, "confidence": 46.0, "loneliness": 38.0},
}

FOCUS_BY_EVENT = {
    "alliance_probe": "building leverage",
    "status_game": "commanding optics",
    "kitchen_strategy": "reading motives",
    "comfort_scene": "repairing trust",
    "garden_tension": "containing conflict",
    "romance_tease": "playing intimacy",
    "bedroom_whisper": "securing secrets",
    "late_night_paranoia": "managing suspicion",
    "confessional_request": "shaping narrative",
    "contradiction_watch": "covering contradictions",
    "rumor_drop": "weaponizing ambiguity",
    "forced_dinner": "surviving pressure",
    "truth_lie_test": "balancing exposure",
    "trust_test": "proving loyalty",
}


def _clamp(value: float, lower: float = 0.0, upper: float = 100.0) -> float:
    return round(max(lower, min(upper, value)), 2)


def _progress_value(objective: Objective) -> float:
    return round(float(objective.success_conditions_json.get("progress", 0.0)), 3)


def _popularity_metrics(state: ContestantState, outgoing_relationships: list[Relationship]) -> dict[str, float]:
    avg_trust = sum(item.trust for item in outgoing_relationships) / max(len(outgoing_relationships), 1)
    avg_rivalry = sum(item.rivalry for item in outgoing_relationships) / max(len(outgoing_relationships), 1)
    avg_respect = sum(item.respect for item in outgoing_relationships) / max(len(outgoing_relationships), 1)
    public_appeal = _clamp((state.confidence * 0.35) + (state.social_visibility * 0.25) + (100.0 - state.stress) * 0.2 + avg_trust * 0.2)
    house_respect = _clamp((avg_respect * 0.55) + (state.energy * 0.15) + (state.confidence * 0.3))
    strategic_threat = _clamp((state.ambition * 0.45) + (state.suspicion * 0.2) + (avg_rivalry * 0.2) + (state.social_visibility * 0.15))
    drama_value = _clamp((state.stress * 0.35) + (avg_rivalry * 0.3) + (state.social_visibility * 0.35))
    authenticity = _clamp((avg_trust * 0.4) + (100.0 - state.suspicion) * 0.25 + (100.0 - state.stress) * 0.15 + (state.confidence * 0.2))
    meme_value = _clamp((state.social_visibility * 0.45) + (drama_value * 0.35) + (state.confidence * 0.2))
    controversy = _clamp((avg_rivalry * 0.4) + (state.suspicion * 0.25) + (state.stress * 0.2) + (state.social_visibility * 0.15))
    return {
        "public_appeal": public_appeal,
        "house_respect": house_respect,
        "strategic_threat": strategic_threat,
        "drama_value": drama_value,
        "authenticity": authenticity,
        "meme_value": meme_value,
        "controversy": controversy,
    }


def ensure_contestant_states(session: Session, season_id: int, seed: int | None = None) -> None:
    contestants = list(session.scalars(select(Contestant).where(Contestant.season_id == season_id).order_by(Contestant.id)))
    rooms = list(session.scalars(select(Room).where(Room.season_id == season_id).order_by(Room.id)))
    if not contestants or not rooms:
        return

    rng = Random(seed or (season_id * 97))
    existing_ids = {
        contestant_id
        for contestant_id in session.scalars(select(ContestantState.contestant_id).join(Contestant).where(Contestant.season_id == season_id))
    }
    for index, contestant in enumerate(contestants):
        if contestant.id in existing_ids:
            continue
        base = STATE_BASELINES.get(contestant.archetype, STATE_BASELINES["Diplomat"])
        room = rooms[(index + rng.randint(0, len(rooms) - 1)) % len(rooms)]
        state = ContestantState(
            contestant_id=contestant.id,
            room_id=room.id,
            energy=base["energy"],
            stress=base["stress"],
            suspicion=base["suspicion"],
            trust_baseline=50.0,
            loneliness=base["loneliness"],
            ambition=base["ambition"],
            confidence=base["confidence"],
            social_visibility=26.0 + index * 2,
            current_focus="settling_in",
            status_effects_json={"popularity": {}, "flags": ["fresh_entry"]},
        )
        session.add(state)
    session.flush()


def _objective_payload(progress: float = 0.0, target: float = 1.0) -> dict:
    return {"progress": progress, "target": target}


def _make_objective(
    contestant: Contestant,
    objective_type: str,
    title: str,
    description: str,
    priority: float,
    duration_ticks: int,
) -> Objective:
    return Objective(
        contestant_id=contestant.id,
        objective_type=objective_type,
        title=title,
        description=description,
        priority=priority,
        duration_ticks=duration_ticks,
        active=True,
        success_conditions_json=_objective_payload(),
        failure_conditions_json={"stress_breakpoint": 82.0, "suspicion_breakpoint": 76.0},
        reward_json={"confidence": 4.0, "public_appeal": 3.0},
        penalty_json={"stress": 5.0, "controversy": 4.0},
    )


def ensure_objectives(session: Session, season_id: int) -> None:
    contestants = list(session.scalars(select(Contestant).where(Contestant.season_id == season_id).order_by(Contestant.id)))
    active_counts = defaultdict(int)
    for contestant_id, in session.execute(select(Objective.contestant_id).where(Objective.active.is_(True))):
        active_counts[int(contestant_id)] += 1

    for contestant in contestants:
        if active_counts[contestant.id] >= 2:
            continue
        if active_counts[contestant.id] == 0:
            session.add(
                _make_objective(
                    contestant,
                    "public_positioning",
                    f"Protect {contestant.display_name}'s public line",
                    contestant.public_goal,
                    priority=62.0,
                    duration_ticks=24,
                )
            )
            session.add(
                _make_objective(
                    contestant,
                    "hidden_strategy",
                    f"Advance the hidden game for {contestant.display_name}",
                    contestant.hidden_goal_summary,
                    priority=74.0,
                    duration_ticks=28,
                )
            )
            continue

        session.add(
            _make_objective(
                contestant,
                "recovery_arc",
                f"Rebalance after the last beat for {contestant.display_name}",
                f"Stabilize {contestant.display_name}'s position while the house changes pace.",
                priority=58.0,
                duration_ticks=16,
            )
        )
    session.flush()


def list_contestant_states(session: Session, season_id: int) -> list[ContestantStateRead]:
    ensure_contestant_states(session, season_id)
    contestants = {
        contestant.id: contestant.display_name
        for contestant in session.scalars(select(Contestant).where(Contestant.season_id == season_id))
    }
    rooms = {room.id: room for room in session.scalars(select(Room).where(Room.season_id == season_id))}
    states = list(
        session.scalars(
            select(ContestantState)
            .join(Contestant, Contestant.id == ContestantState.contestant_id)
            .where(Contestant.season_id == season_id)
            .order_by(ContestantState.social_visibility.desc(), ContestantState.contestant_id.asc())
        )
    )
    return [
        ContestantStateRead(
            contestant_id=state.contestant_id,
            display_name=contestants.get(state.contestant_id, f"Contestant {state.contestant_id}"),
            room_id=state.room_id,
            room_code=rooms.get(state.room_id).code if state.room_id in rooms else None,
            room_name=rooms.get(state.room_id).name if state.room_id in rooms else None,
            energy=state.energy,
            stress=state.stress,
            suspicion=state.suspicion,
            trust_baseline=state.trust_baseline,
            loneliness=state.loneliness,
            ambition=state.ambition,
            confidence=state.confidence,
            social_visibility=state.social_visibility,
            current_focus=state.current_focus,
            status_effects_json=state.status_effects_json,
            updated_at=state.updated_at,
        )
        for state in states
    ]


def list_objectives(session: Session, season_id: int, active_only: bool = False) -> list[ObjectiveRead]:
    ensure_objectives(session, season_id)
    contestants = {
        contestant.id: contestant.display_name
        for contestant in session.scalars(select(Contestant).where(Contestant.season_id == season_id))
    }
    query = select(Objective).join(Contestant, Contestant.id == Objective.contestant_id).where(Contestant.season_id == season_id)
    if active_only:
        query = query.where(Objective.active.is_(True))
    objectives = list(session.scalars(query.order_by(Objective.active.desc(), Objective.priority.desc(), Objective.id.asc())))
    return [
        ObjectiveRead(
            id=objective.id,
            contestant_id=objective.contestant_id,
            contestant_name=contestants.get(objective.contestant_id, f"Contestant {objective.contestant_id}"),
            objective_type=objective.objective_type,
            title=objective.title,
            description=objective.description,
            priority=objective.priority,
            duration_ticks=objective.duration_ticks,
            active=objective.active,
            progress=_progress_value(objective),
            success_conditions_json=objective.success_conditions_json,
            failure_conditions_json=objective.failure_conditions_json,
            reward_json=objective.reward_json,
            penalty_json=objective.penalty_json,
            created_at=objective.created_at,
            updated_at=objective.updated_at,
        )
        for objective in objectives
    ]


def top_objectives_by_contestant(session: Session, contestant_ids: list[int], limit: int = 3) -> dict[int, list[Objective]]:
    if not contestant_ids:
        return {}
    objective_map: dict[int, list[Objective]] = defaultdict(list)
    objectives = list(
        session.scalars(
            select(Objective)
            .where(Objective.contestant_id.in_(contestant_ids), Objective.active.is_(True))
            .order_by(Objective.priority.desc(), Objective.id.asc())
        )
    )
    for objective in objectives:
        if len(objective_map[objective.contestant_id]) < limit:
            objective_map[objective.contestant_id].append(objective)
    return dict(objective_map)


def apply_tick_state_transitions(
    session: Session,
    season_id: int,
    event_type: str,
    room_id: int | None,
    actor_ids: list[int],
    director_mode: str | None,
) -> dict[int, dict]:
    ensure_contestant_states(session, season_id)
    contestant_ids = list(session.scalars(select(Contestant.id).where(Contestant.season_id == season_id)))
    relationship_map: dict[int, list[Relationship]] = defaultdict(list)
    for relationship in session.scalars(select(Relationship).where(Relationship.season_id == season_id)):
        relationship_map[relationship.source_contestant_id].append(relationship)

    state_map = {
        state.contestant_id: state
        for state in session.scalars(select(ContestantState).where(ContestantState.contestant_id.in_(contestant_ids)))
    }

    updates: dict[int, dict] = {}
    for contestant_id in contestant_ids:
        state = state_map[contestant_id]
        before = {
            "energy": state.energy,
            "stress": state.stress,
            "suspicion": state.suspicion,
            "confidence": state.confidence,
            "loneliness": state.loneliness,
            "social_visibility": state.social_visibility,
        }
        is_active = contestant_id in actor_ids
        if is_active:
            event_heat = 8.0 if event_type in {"garden_tension", "late_night_paranoia", "truth_lie_test"} else 5.0
            event_heat += 2.0 if director_mode in {"pressure_spike", "contradiction_hunt"} else 0.0
            state.room_id = room_id
            state.energy = _clamp(state.energy - (4.0 + event_heat * 0.2))
            state.stress = _clamp(state.stress + event_heat)
            state.suspicion = _clamp(state.suspicion + (5.5 if "strategy" in event_type or "paranoia" in event_type else 2.2))
            state.confidence = _clamp(state.confidence + (3.5 if event_type in {"status_game", "alliance_probe", "romance_tease"} else -1.0))
            state.loneliness = _clamp(state.loneliness - (5.0 if event_type in {"comfort_scene", "romance_tease"} else 1.5))
            state.social_visibility = _clamp(state.social_visibility + (6.0 if room_id is not None else 3.0))
            state.current_focus = FOCUS_BY_EVENT.get(event_type, "adapting to the house")
        else:
            state.energy = _clamp(state.energy + 1.6)
            state.stress = _clamp(state.stress - 1.4)
            state.suspicion = _clamp(state.suspicion + 0.6)
            state.loneliness = _clamp(state.loneliness + 0.8)
            state.social_visibility = _clamp(state.social_visibility - 0.6)
            if director_mode == "house_reset":
                state.stress = _clamp(state.stress - 0.8)

        outgoing = relationship_map.get(contestant_id, [])
        state.trust_baseline = round(sum(item.trust for item in outgoing) / max(len(outgoing), 1), 2)
        state.status_effects_json = {
            "popularity": _popularity_metrics(state, outgoing),
            "flags": [director_mode] if director_mode else [],
        }
        session.add(state)
        updates[contestant_id] = {
            "before": before,
            "after": {
                "energy": state.energy,
                "stress": state.stress,
                "suspicion": state.suspicion,
                "confidence": state.confidence,
                "loneliness": state.loneliness,
                "social_visibility": state.social_visibility,
            },
            "focus": state.current_focus,
            "room_id": state.room_id,
        }

    session.flush()
    return updates


def apply_objective_progress(
    session: Session,
    actor_ids: list[int],
    event_type: str,
    tension_score: float,
) -> dict[int, list[dict]]:
    if not actor_ids:
        return {}
    objective_map = top_objectives_by_contestant(session, actor_ids, limit=3)
    progress_delta = 0.05 + tension_score * 0.08
    if event_type in {"alliance_probe", "kitchen_strategy", "status_game", "truth_lie_test"}:
        progress_delta += 0.04
    if event_type in {"comfort_scene", "romance_tease"}:
        progress_delta += 0.02

    updates: dict[int, list[dict]] = defaultdict(list)
    for contestant_id, objectives in objective_map.items():
        for objective in objectives:
            current = _progress_value(objective)
            target = float(objective.success_conditions_json.get("target", 1.0))
            next_progress = round(min(target, current + progress_delta * (objective.priority / 100.0)), 3)
            objective.success_conditions_json = {**objective.success_conditions_json, "progress": next_progress, "target": target}
            objective.duration_ticks = max(objective.duration_ticks - 1, 0)
            if next_progress >= target or objective.duration_ticks == 0:
                objective.active = False
            session.add(objective)
            updates[contestant_id].append(
                {
                    "objective_id": objective.id,
                    "title": objective.title,
                    "progress": next_progress,
                    "active": objective.active,
                }
            )

    session.flush()
    season_id = None
    if actor_ids:
        contestant = session.get(Contestant, actor_ids[0])
        season_id = contestant.season_id if contestant is not None else None
    if season_id is not None:
        ensure_objectives(session, season_id)
    return dict(updates)
