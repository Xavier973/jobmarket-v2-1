# Utiliser une image officielle Python slim comme base
FROM python:3.9-slim

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Installer les dépendances système nécessaires
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copier uniquement requirements.txt d'abord (meilleur cache Docker)
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copier le contenu de l'application
COPY . .

# Variables d'environnement
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV ES_HOST=elasticsearch:9200

# Script d'initialisation
RUN chmod +x /app/init_es.sh

# Exposer le port pour dash
EXPOSE 8050

# Utiliser le script de démarrage
CMD ["/app/init_es.sh"]
