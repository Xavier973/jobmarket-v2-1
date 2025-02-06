# Scraping France Travail
FROM python:3.9-slim

# Installation des dépendances système nécessaires
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    chromium \
    chromium-driver \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

# Création et définition du répertoire de travail
WORKDIR /app

# Copie des fichiers nécessaires
COPY src/ ./src/
COPY requirements.txt .

# Installation des dépendances Python
RUN pip install --no-cache-dir -r requirements.txt


# Définition des variables d'environnement
ENV PYTHONUNBUFFERED=1
ENV DISPLAY=:99
ENV CHROME_BIN=/usr/bin/chromium
ENV ES_HOST=elasticsearch:9200
ENV PYTHONPATH=/app

# Script de démarrage
COPY start.sh /start.sh
RUN chmod +x /start.sh

ENTRYPOINT ["/start.sh"]
# CMD ["--all"]



