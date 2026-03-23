# Integration Contract

This scaffold assumes future app code will follow a few simple rules:

- Configuration comes from environment variables, not hard-coded ports or credentials.
- `DATABASE_URL` and `REDIS_URL` are the primary backend service connections.
- The web app should be able to call the API at `API_URL`.
- Each service should tolerate dependency startup order by retrying connections.

The compose file is intentionally narrow so backend and frontend teams can add real builds later without changing the surrounding workflow.

