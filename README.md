# JobMarket — Data Job Market Analytics

## Aperçu
JobMarket V2.1 est une plateforme d’analyse du marché de l’emploi data en France. Elle automatise la collecte d’offres (France Travail), les transforme et les indexe dans Elasticsearch, puis expose un tableau de bord interactif (Dash) pour explorer les tendances, les compétences et les offres.

## Fonctionnalités clés
- Scraping France Travail avec Selenium (mode headless).
- Pipeline ETL : extraction → transformation → chargement dans Elasticsearch.
- Index Elasticsearch optimisé pour l’analyse des offres.
- Dashboard Dash avec graphiques, cartes et table des offres.
- Reverse‑proxy Nginx (HTTP/HTTPS) prêt pour local et prod.

## Architecture
- **Elasticsearch** : stockage et agrégation des offres.
- **Dash** : application web interactive (pages Accueil, Marché, Compétences, Offres).
- **Nginx** : proxy et terminaison SSL.
- **Scraper France Travail** : container dédié à la collecte.

## Stack technique
- Python 3.9
- Dash / Plotly / Dash Bootstrap Components
- Elasticsearch 8.x
- Selenium + Chromium
- Docker + Docker Compose
- Nginx

## Structure du projet
- dashboard/ : application Dash (UI, pages, composants).
- Elasticsearch/ : init de l’index et helpers ES.
- ETL/Extract/FranceTravail/ : scraper France Travail.
- ETL/Transform/ : nettoyage & transformations.
- ETL/Load/ : chargement des JSON transformés vers ES.
- config/nginx/ : configs Nginx local/prod.
- data/ : données brutes, transformées, traitées et logs.

## Prérequis
- Docker Desktop + Docker Compose
- Un volume Docker externe nommé **jobmarket_elasticsearch_data**
- (Optionnel) Certificats SSL dans config/nginx/ssl

## Configuration
Les variables d’environnement principales (exemple dans un fichier .env à la racine) :
- ES_SECURITY_ENABLED=true
- ELASTIC_PASSWORD=VotreMotDePasse
- ES_HEAP_SIZE=1g
- ES_MEMORY_LIMIT=1.5G
- ES_PORT=9200
- DASH_PORT=8050
- NGINX_HTTP_PORT=80
- NGINX_HTTPS_PORT=443
- ENV=local

## Démarrage rapide
1. Créer le volume Elasticsearch :
   - docker volume create jobmarket_elasticsearch_data
2. Démarrer les services :
   - docker compose up -d --build
3. Accéder au dashboard :
   - http://localhost:8050 (ou via Nginx : http://localhost)

## Lancer le scraping France Travail
Le service francetravail est lancé en mode « attente ». Pour exécuter un scraping :
- Exécution standard (filtre “1 jour”) :
  - docker compose exec francetravail python /app/ETL/Extract/FranceTravail/src/main.py
- Exécution complète (sans filtre de date) :
  - docker compose exec francetravail python /app/ETL/Extract/FranceTravail/src/main.py --all

Les données sont stockées dans :
- data/raw/francetravail/
- data/transformed/francetravail/
- data/processed/francetravail/
- data/logs/francetravail/

## Charger les données dans Elasticsearch
Après transformation, charger les JSON vers ES :
- docker compose exec francetravail python /app/ETL/Load/load_data_container.py

## Planifier l’exécution automatique
Un exemple de planification est fourni dans [scripts/crontab.txt](scripts/crontab.txt). Par défaut, il exécute le scraper tous les jours à 04:00 :

- 0 4 * * * /home/ubuntu/jobmarket-v2-1/scripts/run_francetravail_scraper.sh

Le script [scripts/run_francetravail_scraper.sh](scripts/run_francetravail_scraper.sh) :
- démarre le conteneur si nécessaire ;
- lance le scraping ;
- écrit les logs dans data/logs/francetravail/cron.log.

Adaptez le chemin (/home/ubuntu/...) à votre serveur.

## Pages du dashboard
- Accueil : sources et évolution temporelle
- Marché : répartition par poste, contrat, et carte par département
- Compétences : nuage de mots des compétences
- Offres : table filtrable des offres

## Remarques
- L’index ES est initialisé au démarrage du service Dash via Elasticsearch/init_es.sh.
- Le mapping Elasticsearch est défini dans Elasticsearch/src/init_es.py.
- En local, si SSL n’est pas configuré, utiliser ENV=local pour la config Nginx.

## Licence
Projet interne / usage privé.