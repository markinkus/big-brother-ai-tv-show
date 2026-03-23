from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.entities import Article, Journalist
from app.schemas.article import ArticleRead, JournalistRead, RunNewsroomCycleResponse
from app.services.newsroom import run_newsroom_cycle
from app.websocket.manager import manager

router = APIRouter(prefix="/api", tags=["newsroom"])


@router.get("/seasons/{season_id}/journalists", response_model=list[JournalistRead])
def list_journalists(season_id: int, db: Session = Depends(get_db)):
    return list(db.scalars(select(Journalist).where(Journalist.season_id == season_id).order_by(Journalist.id)))


@router.get("/seasons/{season_id}/articles", response_model=list[ArticleRead])
def list_articles(season_id: int, db: Session = Depends(get_db)):
    return list(db.scalars(select(Article).where(Article.season_id == season_id).order_by(Article.published_at.desc())))


@router.get("/articles/{article_id}", response_model=ArticleRead)
def get_article(article_id: int, db: Session = Depends(get_db)):
    article = db.get(Article, article_id)
    if article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    return article


@router.post("/seasons/{season_id}/newsroom/run-cycle", response_model=RunNewsroomCycleResponse)
async def run_cycle(season_id: int, db: Session = Depends(get_db)):
    articles = run_newsroom_cycle(db, season_id)
    for article in articles:
        await manager.broadcast(
            season_id,
            {
                "type": "article.published",
                "season_id": season_id,
                "tick_number": None,
                "timestamp": article.published_at.isoformat(),
                "payload": {"article_id": article.id, "title": article.title},
            },
        )
    return RunNewsroomCycleResponse(published_article_ids=[article.id for article in articles])

