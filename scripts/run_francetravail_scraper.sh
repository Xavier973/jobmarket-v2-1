#!/bin/bash

# Configuration du logging
LOG_FILE="/home/ubuntu/jobmarket-v2-1/data/logs/francetravail/cron.log"
mkdir -p "$(dirname "$LOG_FILE")"

# Fonction de logging
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S'): $1" >> "$LOG_FILE"
}

# Début de l'exécution
log "Début de l'exécution du scraper France Travail"

# Vérification du répertoire
cd /home/ubuntu/jobmarket-v2-1 || {
    log "ERREUR: Impossible d'accéder au répertoire /home/ubuntu/jobmarket-v2-1"
    exit 1
}

# Vérification que le conteneur francetravail est en cours d'exécution
if ! ./scripts/dc.sh ps | grep -q "francetravail.*Up"; then
    log "Le conteneur francetravail n'est pas en cours d'exécution. Tentative de démarrage..."
    ./scripts/dc.sh up -d francetravail
    sleep 10  # Attendre que le conteneur soit prêt
fi

# Exécution du script Python
log "Lancement du script Python dans le conteneur"
if ./scripts/dc.sh exec -T francetravail python /app/ETL/Extract/FranceTravail/src/main.py; then
    log "Exécution du scraper France Travail terminée avec succès"
else
    log "ERREUR: L'exécution du script a échoué"
    exit 1
fi 