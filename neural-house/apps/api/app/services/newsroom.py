from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.entities import Article, Confessional, Contestant, Highlight, Journalist, Relationship, SimulationEvent


def _contestant_names(session: Session, season_id: int) -> dict[int, str]:
    return {
        contestant.id: contestant.display_name
        for contestant in session.scalars(select(Contestant).where(Contestant.season_id == season_id))
    }


def run_newsroom_cycle(session: Session, season_id: int) -> list[Article]:
    journalists = list(session.scalars(select(Journalist).where(Journalist.season_id == season_id, Journalist.active.is_(True)).order_by(Journalist.id)))
    latest_events = list(
        session.scalars(
            select(SimulationEvent).where(SimulationEvent.season_id == season_id).order_by(SimulationEvent.tick_number.desc()).limit(4)
        )
    )
    highlights = list(
        session.scalars(select(Highlight).where(Highlight.season_id == season_id).order_by(Highlight.score.desc(), Highlight.created_at.desc()).limit(3))
    )
    names = _contestant_names(session, season_id)
    confessionals = list(
        session.scalars(
            select(Confessional)
            .join(Contestant, Contestant.id == Confessional.contestant_id)
            .where(Contestant.season_id == season_id)
            .order_by(Confessional.created_at.desc())
            .limit(2)
        )
    )
    hot_relationship = session.scalar(
        select(Relationship).where(Relationship.season_id == season_id).order_by(Relationship.rivalry.desc(), Relationship.trust.asc()).limit(1)
    )

    lead = latest_events[0] if latest_events else None
    lead_phrase = lead.event_type.replace("_", " ") if lead is not None else "house rhythm"
    highlight_phrase = highlights[0].title if highlights else "the house pressure line"
    contradiction_phrase = (
        f"{names.get(confessionals[0].contestant_id, 'A contestant')} is already carrying contradiction flags"
        if confessionals and confessionals[0].contradiction_flags_json
        else "no contradiction spike has fully broken into public certainty yet"
    )
    rivalry_phrase = (
        f"{names.get(hot_relationship.source_contestant_id, 'Contestant')} vs {names.get(hot_relationship.target_contestant_id, 'Contestant')}"
        if hot_relationship is not None
        else "the rivalry map"
    )
    referenced_event_ids = [event.id for event in latest_events]
    referenced_contestant_ids = sorted(
        {
            contestant_id
            for event in latest_events
            for contestant_id in event.payload_json.get("actor_ids", [])
        }
        | {confessional.contestant_id for confessional in confessionals}
    )

    articles: list[Article] = []
    for journalist in journalists:
        if "tabloid" in journalist.style:
            title = f"{journalist.display_name}: {lead_phrase} turns into a pressure headline"
            dek = f"{highlight_phrase} gives the gossip desk a clean new obsession."
            body = (
                "Deterministic fallback article. "
                f"The tabloid frame reads {lead_phrase} as the new ignition point, keeps one eye on {rivalry_phrase}, "
                f"and treats {contradiction_phrase} as the next possible scandal trigger."
            )
        elif "analytical" in journalist.style or "analyst" in journalist.style:
            title = f"{journalist.display_name}: {lead_phrase} changes the strategic map"
            dek = f"{highlight_phrase} matters because the alliance geometry moved."
            body = (
                "Deterministic fallback article. "
                f"The analytical desk tracks {lead_phrase} through leverage, notes {rivalry_phrase} as the sharpest pressure pair, "
                f"and treats the current highlight stack as evidence of a shifting game tree."
            )
        else:
            title = f"{journalist.display_name}: {lead_phrase} exposes the house tone"
            dek = f"{highlight_phrase} is being framed as a moral weather report."
            body = (
                "Deterministic fallback article. "
                f"The moralizing desk reads {lead_phrase} as a question of authenticity, flags that {contradiction_phrase}, "
                f"and asks whether {rivalry_phrase} reflects strategy, insecurity, or both."
            )

        article = Article(
            season_id=season_id,
            journalist_id=journalist.id,
            title=title,
            dek=dek,
            body=body,
            tone=journalist.style,
            stance=journalist.ideology,
            referenced_event_ids_json=referenced_event_ids,
            referenced_contestant_ids_json=referenced_contestant_ids,
            published_at=datetime.now(timezone.utc),
            visibility_scope="public",
        )
        session.add(article)
        articles.append(article)

    session.commit()
    for article in articles:
        session.refresh(article)
    return articles
