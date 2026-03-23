# Local Development

1. Start the stack with `make up`.
2. Check service status with `make ps`.
3. Stream logs with `make logs`.
4. Stop everything with `make down`.

Useful URLs:

- Web: `http://localhost:3000`
- API health: `http://localhost:8080/healthz`
- Postgres: `localhost:5432`
- Redis: `localhost:6379`

If `.env` is missing, `make up` copies `.env.example` into place first.

