#!/bin/bash

ENV=$1
CONFIG_DIR="config/docker"

# Se placer dans le répertoire racine du projet
cd "$(dirname "$0")/.." || exit

# Vérification des dossiers requis
required_dirs=(
    "config/nginx/local"
    "config/nginx/prod"
    "nginx/logs"
    "nginx/ssl"
    "data/raw/francetravail"
    "data/transformed/francetravail"
    "data/processed/francetravail"
    "data/logs/francetravail"
    "ETL"
    "Utils"
)

for dir in "${required_dirs[@]}"; do
    if [ ! -d "$dir" ]; then
        echo "Création du dossier $dir"
        mkdir -p "$dir"
    fi
done

# Vérifier que le fichier .env existe et le charger
if [ ! -f "config/env/.env.$ENV" ]; then
    echo "Erreur: Le fichier config/env/.env.$ENV n'existe pas"
    exit 1
fi

# Copier et charger le fichier .env
echo "Chargement des variables d'environnement..."
cp "config/env/.env.$ENV" .env
set -a  # automatically export all variables
source .env
set +a

# Vérifier les variables essentielles
required_vars=("ES_HOST" "DATA_RAW_DIR" "DATA_LOG_DIR")
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "Erreur: La variable $var n'est pas définie dans .env.$ENV"
        exit 1
    fi
done

case $ENV in
    "local")
        echo "Déploiement en local..."
        cp config/env/.env.local .env
        
        echo "Arrêt des conteneurs existants..."
        docker compose -f $CONFIG_DIR/docker-compose.yml \
                      -f $CONFIG_DIR/docker-compose.local.yml \
                      down

        echo "Démarrage des conteneurs..."
        docker compose -p jobmarket \
                      -f $CONFIG_DIR/docker-compose.yml \
                      -f $CONFIG_DIR/docker-compose.local.yml \
                      up -d
        ;;
    "prod")
        echo "Déploiement en production..."
        cp config/env/.env.prod .env
        
        echo "Arrêt des conteneurs existants..."
        docker compose -f $CONFIG_DIR/docker-compose.yml \
                      -f $CONFIG_DIR/docker-compose.prod.yml \
                      down

        echo "Démarrage des conteneurs..."
        docker compose -p jobmarket \
                      -f $CONFIG_DIR/docker-compose.yml \
                      -f $CONFIG_DIR/docker-compose.prod.yml \
                      up -d
        ;;
    *)
        echo "Usage: ./deploy.sh [local|prod]"
        exit 1
        ;;
esac 