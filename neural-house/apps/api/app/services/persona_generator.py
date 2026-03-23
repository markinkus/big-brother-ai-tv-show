from __future__ import annotations

from random import Random

from sqlalchemy.orm import Session

from app.models.entities import PersonaCard
from app.schemas.persona_card import PersonaCardGenerateRequest

ARCHETYPES = ["Diplomat", "Manipulator", "Romantic", "Analyst", "Chaotic", "Outsider"]
HOOKS = [
    "wins rooms with measured warmth and surgical listening",
    "performs sincerity while privately mapping every weakness",
    "treats every bond as either sanctuary or leverage",
    "sees patterns first and people second until feelings leak through",
    "weaponizes unpredictability against stale power blocs",
    "enters with outsider dignity and a long memory for slights",
]


def generate_persona_cards(session: Session, season_id: int, payload: PersonaCardGenerateRequest) -> list[PersonaCard]:
    rng = Random(season_id * 1000 + payload.requested_count)
    requested = payload.requested_count
    archetypes = payload.dominant_archetypes or ARCHETYPES
    created: list[PersonaCard] = []

    for index in range(requested):
        archetype = archetypes[index % len(archetypes)]
        hook = HOOKS[index % len(HOOKS)]
        card = PersonaCard(
            season_id=season_id,
            label=f"{archetype} Variant {index + 1}",
            status="candidate",
            base_seed=rng.randint(1000, 9999),
            dominant_archetype=archetype,
            synopsis=f"A {archetype.lower()} profile that {hook}.",
            public_pitch=f"Public-facing role tuned for {archetype.lower()} drama without degrading cultural or religious framing.",
            private_complexity_summary="Carries a controlled contradiction between social performance and private need for safety.",
            trustability_score=round(rng.uniform(0.35, 0.86), 2),
            manipulation_susceptibility=round(rng.uniform(0.2, 0.78), 2),
            generation_notes_json={
                "short_hook": hook,
                "cultural_context_summary": "Urban and multi-layered, grounded in respectful fictional social context.",
                "historical_context_summary": "Uses abstract pseudo-historical cues instead of literal identity claims.",
                "religious_context_summary": "Optional spiritual framing remains reverent and non-mocking.",
                "speech_style_cues": ["measured cadence", "clean irony", "camera-aware restraint"],
                "safe_use_flags": ["fictional_role_blueprint", "sensitivity_checked"],
            },
        )
        session.add(card)
        created.append(card)

    session.commit()
    for card in created:
        session.refresh(card)
    return created

