from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from neural_house_api.api.dependencies import contestant_service_dependency
from neural_house_api.application.schemas.contestants import (
    ContestantCreate,
    ContestantRead,
    ContestantUpdate,
)
from neural_house_api.application.services.contestant_service import ContestantService

router = APIRouter()


@router.get("", response_model=list[ContestantRead])
async def list_contestants(
    service: ContestantService = Depends(contestant_service_dependency),
) -> list[ContestantRead]:
    contestants = await service.list_contestants()
    return [ContestantRead.model_validate(contestant) for contestant in contestants]


@router.post("", response_model=ContestantRead, status_code=status.HTTP_201_CREATED)
async def create_contestant(
    payload: ContestantCreate,
    service: ContestantService = Depends(contestant_service_dependency),
) -> ContestantRead:
    contestant = await service.create_contestant(payload)
    return ContestantRead.model_validate(contestant)


@router.get("/{contestant_id}", response_model=ContestantRead)
async def get_contestant(
    contestant_id: UUID,
    service: ContestantService = Depends(contestant_service_dependency),
) -> ContestantRead:
    contestant = await service.get_contestant(contestant_id)
    if contestant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contestant not found")
    return ContestantRead.model_validate(contestant)


@router.patch("/{contestant_id}", response_model=ContestantRead)
async def update_contestant(
    contestant_id: UUID,
    payload: ContestantUpdate,
    service: ContestantService = Depends(contestant_service_dependency),
) -> ContestantRead:
    contestant = await service.update_contestant(contestant_id, payload)
    if contestant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contestant not found")
    return ContestantRead.model_validate(contestant)


@router.delete("/{contestant_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contestant(
    contestant_id: UUID,
    service: ContestantService = Depends(contestant_service_dependency),
) -> None:
    deleted = await service.delete_contestant(contestant_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contestant not found")
