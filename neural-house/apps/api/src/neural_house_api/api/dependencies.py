from collections.abc import AsyncIterator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from neural_house_api.application.services.contestant_service import ContestantService
from neural_house_api.infrastructure.db.session import get_db_session
from neural_house_api.infrastructure.db.repositories.contestant_repository import (
    ContestantRepository,
)


async def db_session_dependency() -> AsyncIterator[AsyncSession]:
    async for session in get_db_session():
        yield session


def contestant_service_dependency(
    session: AsyncSession = Depends(db_session_dependency),
) -> ContestantService:
    repository = ContestantRepository(session)
    return ContestantService(repository)
