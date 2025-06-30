#!/bin/bash

# Configuration du logging
LOG_FILE="/home/xadmin/projets/jobmarket-v2-1/data/logs/cron.log"
mkdir -p "$(dirname "$LOG_FILE")"

# Fonction de logging
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S'): $1" >> "$LOG_FILE"
}

log "Début de l'exécution du scraper Welcome To The Jungle"

# Vérification du répertoire
cd /home/xadmin/projets/jobmarket-v2-1 || {
    log "ERREUR: Impossible d'accéder au répertoire /home/xadmin/projets/jobmarket-v2-1"
    exit 1
}

# Vérification que le conteneur welcometothejungle est en cours d'exécution
if ! ./scripts/dc.sh ps | grep -q "wttj.*Up"; then
    log "Le conteneur welcometothejungle n'est pas en cours d'exécution. Tentative de démarrage..."
    ./scripts/dc.sh up -d welcometothejungle
    sleep 10  # Attendre que le conteneur soit prêt
fi

# Exécution du script Python
log "Lancement du script Python dans le conteneur"
if ./scripts/dc.sh exec -T wttj python /app/ETL/Extract/WelcomeToTheJungle/main.py; then
    log "Exécution du scraper Welcome To The Jungle terminée avec succès"
else
    log "ERREUR: L'exécution du script a échoué"
    exit 1
fi 