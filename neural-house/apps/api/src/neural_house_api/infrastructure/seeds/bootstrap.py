from __future__ import annotations

import asyncio

from neural_house_api.application.services.contestant_service import ContestantService
from neural_house_api.core.settings import get_settings
from neural_house_api.infrastructure.db.repositories.contestant_repository import (
    ContestantRepository,
)
from neural_house_api.infrastructure.db.session import SessionFactory
from neural_house_api.infrastructure.seeds.contestants import seed_default_contestants


async def run_seed() -> None:
    settings = get_settings()
    async with SessionFactory() as session:
        service = ContestantService(ContestantRepository(session))
        await seed_default_contestants(service, settings.simulation_seed)


def main() -> None:
    asyncio.run(run_seed())


if __name__ == "__main__":
    main()
