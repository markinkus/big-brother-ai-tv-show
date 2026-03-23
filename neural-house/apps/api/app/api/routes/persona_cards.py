from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.entities import Contestant, PersonaCard
from app.schemas.contestant import ContestantRead
from app.schemas.persona_card import CreateContestantFromCardRequest, PersonaCardGenerateRequest, PersonaCardRead
from app.services.persona_generator import generate_persona_cards
from app.websocket.manager import manager

router = APIRouter(prefix="/api", tags=["persona_cards"])


@router.post("/seasons/{season_id}/persona-cards/generate", response_model=list[PersonaCardRead])
async def generate_cards(season_id: int, payload: PersonaCardGenerateRequest, db: Session = Depends(get_db)):
    cards = generate_persona_cards(db, season_id, payload)
    await manager.broadcast(
        season_id,
        {
            "type": "event.created",
            "season_id": season_id,
            "tick_number": None,
            "timestamp": cards[0].created_at.isoformat() if cards else "",
            "payload": {"persona_card_ids": [card.id for card in cards]},
        },
    )
    return cards


@router.get("/seasons/{season_id}/persona-cards", response_model=list[PersonaCardRead])
def list_cards(season_id: int, db: Session = Depends(get_db)):
    return list(db.scalars(select(PersonaCard).where(PersonaCard.season_id == season_id).order_by(PersonaCard.id.desc())))


@router.get("/persona-cards/{persona_card_id}", response_model=PersonaCardRead)
def get_card(persona_card_id: int, db: Session = Depends(get_db)):
    card = db.get(PersonaCard, persona_card_id)
    if card is None:
        raise HTTPException(status_code=404, detail="Persona card not found")
    return card


@router.post("/persona-cards/{persona_card_id}/approve", response_model=PersonaCardRead)
def approve_card(persona_card_id: int, db: Session = Depends(get_db)):
    card = db.get(PersonaCard, persona_card_id)
    if card is None:
        raise HTTPException(status_code=404, detail="Persona card not found")
    card.status = "approved"
    db.add(card)
    db.commit()
    db.refresh(card)
    return card


@router.post("/persona-cards/{persona_card_id}/create-contestant", response_model=ContestantRead)
async def create_contestant_from_card(
    persona_card_id: int, payload: CreateContestantFromCardRequest, db: Session = Depends(get_db)
):
    card = db.get(PersonaCard, persona_card_id)
    if card is None:
        raise HTTPException(status_code=404, detail="Persona card not found")
    if card.status != "approved":
        raise HTTPException(status_code=400, detail="Persona card must be approved before contestant creation")

    contestant = Contestant(
        season_id=card.season_id,
        display_name=payload.display_name_override or card.label,
        archetype=card.dominant_archetype,
        avatar_seed=card.base_seed,
        public_bio=card.public_pitch,
        public_goal="Enter the house with a strong social read and remain nomination-safe.",
        hidden_goal_summary=card.private_complexity_summary,
        speech_style=payload.speech_style_override or "camera-aware restraint",
        persona_card_id=card.id,
        active=True,
    )
    db.add(contestant)
    db.commit()
    db.refresh(contestant)
    await manager.broadcast(
        card.season_id,
        {
            "type": "contestant.state_changed",
            "season_id": card.season_id,
            "tick_number": None,
            "timestamp": contestant.created_at.isoformat(),
            "payload": {"contestant_id": contestant.id, "persona_card_id": card.id},
        },
    )
    return contestant

