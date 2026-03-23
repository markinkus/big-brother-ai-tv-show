from __future__ import annotations

from collections import defaultdict

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.entities import Contestant, Memory, Objective
from app.schemas.simulation_core import MemoryRead


def _clamp(value: float, lower: float = 0.0, upper: float = 1.0) -> float:
    return round(max(lower, min(upper, value)), 3)


def _goal_relevance(objectives: list[Objective]) -> float:
    if not objectives:
        return 0.35
    return _clamp(sum(float(item.success_conditions_json.get("progress", 0.0)) + (item.priority / 100.0) for item in objectives) / (len(objectives) * 1.8))


def _memory_type(event_type: str, salience: float, primary: bool) -> str:
    if event_type in {"confessional_request", "contradiction_watch"}:
        return "core"
    if primary and event_type in {"alliance_probe", "kitchen_strategy", "truth_lie_test", "rumor_drop"}:
        return "secret"
    if salience >= 0.72:
        return "core"
    if salience < 0.35:
        return "working"
    return "episodic"


def create_memories_for_event(
    session: Session,
    season_id: int,
    event_id: int,
    event_type: str,
    event_summary: str,
    actor_ids: list[int],
    relationship_total_delta: float,
    objective_map: dict[int, list[Objective]],
    state_updates: dict[int, dict],
    novelty: float,
    event_intensity: float,
) -> list[int]:
    contestants = {
        contestant.id: contestant
        for contestant in session.scalars(select(Contestant).where(Contestant.season_id == season_id))
    }
    created_ids: list[int] = []
    for index, contestant_id in enumerate(actor_ids):
        contestant = contestants.get(contestant_id)
        if contestant is None:
            continue
        deltas = state_updates.get(contestant_id, {})
        before = deltas.get("before", {})
        after = deltas.get("after", {})
        emotional_impact = _clamp(
            sum(abs(float(after.get(key, 0.0)) - float(before.get(key, 0.0))) for key in ("stress", "confidence", "loneliness")) / 90.0
        )
        social_consequence = _clamp(relationship_total_delta / 25.0)
        goal_relevance = _goal_relevance(objective_map.get(contestant_id, []))
        salience = _clamp(
            (event_intensity * 0.30)
            + (goal_relevance * 0.25)
            + (emotional_impact * 0.20)
            + (social_consequence * 0.15)
            + (novelty * 0.10)
        )
        confidence_shift = float(after.get("confidence", 0.0)) - float(before.get("confidence", 0.0))
        stress_shift = float(after.get("stress", 0.0)) - float(before.get("stress", 0.0))
        emotional_valence = round(max(-1.0, min(1.0, (confidence_shift - stress_shift) / 12.0)), 3)
        strategic_value = _clamp((goal_relevance * 0.55) + (social_consequence * 0.45))
        memory = Memory(
            contestant_id=contestant_id,
            memory_type=_memory_type(event_type, salience, primary=index == 0),
            summary=f"{contestant.display_name} stores the beat: {event_summary}",
            salience=salience,
            emotional_valence=emotional_valence,
            strategic_value=strategic_value,
            related_contestant_ids_json=[actor_id for actor_id in actor_ids if actor_id != contestant_id],
            related_event_id=event_id,
            decay_rate=0.08 if salience >= 0.72 else 0.16,
        )
        session.add(memory)
        session.flush()
        created_ids.append(memory.id)

    _decay_and_compress_memories(session, season_id)
    return created_ids


def _decay_and_compress_memories(session: Session, season_id: int) -> None:
    contestants = list(session.scalars(select(Contestant).where(Contestant.season_id == season_id)))
    for contestant in contestants:
        memories = list(
            session.scalars(
                select(Memory).where(Memory.contestant_id == contestant.id).order_by(Memory.salience.desc(), Memory.updated_at.desc())
            )
        )
        for memory in memories:
            memory.salience = _clamp(memory.salience * (1.0 - memory.decay_rate * 0.15))
            memory.strategic_value = _clamp(memory.strategic_value * (1.0 - memory.decay_rate * 0.08))
            session.add(memory)
            if memory.salience < 0.12:
                session.delete(memory)

        kept = [memory for memory in memories if memory.salience >= 0.12]
        if len(kept) <= 8:
            continue

        compressed_source = kept[6:]
        merged_summary = " | ".join(memory.summary for memory in compressed_source[:3])
        compressed = Memory(
            contestant_id=contestant.id,
            memory_type="archive",
            summary=f"Compressed memory braid: {merged_summary}",
            salience=_clamp(sum(memory.salience for memory in compressed_source) / len(compressed_source)),
            emotional_valence=round(sum(memory.emotional_valence for memory in compressed_source) / len(compressed_source), 3),
            strategic_value=_clamp(sum(memory.strategic_value for memory in compressed_source) / len(compressed_source)),
            related_contestant_ids_json=sorted({related for memory in compressed_source for related in memory.related_contestant_ids_json}),
            related_event_id=compressed_source[0].related_event_id,
            decay_rate=0.22,
        )
        session.add(compressed)
        for memory in compressed_source:
            session.delete(memory)

    session.flush()


def list_memories(session: Session, season_id: int, limit_per_contestant: int = 3) -> list[MemoryRead]:
    contestants = {
        contestant.id: contestant.display_name
        for contestant in session.scalars(select(Contestant).where(Contestant.season_id == season_id))
    }
    grouped: dict[int, int] = defaultdict(int)
    memories = list(
        session.scalars(
            select(Memory)
            .join(Contestant, Contestant.id == Memory.contestant_id)
            .where(Contestant.season_id == season_id)
            .order_by(Memory.salience.desc(), Memory.updated_at.desc(), Memory.id.desc())
        )
    )
    response: list[MemoryRead] = []
    for memory in memories:
        if grouped[memory.contestant_id] >= limit_per_contestant:
            continue
        grouped[memory.contestant_id] += 1
        response.append(
            MemoryRead(
                id=memory.id,
                contestant_id=memory.contestant_id,
                contestant_name=contestants.get(memory.contestant_id, f"Contestant {memory.contestant_id}"),
                memory_type=memory.memory_type,
                summary=memory.summary,
                salience=memory.salience,
                emotional_valence=memory.emotional_valence,
                strategic_value=memory.strategic_value,
                related_contestant_ids_json=memory.related_contestant_ids_json,
                related_event_id=memory.related_event_id,
                decay_rate=memory.decay_rate,
                created_at=memory.created_at,
                updated_at=memory.updated_at,
            )
        )
    return response
