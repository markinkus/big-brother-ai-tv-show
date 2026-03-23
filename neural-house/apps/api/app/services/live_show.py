from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.entities import Article, Confessional, Contestant, Highlight, Relationship, Season, SimulationEvent
from app.schemas.live import AudiencePulseRead, LiveSegmentRead, WeeklyLiveRead


AUDIENCE_CLUSTERS = [
    ("drama_lovers", "leaning into the most combustible beat"),
    ("strategists", "tracking leverage and threat"),
    ("moralists", "judging contradictions"),
    ("romantics", "protecting the softest bond"),
]


def _contestant_names(session: Session, season_id: int) -> dict[int, str]:
    return {
        contestant.id: contestant.display_name
        for contestant in session.scalars(select(Contestant).where(Contestant.season_id == season_id))
    }


def build_weekly_live(session: Session, season_id: int) -> WeeklyLiveRead:
    season = session.get(Season, season_id)
    if season is None:
        raise ValueError("Season not found")

    names = _contestant_names(session, season_id)
    latest_event = session.scalar(
        select(SimulationEvent).where(SimulationEvent.season_id == season_id).order_by(SimulationEvent.tick_number.desc()).limit(1)
    )
    highlights = list(
        session.scalars(select(Highlight).where(Highlight.season_id == season_id).order_by(Highlight.score.desc(), Highlight.created_at.desc()).limit(3))
    )
    confessionals = list(
        session.scalars(
            select(Confessional)
            .join(Contestant, Contestant.id == Confessional.contestant_id)
            .where(Contestant.season_id == season_id)
            .order_by(Confessional.created_at.desc())
            .limit(2)
        )
    )
    articles = list(session.scalars(select(Article).where(Article.season_id == season_id).order_by(Article.published_at.desc()).limit(2)))
    tension_pairs = list(
        session.scalars(
            select(Relationship)
            .where(Relationship.season_id == season_id)
            .order_by(Relationship.rivalry.desc(), Relationship.trust.asc())
            .limit(2)
        )
    )

    segments: list[LiveSegmentRead] = []
    if latest_event is not None:
        segments.append(
            LiveSegmentRead(
                slot="intro",
                headline=f"Presenter opens on tick {latest_event.tick_number}",
                summary=latest_event.summary,
                tone="hosted",
                target_names=latest_event.payload_json.get("actor_names", []),
            )
        )
    for highlight in highlights:
        event = session.get(SimulationEvent, highlight.event_id)
        target_names = event.payload_json.get("actor_names", []) if event is not None else []
        segments.append(
            LiveSegmentRead(
                slot="highlight_reveal",
                headline=highlight.title,
                summary=highlight.summary,
                tone=highlight.category,
                target_names=target_names,
            )
        )
    for confessional in confessionals:
        segments.append(
            LiveSegmentRead(
                slot="contradiction_reveal",
                headline=f"{names.get(confessional.contestant_id, 'Contestant')} in the diary room",
                summary=confessional.public_transcript,
                tone="confessional",
                target_names=[names.get(confessional.contestant_id, "Contestant")],
            )
        )

    commentator_panels = [
        "Commentator 1: the social map is no longer flat; pressure is sticking to the same names.",
        "Commentator 2: the interesting layer is not the noise, it is who keeps trying to narrate the noise first.",
    ]
    if articles:
        commentator_panels.append(f"Newsroom echo: {articles[0].title}")

    audience_pulse = [
        AudiencePulseRead(
            cluster=cluster,
            leaning=description,
            mood="heated" if highlights else "watchful",
            intensity=round(0.44 + index * 0.11 + (highlights[0].score if highlights else 0.0) * 0.2, 2),
        )
        for index, (cluster, description) in enumerate(AUDIENCE_CLUSTERS)
    ]

    scoreboard: list[str] = []
    for relationship in tension_pairs:
        source_name = names.get(relationship.source_contestant_id, f"Contestant {relationship.source_contestant_id}")
        target_name = names.get(relationship.target_contestant_id, f"Contestant {relationship.target_contestant_id}")
        scoreboard.append(
            f"{source_name} vs {target_name} · rivalry {relationship.rivalry:.1f} · trust {relationship.trust:.1f}"
        )

    return WeeklyLiveRead(
        season_id=season_id,
        tick_number=latest_event.tick_number if latest_event is not None else 0,
        generated_at=datetime.now(timezone.utc),
        presenter_intro="Tonight the House is not just showing tension, it is showing who profits from it.",
        commentator_panels=commentator_panels,
        segments=segments,
        audience_pulse=audience_pulse,
        scoreboard=scoreboard,
    )
