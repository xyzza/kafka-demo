.PHONY: exec build db down clean api load logs
DOCKER_DIR = docker
COMPOSE_FILES = -f $(DOCKER_DIR)/docker-compose.yml
OVERRIDE_FILE = $(DOCKER_DIR)/docker-compose.override.yml

ifneq (,$(wildcard $(OVERRIDE_FILE)))
    COMPOSE_FILES += -f $(OVERRIDE_FILE)
endif

exec:
	@docker compose $(COMPOSE_FILES) run --remove-orphans --rm --entrypoint /bin/bash build_source

build:
	@docker compose $(COMPOSE_FILES) build build_source --no-cache

up:
	@docker compose $(COMPOSE_FILES) up -d

db:
	@docker compose $(COMPOSE_FILES) up -d db

api:
	@docker compose $(COMPOSE_FILES) up -d api

load:
	@wrk -t4 -c50 -d30s -s scripts/load.lua http://localhost:8000

logs:
	@docker compose $(COMPOSE_FILES) logs -f --tail=200 $(name)

down:
	@docker compose $(COMPOSE_FILES) down

clean:
	@docker compose $(COMPOSE_FILES) down -v --remove-orphans --rmi local
