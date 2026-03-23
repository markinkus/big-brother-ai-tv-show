from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from neural_house_api.domain.models.contestant import Contestant


class ContestantRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list(self) -> list[Contestant]:
        result = await self._session.execute(
            select(Contestant).order_by(Contestant.created_at.asc())
        )
        return list(result.scalars().all())

    async def get(self, contestant_id: UUID) -> Contestant | None:
        return await self._session.get(Contestant, contestant_id)

    async def create(self, contestant: Contestant) -> Contestant:
        self._session.add(contestant)
        await self._session.commit()
        await self._session.refresh(contestant)
        return contestant

    async def save(self, contestant: Contestant) -> Contestant:
        await self._session.commit()
        await self._session.refresh(contestant)
        return contestant

    async def delete(self, contestant_id: UUID) -> bool:
        contestant = await self.get(contestant_id)
        if contestant is None:
            return False
        await self._session.delete(contestant)
        await self._session.commit()
        return True
