from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import auditions, contestants, health, live, newsroom, persona_cards, seasons, vip, ws
from app.core.config import settings

app = FastAPI(title=settings.app_name, version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(seasons.router)
app.include_router(contestants.router)
app.include_router(auditions.router)
app.include_router(persona_cards.router)
app.include_router(newsroom.router)
app.include_router(vip.router)
app.include_router(live.router)
app.include_router(ws.router)
