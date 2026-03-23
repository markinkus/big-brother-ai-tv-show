from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.audition import AuditionCreateRequest, AuditionEventRead, AuditionLiveState, AuditionSessionRead
from app.services.audition import (
    create_audition_session,
    get_audition_session,
    get_live_state,
    list_audition_events,
    list_audition_sessions,
    serialize_event,
    serialize_session,
)

router = APIRouter(prefix="/api", tags=["auditions"])


@router.get("/auditions", response_model=list[AuditionSessionRead])
def get_auditions(db: Session = Depends(get_db)) -> list[AuditionSessionRead]:
    return [serialize_session(session) for session in list_audition_sessions(db)]


@router.post("/auditions", response_model=AuditionSessionRead)
def create_audition(payload: AuditionCreateRequest, db: Session = Depends(get_db)) -> AuditionSessionRead:
    session = create_audition_session(db, payload)
    session = get_audition_session(db, session.id)
    assert session is not None
    return serialize_session(session)


@router.get("/auditions/{session_id}", response_model=AuditionSessionRead)
def get_audition(session_id: int, db: Session = Depends(get_db)) -> AuditionSessionRead:
    session = get_audition_session(db, session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Audition session not found")
    return serialize_session(session)


@router.get("/auditions/{session_id}/events", response_model=list[AuditionEventRead])
def get_audition_events(
    session_id: int,
    visible_only: bool = Query(default=False),
    db: Session = Depends(get_db),
) -> list[AuditionEventRead]:
    session = get_audition_session(db, session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Audition session not found")
    return [serialize_event(event) for event in list_audition_events(db, session_id, visible_only)]


@router.get("/auditions/{session_id}/live", response_model=AuditionLiveState)
def get_audition_live(session_id: int, db: Session = Depends(get_db)) -> AuditionLiveState:
    live_state = get_live_state(db, session_id)
    if live_state is None:
        raise HTTPException(status_code=404, detail="Audition session not found")
    return live_state
