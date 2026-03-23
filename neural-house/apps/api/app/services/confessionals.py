from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.entities import Confessional, Contestant
from app.schemas.simulation_core import ConfessionalRead


def _contradiction_flags(contestant: Contestant, event_type: str) -> list[str]:
    hidden = contestant.hidden_goal_summary.lower()
    public_goal = contestant.public_goal.lower()
    flags: list[str] = []
    if event_type in {"comfort_scene", "romance_tease"} and any(term in hidden for term in ["break", "leverage", "use intimacy", "control"]):
        flags.append("care_used_as_cover")
    if event_type in {"alliance_probe", "status_game", "kitchen_strategy"} and any(term in public_goal for term in ["peace", "bond", "respect"]):
        flags.append("soft_language_hard_game")
    if event_type in {"contradiction_watch", "truth_lie_test"}:
        flags.append("public_line_under_review")
    return flags


def _shadow_flags(stress: float, suspicion: float, confidence: float) -> list[str]:
    flags: list[str] = []
    if stress >= 62.0:
        flags.append("stress_spike")
    if suspicion >= 58.0:
        flags.append("paranoia_spike")
    if confidence <= 42.0:
        flags.append("confidence_drop")
    return flags


def create_confessionals_for_event(
    session: Session,
    season_id: int,
    event_id: int,
    event_type: str,
    actor_ids: list[int],
    state_updates: dict[int, dict],
    director_mode: str | None,
) -> list[int]:
    contestants = {
        contestant.id: contestant
        for contestant in session.scalars(select(Contestant).where(Contestant.season_id == season_id))
    }
    confessional_ids: list[int] = []
    for contestant_id in actor_ids[:2]:
        contestant = contestants.get(contestant_id)
        if contestant is None:
            continue
        after = state_updates.get(contestant_id, {}).get("after", {})
        stress = float(after.get("stress", 0.0))
        suspicion = float(after.get("suspicion", 0.0))
        confidence = float(after.get("confidence", 0.0))
        contradiction_flags = _contradiction_flags(contestant, event_type)
        trigger = stress >= 34.0 or suspicion >= 30.0 or bool(contradiction_flags) or director_mode == "contradiction_hunt"
        if not trigger:
            continue

        shadow_flags = _shadow_flags(stress, suspicion, confidence)
        public_transcript = (
            f"{contestant.display_name} says the house beat was manageable, but admits the room shifted after {event_type.replace('_', ' ')}."
        )
        private_analysis = (
            f"{contestant.display_name} is privately tracking {contestant.hidden_goal_summary.lower()} while the current stress level sits at {stress:.1f}."
        )
        confessional = Confessional(
            contestant_id=contestant_id,
            triggered_by_event_id=event_id,
            public_transcript=public_transcript,
            private_analysis=private_analysis,
            shadow_flags_json=shadow_flags,
            contradiction_flags_json=contradiction_flags,
        )
        session.add(confessional)
        session.flush()
        confessional_ids.append(confessional.id)

    return confessional_ids


def list_confessionals(session: Session, season_id: int, limit: int = 12) -> list[ConfessionalRead]:
    contestants = {
        contestant.id: contestant.display_name
        for contestant in session.scalars(select(Contestant).where(Contestant.season_id == season_id))
    }
    confessionals = list(
        session.scalars(
            select(Confessional)
            .join(Contestant, Contestant.id == Confessional.contestant_id)
            .where(Contestant.season_id == season_id)
            .order_by(Confessional.created_at.desc(), Confessional.id.desc())
            .limit(limit)
        )
    )
    return [
        ConfessionalRead(
            id=confessional.id,
            contestant_id=confessional.contestant_id,
            contestant_name=contestants.get(confessional.contestant_id, f"Contestant {confessional.contestant_id}"),
            triggered_by_event_id=confessional.triggered_by_event_id,
            public_transcript=confessional.public_transcript,
            private_analysis=confessional.private_analysis,
            shadow_flags_json=confessional.shadow_flags_json,
            contradiction_flags_json=confessional.contradiction_flags_json,
            created_at=confessional.created_at,
        )
        for confessional in confessionals
    ]
