#!/bin/bash

# Trouver le répertoire racine du projet
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

# Vérifier que le fichier .env existe
if [ ! -f "$PROJECT_ROOT/.env" ]; then
    echo "Fichier .env non trouvé, copie de .env.local..."
    cp "$PROJECT_ROOT/config/env/.env.local" "$PROJECT_ROOT/.env"
else
    echo "Fichier .env trouvé dans $PROJECT_ROOT/.env"
fi

# Charger les variables d'environnement
echo "Chargement des variables d'environnement..."
set -a
source "$PROJECT_ROOT/.env"
set +a

# Exécuter docker compose avec les bons fichiers
docker compose --env-file "$PROJECT_ROOT/.env" \
    -f "$PROJECT_ROOT/config/docker/docker-compose.yml" \
    -f "$PROJECT_ROOT/config/docker/docker-compose.local.yml" \
    -p jobmarket \
    "$@" 