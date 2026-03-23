# Architecture

Initial shape:

- `postgres` holds durable relational state.
- `redis` backs ephemeral cache, queue, and coordination use cases.
- `api` serves the backend HTTP surface.
- `worker` handles async jobs and background processing.
- `web` serves the browser-facing UI.

The first scaffold keeps these roles separate so teams can replace the stub services independently without reworking the local developer contract.

