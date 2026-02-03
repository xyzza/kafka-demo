.PHONY: exec build db down clean
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

down:
	@docker compose $(COMPOSE_FILES) down

clean:
	@docker compose $(COMPOSE_FILES) down -v --remove-orphans --rmi local
