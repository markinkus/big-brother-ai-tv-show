# LLM Contracts

The first deliverable defines shared contract shapes in `packages/contracts/src/index.ts` and mirrors them in the backend roadmap.

Contract families:

- action plans
- dialogue turns
- confessionals
- article outputs
- persona card variants

Rules:

- all model outputs must be strict JSON
- one repair attempt on validation failure
- deterministic fallback after failed repair
- token estimates and purpose must be logged

