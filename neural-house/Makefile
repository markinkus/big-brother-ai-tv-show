COMPOSE = docker compose -f infra/docker-compose.yml

.PHONY: dev down logs install-web dev-web api-seed api-migrate

dev:
	$(COMPOSE) up --build

down:
	$(COMPOSE) down --remove-orphans

logs:
	$(COMPOSE) logs -f

install-web:
	npm install

dev-web:
	npm run dev:web

api-migrate:
	cd apps/api && alembic upgrade head

api-seed:
	cd apps/api && python -m app.seed

