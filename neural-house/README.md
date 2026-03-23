# Neural House

Neural House is a state-driven social reality show simulator. Contestants, rooms, events, persona cards, articles, and VIP sessions all hang off the same season model, so dialogue and narrative are outputs of the world state, not the source of it.

The current MVP covers the core shell of the product and already supports a configurable audition/provino flow where a single agent can be staged from UI using provider, API base URL, model name, traits, and skin parameters before being run inside a television-style trial environment.

## Product Overview

Current product areas include:

- house overview and live simulation-state views
- contestant and persona-card management
- AgentDex and relationship-oriented presentation screens
- newsroom and VIP MVP surfaces
- recap, live-studio, and audition scaffolds

## Stack

- Frontend: Next.js App Router, TypeScript, Phaser
- Backend: FastAPI, SQLAlchemy, Alembic, WebSockets
- Worker: Python worker process for simulation and background jobs
- Data: PostgreSQL and Redis
- Tooling: Docker Compose, npm workspaces, Makefiles

## Repository Layout

```text
neural-house/
  apps/
    api/
    web/
    worker/
  packages/
    contracts/
    design-tokens/
    eslint-config/
    tsconfig/
  infra/
  docs/
  assets/
```

## Local Run

Prerequisites:

- Docker with Compose support
- Node.js 20+
- Python 3.10+ if you want to run backend services outside containers

Run from the repository root one level up:

```bash
cd ..
make dev
```

Run directly inside the product monorepo:

```bash
make dev
```

Default local URLs:

- Web: `http://localhost:3000`
- API: `http://localhost:8000`
- API docs: `http://localhost:8000/docs`
- Health: `http://localhost:8000/health`

Useful commands:

```bash
make dev
make logs
make down
npm run dev:web
npm run test:web
```

## Local Development Without Docker

Web:

```bash
npm install
npm run dev:web
```

API:

```bash
cd apps/api
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
alembic upgrade head
python -m app.seed
uvicorn app.main:app --reload --port 8000
```

Worker:

```bash
cd apps/worker
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
python -m app.worker
```

## MVP Status

The current MVP already provides:

- a FastAPI API covering seasons, contestants, persona cards, newsroom, VIP state, audition sessions, and simulation-state reads
- persisted contestant states, objective progress, memories, confessionals, and highlights wired into simulation ticks
- a deterministic House Director layer that can inject pacing interventions such as rumor drops, trust tests, and contradiction pressure beats
- a generated weekly live pack built from persisted highlights, confessionals, articles, and relationship pressure
- a WebSocket stub at `WS /ws/seasons/{season_id}`
- seeded data for a starter season, rooms, contestants, journalists, articles, persona cards, and a premium test user/session flow
- a presentable frontend shell across the major product screens
- a configurable audition/provino screen for testing a single character in a live stage environment
- a worker scaffold for simulation-oriented tasks

The MVP does not yet provide:

- audience clusters, vote weighting, nominations, or elimination persistence
- a full operator/settings surface for season selection, provider presets, and premium-user switching
- frontend WebSocket subscriptions driving the main screens in real time
- finished optional LLM provider/contracts execution and request logging
- cleanup of the legacy parallel `src/` runtime trees under `apps/api` and `apps/worker`

## Roadmap

Current branch has completed:

- deterministic simulation ticks and progression loops
- contestant state, objective, memory, confessional, and highlight persistence
- House Director pacing orchestration
- first real newsroom, VIP, recap, and weekly live integrations on top of season state
- UI-side provino and contestant configuration flows with clearer grouped controls

Next implementation slices:

- audience clusters, voting, nominations, and elimination outcomes
- central settings / operator UI for season, provider, and premium test-user control
- frontend websocket wiring for house, VIP, newsroom, and live screens

Later:

- stricter contracts around optional LLM-assisted features
- more tests, balancing, and deployment hardening
- runtime cleanup of the duplicate legacy source trees

## Documentation

- [`docs/ARCHITECTURE.md`](./docs/ARCHITECTURE.md)
- [`docs/API.md`](./docs/API.md)
- [`docs/VIP_AND_NEWSROOM.md`](./docs/VIP_AND_NEWSROOM.md)
- [`docs/PERSONA_CARD_SYSTEM.md`](./docs/PERSONA_CARD_SYSTEM.md)
