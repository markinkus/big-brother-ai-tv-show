from __future__ import annotations

import random
from datetime import UTC, datetime
from dataclasses import asdict

from sqlalchemy.ext.asyncio import AsyncSession

from neural_house_worker.config import get_settings
from neural_house_worker.models import ContestantState, contestant_projection


class HouseSimulationEngine:
    def __init__(self, seed: int) -> None:
        self._seed = seed

    async def run_tick(self, session: AsyncSession) -> dict[str, object]:
        result = await session.execute(contestant_projection)
        contestants = list(result.all())
        rng = random.Random(self._seed + len(contestants))

        states = [
            ContestantState(
                contestant_id=str(row.id),
                display_name=row.display_name,
                tension_score=max(0, min(100, row.volatility + rng.randint(-8, 8))),
                alliance_score=max(0, min(100, row.sociability + row.strategy // 2 + rng.randint(-5, 5))),
            )
            for row in contestants
        ]

        return {
            "type": "simulation.tick",
            "generated_at": datetime.now(UTC).isoformat(),
            "seed": self._seed,
            "contestant_count": len(states),
            "states": [asdict(state) for state in states],
        }


def build_engine() -> HouseSimulationEngine:
    settings = get_settings()
    return HouseSimulationEngine(seed=settings.simulation_seed)
