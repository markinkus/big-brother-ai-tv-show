# ADR 0001: Repo Boundaries

Status: accepted

Context:

- The monorepo is being bootstrapped before the application code exists.
- Multiple teams will work in parallel on backend and frontend code.

Decision:

- Keep this layer limited to root docs, infra, and root config files.
- Do not place business logic in the bootstrap scaffolding.
- Use environment-based service contracts so apps can be swapped in later.

Consequences:

- Local development is available immediately.
- Real app services can land independently as long as they honor the documented environment contract.

