from elasticsearch import Elasticsearch
import json
import os

# Configuration
es_host = os.getenv('ES_HOST', 'elasticsearch:9200')
es_password = os.getenv('ES_PASSWORD', 'JobMarket2024Secure!')

# Création du client
es = Elasticsearch(
    [f'http://{es_host}'],
    basic_auth=('elastic', es_password),
    verify_certs=False
)

# Récupération du mapping
try:
    mapping = es.indices.get_mapping(index='jobmarket')
    # Convertir la réponse en dictionnaire
    mapping_dict = mapping.body
    print(json.dumps(mapping_dict, indent=2))
except Exception as e:
    print(f"Erreur: {str(e)}") 