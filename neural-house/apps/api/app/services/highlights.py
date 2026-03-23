from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.entities import Highlight, SimulationEvent
from app.schemas.simulation_core import HighlightRead

SPECTACLE_VALUE = {
    "alliance_probe": 0.52,
    "status_game": 0.58,
    "kitchen_strategy": 0.56,
    "comfort_scene": 0.34,
    "garden_tension": 0.74,
    "romance_tease": 0.49,
    "bedroom_whisper": 0.57,
    "late_night_paranoia": 0.78,
    "confessional_request": 0.46,
    "contradiction_watch": 0.71,
    "rumor_drop": 0.75,
    "forced_dinner": 0.63,
    "truth_lie_test": 0.77,
    "trust_test": 0.68,
}


def _clamp(value: float, lower: float = 0.0, upper: float = 1.0) -> float:
    return round(max(lower, min(upper, value)), 3)


def _category_for_event(event_type: str) -> str:
    if event_type in {"garden_tension", "late_night_paranoia", "truth_lie_test"}:
        return "conflict"
    if event_type in {"alliance_probe", "kitchen_strategy", "trust_test"}:
        return "alliance"
    if event_type in {"romance_tease"}:
        return "romance"
    if event_type in {"rumor_drop", "contradiction_watch"}:
        return "contradiction"
    if event_type in {"confessional_request"}:
        return "confession"
    return "challenge"


def create_highlight_for_event(
    session: Session,
    season_id: int,
    event: SimulationEvent,
    relationship_total_delta: float,
    state_updates: dict[int, dict],
    objective_updates: dict[int, list[dict]],
    confessional_count: int,
) -> int:
    recent_highlights = list(
        session.scalars(select(Highlight).where(Highlight.season_id == season_id).order_by(Highlight.created_at.desc()).limit(5))
    )
    novelty = 1.0 if all(item.category != _category_for_event(event.event_type) for item in recent_highlights) else 0.42
    emotional_impact = _clamp(
        sum(
            abs(float(update.get("after", {}).get("stress", 0.0)) - float(update.get("before", {}).get("stress", 0.0)))
            + abs(float(update.get("after", {}).get("confidence", 0.0)) - float(update.get("before", {}).get("confidence", 0.0)))
            for update in state_updates.values()
        )
        / max(len(state_updates), 1)
        / 18.0
    )
    objective_relevance = _clamp(
        sum(item["progress"] for updates in objective_updates.values() for item in updates) / max(sum(len(item) for item in objective_updates.values()), 1)
    )
    contradiction_bonus = 1.0 if confessional_count else 0.0
    conflict = max(event.tension_score, _clamp(relationship_total_delta / 18.0))
    delta_relazioni = _clamp(relationship_total_delta / 20.0)
    spectacular = SPECTACLE_VALUE.get(event.event_type, 0.45)
    score = _clamp(
        (delta_relazioni * 0.20)
        + (emotional_impact * 0.20)
        + (objective_relevance * 0.15)
        + (conflict * 0.15)
        + (contradiction_bonus * 0.10)
        + (novelty * 0.10)
        + (spectacular * 0.10)
    )
    actor_names = event.payload_json.get("actor_names", [])
    headline = " vs ".join(actor_names[:2]) if len(actor_names) >= 2 else (actor_names[0] if actor_names else "House beat")
    highlight = Highlight(
        season_id=season_id,
        event_id=event.id,
        category=_category_for_event(event.event_type),
        title=f"{headline}: {event.event_type.replace('_', ' ')}",
        summary=f"Tick {event.tick_number} pushed {headline.lower()} into a {event.event_type.replace('_', ' ')} beat with score {score:.2f}.",
        score=score,
    )
    session.add(highlight)
    session.flush()
    return highlight.id


def list_highlights(session: Session, season_id: int, limit: int = 12) -> list[HighlightRead]:
    highlights = list(
        session.scalars(
            select(Highlight).where(Highlight.season_id == season_id).order_by(Highlight.score.desc(), Highlight.created_at.desc()).limit(limit)
        )
    )
    return [
        HighlightRead(
            id=highlight.id,
            season_id=highlight.season_id,
            event_id=highlight.event_id,
            category=highlight.category,
            title=highlight.title,
            summary=highlight.summary,
            score=highlight.score,
            created_at=highlight.created_at,
        )
        for highlight in highlights
    ]
