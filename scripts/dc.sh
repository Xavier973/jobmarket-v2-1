#!/bin/bash

# Trouver le répertoire racine du projet
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

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

# Se placer dans le répertoire racine
cd "$PROJECT_ROOT"

# Exécuter docker compose
echo "Exécution en environnement: $ENV"
docker compose -p jobmarket "$@" 