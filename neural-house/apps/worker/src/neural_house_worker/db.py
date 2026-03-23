from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from neural_house_worker.config import get_settings

settings = get_settings()

engine = create_async_engine(settings.database_url, future=True)
SessionFactory = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)
