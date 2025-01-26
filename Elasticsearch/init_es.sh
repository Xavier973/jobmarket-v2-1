#!/bin/bash

# Attendre que Elasticsearch soit prêt
echo "Attente d'Elasticsearch..."
while ! curl -s http://elasticsearch:9200 > /dev/null; do
    sleep 1
done

# Initialiser l'index
python /app/Elasticsearch/src/init_es.py

# Démarrer l'application
cd /app/dashboard/src
exec gunicorn --bind 0.0.0.0:8050 main:server
