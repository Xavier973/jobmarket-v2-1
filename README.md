# JobMarket-v2.1

Application d'analyse du marché de l'emploi en France, avec un pipeline ETL et un tableau de bord interactif.

## Architecture

Le projet est conteneurisé avec Docker et orchestré par Docker Compose. Il se compose des services suivants :

-   **`nginx`**: Serveur web Nginx agissant comme reverse proxy pour le tableau de bord.
-   **`elasticsearch`**: Base de données NoSQL pour le stockage et l'indexation des offres d'emploi.
-   **`dash`**: Application web construite avec Plotly Dash pour la visualisation des données.
-   **`francetravail`**: Conteneur de service pour exécuter les scripts ETL d'extraction, de transformation et de chargement des données.

## Prérequis

-   Docker
-   Docker Compose

## Installation et Lancement

1.  **Cloner le repository**

2.  **Configurer les variables d'environnement**
    Le projet utilise des fichiers de configuration d'environnement distincts pour `local` et `prod` (hebergé sur un VM). Copiez l'exemple fourni ou créez votre propre fichier `jobmarket-v2-1/config/env/.env.local`.

    Voici un exemple de contenu pour `config/env/.env.local`:

    ```bash
    # Configuration Elasticsearch
    ES_HEAP_SIZE=1g
    ES_MEMORY_LIMIT=1.5G
    ELASTIC_PASSWORD=your_super_secret_password
    ES_PORT=9200
    ES_HOST=elasticsearch
    ES_SECURITY_ENABLED=false

    # Configuration du Dashboard
    DASH_PORT=8050

    # Configuration Nginx
    NGINX_HTTP_PORT=80
    NGINX_HTTPS_PORT=443
    ENV=local # ou prod

    # Chemins des données (utilisés par les scripts ETL)
    DATA_RAW_DIR=/app/data/raw
    DATA_TRANSFORMED_DIR=/app/data/transformed
    DATA_PROCESSED_DIR=/app/data/processed
    DATA_LOG_DIR=/app/data/logs
    ```

3.  **Rendre les scripts exécutables**
    ```bash
    chmod +x scripts/deploy.sh scripts/dc.sh
    ```

4.  **Démarrer l'application**
    Le script `deploy.sh` gère le déploiement. Pour un environnement local :
    ```bash
    ./scripts/deploy.sh local
    ```
    Pour un environnement en production :
    ```bash
    ./scripts/deploy.sh prod
    ```

5.  **Initialiser l'index Elasticsearch**
    Une fois les conteneurs démarrés, exécutez le script d'initialisation. Le script `dc.sh` est un raccourci pour les commandes `docker-compose`.
    ```bash
    ./scripts/dc.sh exec francetravail python /app/Elasticsearch/src/init_es.py
    ```
    *Optionnel : Vous pouvez créer un alias `dc` dans votre `~/.bashrc` ou `~/.zshrc` pour un accès plus facile : `alias dc='~/jobmarket-v2-1/scripts/dc.sh'`*

6.  **Accéder au Dashboard**
    Le tableau de bord est accessible à l'adresse [http://localhost](http://localhost) (ou le port que vous avez configuré pour `NGINX_HTTP_PORT`).

## Utilisation de l'ETL

Les scripts ETL peuvent être exécutés manuellement pour un contrôle fin du processus, mais l'extraction des données de France Travail est automatisée via une tâche cron.

### Automatisation de l'extraction (Tâche Cron)

L'extraction et la transformation des données depuis France Travail est configurée pour s'exécuter automatiquement tous les jours à 4h du matin via une tâche cron sur la machine hôte.

**Script Cron :** `scripts/run_francetravail_scraper.sh`
Ce script gère :
- Le logging de l'exécution dans `data/logs/francetravail/cron.log`.
- La vérification que le conteneur `francetravail` est bien démarré.
- L'exécution du script de scraping `main.py` à l'intérieur du conteneur.

**Configuration de la crontab :**
Pour activer la tâche cron, ajoutez la ligne suivante à la crontab de l'utilisateur sur la machine hôte (via la commande `crontab -e`) :
```
# Exécution du scraper France Travail tous les jours à 4h du matin
0 4 * * * /home/ubuntu/jobmarket-v2-1/scripts/run_francetravail_scraper.sh
```
Le fichier `scripts/crontab.txt` contient cette configuration pour référence.

### Exécution manuelle

Les scripts ETL sont à exécuter manuellement depuis le conteneur `francetravail` en utilisant le script `dc.sh`.

#### 1. Extraction (Scraping)

Pour lancer le scraping des offres de France Travail :
```bash
./scripts/dc.sh exec francetravail python /app/ETL/Extract/FranceTravail/src/main.py
```
Les données brutes seront sauvegardées dans le dossier défini par `DATA_RAW_DIR`.

#### 2. Transformation

La transformation des données (`data_cleaning`) est lancée **automatiquement** à la fin de chaque session de scraping par le script d'extraction `main.py`.

Cependant, s'il est nécessaire de retraiter manuellement les fichiers, le script `data_cleaning_ft_manual.sh` peut être utilisé. Il parcourt tous les fichiers JSON du répertoire des données brutes et leur applique le script de transformation.

Pour lancer la transformation manuelle sur tous les fichiers de France Travail :
```bash
./scripts/dc.sh exec francetravail bash /app/ETL/Transform/data_cleaning_ft_manual.sh
```

#### 3. Chargement

Pour charger les données transformées dans Elasticsearch :
```bash
./scripts/dc.sh exec francetravail python /app/ETL/Load/load_data_container.py /app/data/transformed/francetravail/votre_fichier_updated.json
```


## Structure du Projet

```
.
├── config/             # Configuration
│   ├── docker/         # Fichiers docker-compose pour différents environnements
│   ├── env/            # Fichiers de variables d'environnement (.env.local, .env.prod)
│   └── nginx/          # Configuration Nginx (local, prod)
├── dashboard/          # Code source de l'application Dash
│   └── src/
│       ├── assets/
│       ├── components/
│       ├── Page/
│       └── utils/
├── data/               # Données (brutes, transformées, etc.)
│   ├── logs/           # Fichiers de log (scraping, cron)
│   ├── processed/      # Données prêtes pour analyse ou usage final
│   ├── raw/            # Données brutes extraites
│   └── transformed/    # Données nettoyées et transformées
├── docker-compose.yml  # Fichier d'orchestration Docker
├── Elasticsearch/      # Scripts liés à Elasticsearch
├── ETL/                # Scripts d'Extraction, Transformation, Chargement
│   ├── Extract/
│   ├── Load/
│   └── Transform/
├── scripts/            # Scripts utilitaires (déploiement, etc.)
├── Utils/              # Modules Python partagés
└── README.md           # Ce fichier
```