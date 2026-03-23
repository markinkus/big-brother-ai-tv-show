from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.entities import Article, Confessional, Contestant, Highlight, Journalist, Memory, PersonaCard, PremiumUser, Room, Season, SimulationEvent
from app.services.relationships import ensure_relationship_graph
from app.services.simulation_state import ensure_contestant_states, ensure_objectives


def seed() -> None:
    session = SessionLocal()
    try:
        existing = session.scalar(select(Season.id).limit(1))
        if existing:
            return

        season = Season(name="Neural House Season 1", status="ready", seed=424242)
        session.add(season)
        session.flush()

        rooms = [
            Room(season_id=season.id, code="living_room", name="Living Room", x=1, y=1, width=8, height=6),
            Room(season_id=season.id, code="kitchen", name="Kitchen", x=10, y=1, width=6, height=5),
            Room(season_id=season.id, code="garden", name="Garden", x=1, y=8, width=10, height=5),
            Room(season_id=season.id, code="bedroom", name="Bedroom", x=12, y=8, width=7, height=5),
            Room(season_id=season.id, code="confessional", name="Confessional", x=18, y=2, width=4, height=4),
        ]
        session.add_all(rooms)

        persona_cards = [
            PersonaCard(
                season_id=season.id,
                label="Diplomat Variant 1",
                status="approved",
                base_seed=1010,
                dominant_archetype="Diplomat",
                synopsis="Calm social broker with a private fear of irrelevance.",
                public_pitch="Builds trust fast and keeps rooms from collapsing into noise.",
                private_complexity_summary="Needs approval badly enough to blur truth under pressure.",
                trustability_score=0.78,
                manipulation_susceptibility=0.34,
                generation_notes_json={"safe_use_flags": ["fictional_role_blueprint"]},
            ),
            PersonaCard(
                season_id=season.id,
                label="Manipulator Variant 1",
                status="candidate",
                base_seed=2020,
                dominant_archetype="Manipulator",
                synopsis="Polished strategist with a talent for selective disclosure.",
                public_pitch="Reads motives instantly and weaponizes ambiguity with a smile.",
                private_complexity_summary="Masks deep insecurity by turning relationships into controlled systems.",
                trustability_score=0.39,
                manipulation_susceptibility=0.22,
                generation_notes_json={"safe_use_flags": ["fictional_role_blueprint"]},
            ),
        ]
        session.add_all(persona_cards)
        session.flush()

        contestants = [
            Contestant(
                season_id=season.id,
                display_name="Mara",
                archetype="Diplomat",
                avatar_seed=11,
                skin_palette="studio_blue",
                skin_accent="gold",
                skin_silhouette="host-ready",
                hair_style="crown",
                public_bio="Event mediator with a soft-spoken public image.",
                public_goal="Stay central without looking controlling.",
                hidden_goal_summary="Protect self-worth by becoming indispensable to everyone.",
                speech_style="measured and calming",
                persona_card_id=persona_cards[0].id,
                active=True,
            ),
            Contestant(
                season_id=season.id,
                display_name="Rico",
                archetype="Manipulator",
                avatar_seed=22,
                skin_palette="noir_gold",
                skin_accent="coral",
                skin_silhouette="sharp",
                hair_style="spikes",
                public_bio="Nightlife operator who reads a room fast.",
                public_goal="Never be on the wrong side of the vote.",
                hidden_goal_summary="Break alliances before they can isolate him.",
                speech_style="smooth and needling",
                active=True,
            ),
            Contestant(
                season_id=season.id,
                display_name="Lea",
                archetype="Romantic",
                avatar_seed=33,
                skin_palette="orchid_flash",
                skin_accent="gold",
                skin_silhouette="soft",
                hair_style="bob",
                public_bio="Big-feeling storyteller with camera instinct.",
                public_goal="Find one real bond and ride it to safety.",
                hidden_goal_summary="Turns intimacy into leverage when scared.",
                speech_style="warm and lyrical",
                active=True,
            ),
            Contestant(
                season_id=season.id,
                display_name="Noah",
                archetype="Analyst",
                avatar_seed=44,
                skin_palette="mint_signal",
                skin_accent="cyan",
                skin_silhouette="android",
                hair_style="crest",
                public_bio="Systems thinker who studies house patterns obsessively.",
                public_goal="Understand power before anyone notices him doing it.",
                hidden_goal_summary="Needs proof that logic can outperform charisma.",
                speech_style="precise and dry",
                active=True,
            ),
            Contestant(
                season_id=season.id,
                display_name="Ivy",
                archetype="Chaotic",
                avatar_seed=55,
                skin_palette="scarlet_nova",
                skin_accent="lime",
                skin_silhouette="masked",
                hair_style="veil",
                public_bio="Provocateur with a talent for breaking group autopilot.",
                public_goal="Keep the house interesting enough that it can’t settle without her.",
                hidden_goal_summary="Confuses disruption with freedom.",
                speech_style="playful and sharp",
                active=True,
            ),
            Contestant(
                season_id=season.id,
                display_name="Samir",
                archetype="Outsider",
                avatar_seed=66,
                skin_palette="mint_signal",
                skin_accent="violet",
                skin_silhouette="sharp",
                hair_style="crest",
                public_bio="Quiet observer entering with social distance and pride.",
                public_goal="Earn respect without begging for belonging.",
                hidden_goal_summary="Stores every slight for later strategic use.",
                speech_style="reserved and exact",
                active=True,
            ),
        ]
        session.add_all(contestants)
        session.flush()
        ensure_relationship_graph(session, season.id)
        ensure_contestant_states(session, season.id, seed=season.seed)
        ensure_objectives(session, season.id)

        journalists = [
            Journalist(
                season_id=season.id,
                display_name="Gia Vale",
                style="tabloid",
                ideology="attention-first gossip",
                sensationalism=0.92,
                empathy=0.31,
                bias_profile_json={"prefers": ["betrayal", "romance"]},
                activity_interval_ticks=8,
                active=True,
            ),
            Journalist(
                season_id=season.id,
                display_name="Tomas Reed",
                style="analytical",
                ideology="strategy frame",
                sensationalism=0.28,
                empathy=0.67,
                bias_profile_json={"prefers": ["alliances", "threat management"]},
                activity_interval_ticks=12,
                active=True,
            ),
            Journalist(
                season_id=season.id,
                display_name="Elena Miro",
                style="moralizing",
                ideology="cultural critique",
                sensationalism=0.44,
                empathy=0.72,
                bias_profile_json={"prefers": ["authenticity", "contradictions"]},
                activity_interval_ticks=16,
                active=True,
            ),
        ]
        session.add_all(journalists)

        premium_user = PremiumUser(
            email="vip@neural.house",
            display_name="VIP Demo User",
            premium_tier="founder",
            active=True,
        )
        session.add(premium_user)
        session.flush()

        now = datetime.now(timezone.utc)
        events = [
            SimulationEvent(
                season_id=season.id,
                tick_number=1,
                event_type="forced_dinner_seating",
                room_id=rooms[0].id,
                summary="The house forces an awkward dinner seating to break early comfort.",
                payload_json={"actor_ids": [contestants[0].id, contestants[1].id, contestants[2].id]},
                tension_score=0.44,
            ),
            SimulationEvent(
                season_id=season.id,
                tick_number=2,
                event_type="private_pairing",
                room_id=rooms[4].id,
                summary="A private pairing sends Rico and Samir into the confessional orbit.",
                payload_json={"actor_ids": [contestants[1].id, contestants[5].id]},
                tension_score=0.61,
            ),
        ]
        session.add_all(events)
        session.flush()

        session.add_all(
            [
                Highlight(
                    season_id=season.id,
                    event_id=events[0].id,
                    category="alliance",
                    title="Dinner pressure broke the opening calm",
                    summary="The forced dinner seating immediately exposed who wants harmony and who wants leverage.",
                    score=0.67,
                ),
                Highlight(
                    season_id=season.id,
                    event_id=events[1].id,
                    category="confession",
                    title="Private pairing opened the first contradiction lane",
                    summary="Rico and Samir are now carrying the earliest confessional pressure line.",
                    score=0.72,
                ),
            ]
        )
        session.add(
            Confessional(
                contestant_id=contestants[1].id,
                triggered_by_event_id=events[1].id,
                public_transcript="Rico says the pairing was harmless, but the room felt more strategic than social.",
                private_analysis="Rico is already trying to turn one forced pairing into a leverage map.",
                shadow_flags_json=["stress_spike"],
                contradiction_flags_json=["soft_language_hard_game"],
            )
        )
        session.add(
            Memory(
                contestant_id=contestants[5].id,
                memory_type="episodic",
                summary="Samir stores the private pairing as proof that the house wants him under pressure early.",
                salience=0.61,
                emotional_valence=-0.22,
                strategic_value=0.58,
                related_contestant_ids_json=[contestants[1].id],
                related_event_id=events[1].id,
                decay_rate=0.14,
            )
        )

        article = Article(
            season_id=season.id,
            journalist_id=1,
            title="The house has already picked its pressure points",
            dek="Early seating games reveal who wants harmony and who wants leverage.",
            body="Gia Vale frames the first house interventions as a rehearsal for future betrayal.",
            tone="tabloid",
            stance="attention-first gossip",
            referenced_event_ids_json=[event.id for event in events],
            referenced_contestant_ids_json=[1, 2, 6],
            published_at=now,
            visibility_scope="public",
        )
        session.add(article)
        session.commit()
    finally:
        session.close()


if __name__ == "__main__":
    seed()
