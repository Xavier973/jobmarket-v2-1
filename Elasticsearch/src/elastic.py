import os
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import ConnectionError
import time

print(f"Execution : {__file__}")
JOBMARKET_INDEX = "jobmarket"

def get_es_client():
    max_retries = 5
    retry_delay = 10  # secondes

    for attempt in range(max_retries):
        try:
            es_host = os.getenv("ES_HOST", "localhost:9200")
            es_username = os.getenv("ES_USERNAME", "elastic")
            es_password = os.getenv("ES_PASSWORD")

            if not es_password:
                print("Erreur: ES_PASSWORD n'est pas défini")
                return None

            es = Elasticsearch(
                hosts=[f"http://{es_host}"],
                basic_auth=(es_username, es_password),
                retry_on_timeout=True,
                timeout=30
            )
            # Test de connexion
            es.info()
            print(f"Connecté à Elasticsearch sur {es_host}")
            return es
        except ConnectionError as e:
            if attempt < max_retries - 1:
                print(f"Tentative {attempt + 1}/{max_retries} échouée. Nouvelle tentative dans {retry_delay} secondes...")
                time.sleep(retry_delay)
            else:
                print(f"Erreur de connexion à Elasticsearch: {e}")
                return None
        except Exception as e:
            print(f"Erreur inattendue: {e}")
            return None
