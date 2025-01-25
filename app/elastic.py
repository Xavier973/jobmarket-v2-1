import os
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import ConnectionError
import time

JOBMARKET_INDEX = "jobmarket"

def get_es_client():
    max_retries = 5
    retry_delay = 10  # secondes

    for attempt in range(max_retries):
        try:
            es_host = os.getenv("ES_HOST", "localhost:9200")
            es = Elasticsearch(
                hosts=[f"http://{es_host}"],
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
