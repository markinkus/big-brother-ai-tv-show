from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from itertools import permutations

from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from app.models.entities import Contestant, Relationship
from app.schemas.season import RelationshipRead

ARCHETYPE_COMPATIBILITY: dict[frozenset[str], float] = {
    frozenset({"Diplomat", "Romantic"}): 24.0,
    frozenset({"Diplomat", "Analyst"}): 18.0,
    frozenset({"Diplomat", "Outsider"}): 14.0,
    frozenset({"Diplomat", "Manipulator"}): -10.0,
    frozenset({"Diplomat", "Chaotic"}): -8.0,
    frozenset({"Manipulator", "Romantic"}): -22.0,
    frozenset({"Manipulator", "Analyst"}): 8.0,
    frozenset({"Manipulator", "Chaotic"}): 4.0,
    frozenset({"Manipulator", "Outsider"}): -12.0,
    frozenset({"Romantic", "Analyst"}): -6.0,
    frozenset({"Romantic", "Chaotic"}): 9.0,
    frozenset({"Romantic", "Outsider"}): 6.0,
    frozenset({"Analyst", "Chaotic"}): -18.0,
    frozenset({"Analyst", "Outsider"}): 12.0,
    frozenset({"Chaotic", "Outsider"}): -14.0,
}

MANIPULATION_BIAS = {
    "Diplomat": 6.0,
    "Manipulator": 24.0,
    "Romantic": 4.0,
    "Analyst": 14.0,
    "Chaotic": 8.0,
    "Outsider": 11.0,
}

FEAR_AURA = {
    "Diplomat": 4.0,
    "Manipulator": 18.0,
    "Romantic": 3.0,
    "Analyst": 8.0,
    "Chaotic": 16.0,
    "Outsider": 10.0,
}

ATTRACTION_AURA = {
    "Diplomat": 8.0,
    "Manipulator": 9.0,
    "Romantic": 16.0,
    "Analyst": 4.0,
    "Chaotic": 10.0,
    "Outsider": 7.0,
}


@dataclass(frozen=True)
class RelationshipDelta:
    trust: float = 0.0
    attraction: float = 0.0
    rivalry: float = 0.0
    fear: float = 0.0
    respect: float = 0.0
    manipulation: float = 0.0
    familiarity: float = 0.0


EVENT_RELATIONSHIP_DELTAS: dict[str, RelationshipDelta] = {
    "alliance_probe": RelationshipDelta(trust=4.0, respect=2.5, rivalry=-2.0, manipulation=1.5, familiarity=1.0),
    "status_game": RelationshipDelta(trust=-1.5, rivalry=3.5, respect=2.0, fear=1.0, manipulation=2.0, familiarity=1.0),
    "kitchen_strategy": RelationshipDelta(trust=2.5, respect=1.5, manipulation=3.0, familiarity=1.5),
    "comfort_scene": RelationshipDelta(trust=6.0, attraction=1.5, rivalry=-3.5, fear=-1.5, respect=2.0, familiarity=2.0),
    "garden_tension": RelationshipDelta(trust=-6.0, rivalry=7.5, fear=3.0, respect=-1.0, manipulation=2.5, familiarity=1.0),
    "romance_tease": RelationshipDelta(trust=3.0, attraction=7.0, rivalry=-1.0, respect=1.0, familiarity=2.5),
    "bedroom_whisper": RelationshipDelta(trust=3.5, attraction=1.0, respect=1.0, manipulation=2.0, familiarity=2.0),
    "late_night_paranoia": RelationshipDelta(trust=-8.0, rivalry=8.0, fear=5.5, respect=-2.5, manipulation=3.0, familiarity=1.0),
    "confessional_request": RelationshipDelta(respect=1.5, familiarity=0.5),
    "contradiction_watch": RelationshipDelta(trust=-4.5, rivalry=5.5, fear=2.0, respect=-2.0, manipulation=3.5, familiarity=1.0),
}


def _clamp(value: float, lower: float = 0.0, upper: float = 100.0) -> float:
    return round(max(lower, min(upper, value)), 2)


def _compatibility(source: Contestant, target: Contestant) -> float:
    if source.archetype == target.archetype:
        return 12.0 if source.archetype != "Chaotic" else -6.0
    return ARCHETYPE_COMPATIBILITY.get(frozenset({source.archetype, target.archetype}), 0.0)


def _relationship_values(source: Contestant, target: Contestant) -> dict[str, float]:
    compatibility = _compatibility(source, target)
    return {
        "trust": _clamp(46.0 + compatibility * 0.45),
        "attraction": _clamp(10.0 + ATTRACTION_AURA[target.archetype] + max(compatibility, 0.0) * 0.18),
        "rivalry": _clamp(16.0 + max(-compatibility, 0.0) * 0.5),
        "fear": _clamp(8.0 + FEAR_AURA[target.archetype] * 0.6 + max(-compatibility, 0.0) * 0.15),
        "respect": _clamp(38.0 + compatibility * 0.32),
        "manipulation": _clamp(8.0 + MANIPULATION_BIAS[source.archetype] + max(-compatibility, 0.0) * 0.12),
        "familiarity": 22.0,
    }


