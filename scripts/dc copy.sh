#!/bin/bash

# Trouver le répertoire racine du projet
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CONFIG_DIR="$PROJECT_ROOT/config/docker"

# Par défaut, utiliser l'environnement local
ENV=${ENV:-local}

# Vérifier que le fichier .env existe
if [ ! -f "$PROJECT_ROOT/.env" ]; then
    echo "Fichier .env non trouvé, copie de .env.$ENV..."
    cp "$PROJECT_ROOT/config/env/.env.$ENV" "$PROJECT_ROOT/.env"
else
    echo "Fichier .env trouvé dans $PROJECT_ROOT/.env"
fi

# Charger les variables d'environnement
echo "Chargement des variables d'environnement..."
set -a
source "$PROJECT_ROOT/.env"
set +a

# Exécuter docker compose avec les bons fichiers selon l'environnement
case $ENV in
    "local")
        echo "Utilisation de la configuration locale..."
        docker compose --env-file "$PROJECT_ROOT/.env" \
            -f "$CONFIG_DIR/docker-compose.yml" \
            -f "$CONFIG_DIR/docker-compose.local.yml" \
            -p jobmarket \
            "$@"
        ;;
    "prod")
        echo "Utilisation de la configuration de production..."
        docker compose --env-file "$PROJECT_ROOT/.env" \
            -f "$CONFIG_DIR/docker-compose.yml" \
            -f "$CONFIG_DIR/docker-compose.prod.yml" \
            -p jobmarket \
            "$@"
        ;;
    *)
        echo "Environnement $ENV non reconnu. Utilisation de local par défaut..."
        docker compose --env-file "$PROJECT_ROOT/.env" \
            -f "$CONFIG_DIR/docker-compose.yml" \
            -f "$CONFIG_DIR/docker-compose.local.yml" \
            -p jobmarket \
            "$@"
        ;;
esac 