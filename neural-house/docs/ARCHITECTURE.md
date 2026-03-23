# Architecture

Neural House is implemented as a modular monolith:

- `apps/api`: FastAPI application exposing REST and WebSocket interfaces, persistence, deterministic services, and seed flows.
- `apps/worker`: Redis/RQ worker process for simulation ticks, newsroom cycles, recap jobs, and persona generation jobs.
- `apps/web`: Next.js App Router frontend with a retro-inspired shell and Phaser house viewport.
- `packages/contracts`: shared frontend contract schemas and payload types.
- `packages/design-tokens`: reusable palette and typography primitives.
- `infra`: Docker Compose topology and environment bootstrap.

Layering inside `apps/api`:

- `models`: SQLAlchemy entities
- `schemas`: request/response contracts
- `repositories`: persistence access
- `services`: domain/application logic
- `api/routes`: transport layer
- `websocket`: real-time connection manager

Current core simulation slice:

- `simulation.py` orchestrates each tick as a bounded state transition over active contestants.
- `simulation_state.py` owns contestant states, objective generation, and objective progress.
- `house_director.py` decides whether pacing needs intervention beats such as rumor drops or trust tests.
- `memory.py` records salience-scored memories and performs deterministic decay/compression.
- `confessionals.py` emits diary-room outputs when stress, suspicion, or contradiction thresholds trip.
- `highlights.py` scores each event for recap/studio/newsroom surfaces.
- `live_show.py` builds the current weekly live pack from persisted highlights, confessionals, articles, and relationship pressure.
