COMPOSE ?= docker compose
COMPOSE_FILE ?= docker-compose.yml

.PHONY: help init dev up down restart logs ps config clean web-build web-lint

help:
	@printf '%s\n' \
		'Targets:' \
		'  make init      Create .env from .env.example if needed' \
		'  make dev       Start the full Neural House stack' \
		'  make up        Alias for make dev' \
		'  make down      Stop the local stack' \
		'  make restart   Rebuild and restart the local stack' \
		'  make logs      Follow container logs' \
		'  make ps        Show running services' \
		'  make config    Render the resolved compose config' \
		'  make web-build Build the Next.js app locally' \
		'  make web-lint  Lint the Next.js app locally' \
		'  make clean     Stop the stack and remove volumes'

init:
	@if [ ! -f .env ]; then cp .env.example .env; fi

dev: init
	$(COMPOSE) -f $(COMPOSE_FILE) up -d --build

up: dev

down:
	$(COMPOSE) -f $(COMPOSE_FILE) down

restart: down up

logs:
	$(COMPOSE) -f $(COMPOSE_FILE) logs -f --tail=100

ps:
	$(COMPOSE) -f $(COMPOSE_FILE) ps

config:
	$(COMPOSE) -f $(COMPOSE_FILE) config

web-build:
	cd neural-house && npm run build:web

web-lint:
	cd neural-house && npm run lint:web

clean:
	$(COMPOSE) -f $(COMPOSE_FILE) down -v --remove-orphans
