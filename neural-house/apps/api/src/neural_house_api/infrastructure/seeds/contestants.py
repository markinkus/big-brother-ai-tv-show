from __future__ import annotations

from neural_house_api.application.schemas.contestants import ContestantCreate
from neural_house_api.application.services.contestant_service import ContestantService
from neural_house_api.domain.contestants import ContestantStatus


def default_contestants(seed: int) -> list[ContestantCreate]:
    return [
        ContestantCreate(
            canonical_name="aurora-vale",
            display_name="Aurora Vale",
            archetype="strategist",
            status=ContestantStatus.ACTIVE,
            energy=71,
            sociability=62,
            strategy=88,
            volatility=34,
            biography="Calm planner optimized for long-horizon alliances.",
            simulation_seed=seed,
            metadata_json={"origin": "seed", "lane": "core-cast"},
        ),
        ContestantCreate(
            canonical_name="marco-flint",
            display_name="Marco Flint",
            archetype="chaotic-charmer",
            status=ContestantStatus.ACTIVE,
            energy=84,
            sociability=91,
            strategy=53,
            volatility=79,
            biography="High-signal social operator with unstable loyalty curves.",
            simulation_seed=seed + 1,
            metadata_json={"origin": "seed", "lane": "core-cast"},
        ),
    ]


async def seed_default_contestants(
    service: ContestantService,
    seed: int,
) -> None:
    existing = await service.list_contestants()
    if existing:
        return

    for contestant in default_contestants(seed):
        await service.create_contestant(contestant)
