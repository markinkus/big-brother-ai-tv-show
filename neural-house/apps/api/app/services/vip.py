from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.entities import Contestant, ContestantState, Highlight, PremiumUser, Relationship, Room, SimulationEvent, VipAccessSession
from app.schemas.vip import VipRoomSummaryRead, VipStateRead


def build_vip_state(session: Session, season_id: int, selected_room_code: str | None = None) -> VipStateRead:
    rooms = list(session.scalars(select(Room).where(Room.season_id == season_id).order_by(Room.id)))
    room_by_id = {room.id: room for room in rooms}
    room_by_code = {room.code: room for room in rooms}
    recent_events = list(
        session.scalars(
            select(SimulationEvent).where(SimulationEvent.season_id == season_id).order_by(SimulationEvent.tick_number.desc()).limit(8)
        )
    )
    recent_highlights = list(
        session.scalars(select(Highlight).where(Highlight.season_id == season_id).order_by(Highlight.score.desc(), Highlight.created_at.desc()).limit(4))
    )
    contestants = {
        contestant.id: contestant.display_name
        for contestant in session.scalars(select(Contestant).where(Contestant.season_id == season_id))
    }
    states = list(
        session.scalars(
            select(ContestantState)
            .join(Contestant, Contestant.id == ContestantState.contestant_id)
            .where(Contestant.season_id == season_id)
            .order_by(ContestantState.social_visibility.desc())
        )
    )
    occupancy: dict[int, list[str]] = defaultdict(list)
    for state in states:
        if state.room_id is not None:
            occupancy[state.room_id].append(contestants.get(state.contestant_id, f"Contestant {state.contestant_id}"))

    selected_room = room_by_code.get(selected_room_code) if selected_room_code else None
    if selected_room is None and recent_events and recent_events[0].room_id in room_by_id:
        selected_room = room_by_id[recent_events[0].room_id]
    selected_room_code = selected_room.code if selected_room is not None else selected_room_code

    room_summaries: list[VipRoomSummaryRead] = []
    for room in rooms:
        room_events = [event for event in recent_events if event.room_id == room.id][:3]
        tension = round(sum(event.tension_score for event in room_events) / max(len(room_events), 1), 2)
        latest_summary = room_events[0].summary if room_events else "Room is in a holding pattern."
        room_summaries.append(
            VipRoomSummaryRead(
                room_code=room.code,
                room_name=room.name,
                occupant_names=occupancy.get(room.id, []),
                activity_summary=latest_summary,
                tension=tension,
            )
        )

    relationship_rows = list(
        session.scalars(
            select(Relationship)
            .where(Relationship.season_id == season_id)
            .order_by(Relationship.trust.desc(), Relationship.rivalry.desc(), Relationship.id.asc())
            .limit(24)
        )
    )
    active_alliances = [
        f"{contestants.get(item.source_contestant_id, 'Contestant')} trusts {contestants.get(item.target_contestant_id, 'Contestant')} at {item.trust:.1f}"
        for item in relationship_rows
        if item.trust >= 62.0 and item.rivalry <= 35.0
    ][:3]
    active_conflicts = [
        f"{contestants.get(item.source_contestant_id, 'Contestant')} is locked on {contestants.get(item.target_contestant_id, 'Contestant')} with rivalry {item.rivalry:.1f}"
        for item in relationship_rows
        if item.rivalry >= 48.0
    ][:3]
    last_change_digest = [highlight.summary for highlight in recent_highlights[:3]]
    if recent_events:
        last_change_digest.extend(event.summary for event in recent_events[:2])

    filtered_events = recent_events
    if selected_room is not None:
        room_specific = [event for event in recent_events if event.room_id == selected_room.id]
        if room_specific:
            filtered_events = room_specific
    tick_number = filtered_events[0].tick_number if filtered_events else 0
    tension = round(sum(event.tension_score for event in filtered_events[:5]) / max(min(len(filtered_events), 5), 1), 2)
    return VipStateRead(
        season_id=season_id,
        tick_number=tick_number,
        selected_room_code=selected_room_code,
        tension=tension,
        active_alliances=active_alliances or ["No stable alliance has crossed the VIP threshold yet."],
        active_conflicts=active_conflicts or ["No conflict spike currently exceeds the VIP alert threshold."],
        recent_events=[event.summary for event in filtered_events[:5]],
        recent_highlights=[highlight.title for highlight in recent_highlights],
        last_change_digest=last_change_digest[:5],
        room_summaries=room_summaries,
        visibility_policy="VIP shows live state and public-pattern inference. Fully private confessional truth stays masked unless admin mode changes it.",
        rooms=rooms,
    )


def start_vip_session(session: Session, season_id: int, premium_user_id: int, selected_room_code: str | None) -> VipAccessSession:
    user = session.get(PremiumUser, premium_user_id)
    if user is None or not user.active:
        raise ValueError("Premium access is required.")

    vip_session = VipAccessSession(
        premium_user_id=premium_user_id,
        season_id=season_id,
        started_at=datetime.now(timezone.utc),
        ended_at=None,
        selected_room_code=selected_room_code,
        session_meta_json={"entry_mode": "debug_stub", "visibility_policy": "masked_private_state"},
    )
    session.add(vip_session)
    session.commit()
    session.refresh(vip_session)
    return vip_session


def end_vip_session(session: Session, session_id: int) -> VipAccessSession:
    vip_session = session.get(VipAccessSession, session_id)
    if vip_session is None:
        raise ValueError("VIP session not found.")
    vip_session.ended_at = datetime.now(timezone.utc)
    session.add(vip_session)
    session.commit()
    session.refresh(vip_session)
    return vip_session
