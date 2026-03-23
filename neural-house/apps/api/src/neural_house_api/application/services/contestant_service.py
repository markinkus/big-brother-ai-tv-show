from __future__ import annotations

from uuid import UUID

from neural_house_api.application.schemas.contestants import (
    ContestantCreate,
    ContestantUpdate,
)
from neural_house_api.domain.models.contestant import Contestant
from neural_house_api.infrastructure.db.repositories.contestant_repository import (
    ContestantRepository,
)


class ContestantService:
    def __init__(self, repository: ContestantRepository) -> None:
        self._repository = repository

    async def list_contestants(self) -> list[Contestant]:
        return await self._repository.list()

    async def get_contestant(self, contestant_id: UUID) -> Contestant | None:
        return await self._repository.get(contestant_id)

    async def create_contestant(self, payload: ContestantCreate) -> Contestant:
        contestant = Contestant(**payload.model_dump())
        return await self._repository.create(contestant)

    async def update_contestant(
        self,
        contestant_id: UUID,
        payload: ContestantUpdate,
    ) -> Contestant | None:
        contestant = await self._repository.get(contestant_id)
        if contestant is None:
            return None

        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(contestant, field, value)

        return await self._repository.save(contestant)

    async def delete_contestant(self, contestant_id: UUID) -> bool:
        return await self._repository.delete(contestant_id)
