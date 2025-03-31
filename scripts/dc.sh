#!/bin/bash

# Trouver le répertoire racine du projet (où se trouve le .env)
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

# Exécuter docker compose avec les bons fichiers et le bon .env
docker compose --env-file "$PROJECT_ROOT/.env" \
    -f "$PROJECT_ROOT/config/docker/docker-compose.yml" \
    -f "$PROJECT_ROOT/config/docker/docker-compose.local.yml" \
    -p jobmarket \
    "$@" 