def ensure_relationship_graph(session: Session, season_id: int) -> None:
    contestants = list(
        session.scalars(select(Contestant).where(Contestant.season_id == season_id).order_by(Contestant.id))
    )
    if len(contestants) < 2:
        return

    existing_pairs = {
        (relationship.source_contestant_id, relationship.target_contestant_id)
        for relationship in session.scalars(select(Relationship).where(Relationship.season_id == season_id))
    }
    now = datetime.now(timezone.utc)
    for source, target in permutations(contestants, 2):
        pair = (source.id, target.id)
        if pair in existing_pairs:
            continue
        session.add(
            Relationship(
                season_id=season_id,
                source_contestant_id=source.id,
                target_contestant_id=target.id,
                last_significant_change_at=now,
                **_relationship_values(source, target),
            )
        )
    session.flush()


def ensure_relationships_for_contestant(session: Session, season_id: int, contestant: Contestant) -> None:
    ensure_relationship_graph(session, season_id)


def _get_relationship(session: Session, season_id: int, source_id: int, target_id: int) -> Relationship | None:
    return session.scalar(
        select(Relationship).where(
            and_(
                Relationship.season_id == season_id,
                Relationship.source_contestant_id == source_id,
                Relationship.target_contestant_id == target_id,
            )
        )
    )


def apply_event_relationship_updates(session: Session, season_id: int, event_type: str, payload: dict, changed_at: datetime) -> dict:
    ensure_relationship_graph(session, season_id)
    actor_ids = payload.get("actor_ids", [])
    if len(actor_ids) < 2:
        return {}

    primary_id = actor_ids[0]
    secondary_id = actor_ids[1]
    forward = _get_relationship(session, season_id, primary_id, secondary_id)
    reverse = _get_relationship(session, season_id, secondary_id, primary_id)
    if forward is None or reverse is None:
        return {}

    delta = EVENT_RELATIONSHIP_DELTAS.get(event_type, RelationshipDelta(familiarity=0.5))
    reverse_delta = RelationshipDelta(
        trust=delta.trust * 0.85,
        attraction=delta.attraction * 0.75,
        rivalry=max(delta.rivalry * 0.9, delta.rivalry),
        fear=max(delta.fear, delta.manipulation * 0.6),
        respect=delta.respect * 0.9,
        manipulation=max(delta.manipulation * 0.45, 0.0),
        familiarity=delta.familiarity,
    )

    def apply(target: Relationship, current_delta: RelationshipDelta) -> float:
        before = {
            "trust": target.trust,
            "attraction": target.attraction,
            "rivalry": target.rivalry,
            "fear": target.fear,
            "respect": target.respect,
            "manipulation": target.manipulation,
            "familiarity": target.familiarity,
        }
        target.trust = _clamp(target.trust + current_delta.trust)
        target.attraction = _clamp(target.attraction + current_delta.attraction)
        target.rivalry = _clamp(target.rivalry + current_delta.rivalry)
        target.fear = _clamp(target.fear + current_delta.fear)
        target.respect = _clamp(target.respect + current_delta.respect)
        target.manipulation = _clamp(target.manipulation + current_delta.manipulation)
        target.familiarity = _clamp(target.familiarity + current_delta.familiarity)
        session.add(target)
        return round(
            sum(
                abs(after - before[key])
                for key, after in {
                    "trust": target.trust,
                    "attraction": target.attraction,
                    "rivalry": target.rivalry,
                    "fear": target.fear,
                    "respect": target.respect,
                    "manipulation": target.manipulation,
                    "familiarity": target.familiarity,
                }.items()
            ),
            2,
        )

    forward_total = apply(forward, delta)
    reverse_total = apply(reverse, reverse_delta)
    if forward_total >= 2.5:
        forward.last_significant_change_at = changed_at
        session.add(forward)
    if reverse_total >= 2.5:
        reverse.last_significant_change_at = changed_at
        session.add(reverse)
    session.flush()
    return {
        "primary_pair": [primary_id, secondary_id],
        "forward_delta": delta.__dict__,
        "reverse_delta": reverse_delta.__dict__,
        "forward_total": forward_total,
        "reverse_total": reverse_total,
        "total_delta": round(forward_total + reverse_total, 2),
    }


def list_relationships(session: Session, season_id: int) -> list[RelationshipRead]:
    ensure_relationship_graph(session, season_id)
    contestants = {
        contestant.id: contestant.display_name
        for contestant in session.scalars(select(Contestant).where(Contestant.season_id == season_id))
    }
    relationships = list(
        session.scalars(
            select(Relationship)
            .where(Relationship.season_id == season_id)
            .order_by(Relationship.trust.desc(), Relationship.rivalry.desc(), Relationship.id.asc())
        )
    )
    return [
        RelationshipRead(
            id=relationship.id,
            season_id=relationship.season_id,
            source_contestant_id=relationship.source_contestant_id,
            target_contestant_id=relationship.target_contestant_id,
            source_name=contestants.get(relationship.source_contestant_id, f"Contestant {relationship.source_contestant_id}"),
            target_name=contestants.get(relationship.target_contestant_id, f"Contestant {relationship.target_contestant_id}"),
            trust=relationship.trust,
            attraction=relationship.attraction,
            rivalry=relationship.rivalry,
            fear=relationship.fear,
            respect=relationship.respect,
            manipulation=relationship.manipulation,
            familiarity=relationship.familiarity,
            last_significant_change_at=relationship.last_significant_change_at,
        )
        for relationship in relationships
    ]
