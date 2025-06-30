#!/bin/bash

# Fichier de log
LOG_FILE="/home/ubuntu/jobmarket-v2-1/data/logs/cron.log"
mkdir -p "$(dirname "$LOG_FILE")"

# Fonction de log
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S'): FranceTravail $1" >> "$LOG_FILE"
}

log "Début de l'exécution du chargement des données dans Elasticsearch"

# Aller dans le dossier du projet
cd /home/ubuntu/jobmarket-v2-1 || {
    log "ERREUR: Impossible d'accéder au répertoire /home/ubuntu/jobmarket-v2-1"
    exit 1
}

# Vérifier que le conteneur francetravail est en cours d'exécution
if ! ./scripts/dc.sh ps | grep -q "francetravail.*Up"; then
    log "Le conteneur francetravail n'est pas en cours d'exécution. Tentative de démarrage..."
    ./scripts/dc.sh up -d francetravail
    sleep 10
fi

# Exécution du chargement
log "Lancement du script de chargement dans le conteneur"
if ./scripts/dc.sh exec -T francetravail python /app/ETL/Load/load_data_ft.py; then
    log "Chargement des données terminé avec succès"
else
    log "ERREUR: L'exécution du chargement a échoué"
    exit 1
fi 