import os
from elasticsearch import Elasticsearch

ES_HOST = os.getenv('ES_HOST', 'elasticsearch:9200')
ELASTIC_PASSWORD = os.getenv('ELASTIC_PASSWORD')
JOBMARKET_INDEX = "jobmarket"

def get_es_client(host=None, password=None):
    host = host or ES_HOST
    password = password if password is not None else ELASTIC_PASSWORD
    try:
        print(f"Tentative de connexion à Elasticsearch sur {host}")
        print(f"Authentification activée: {'Oui' if password else 'Non'}")
        es_config = {
            'hosts': [f'http://{host}'],
            'retry_on_timeout': True,
            'request_timeout': 30,
            'verify_certs': False,
            'basic_auth': ('elastic', password)
        }
        es = Elasticsearch(**es_config)
        try:
            if es.ping():
                print(f"✅ Connecté à Elasticsearch sur {host}")
                info = es.info()
                print(f"Version: {info['version']['number']}")
                print(f"Cluster: {info['cluster_name']}")
                return es
            else:
                print("❌ Impossible de se connecter à Elasticsearch - Le ping a échoué")
                return None
        except Exception as e:
            print(f"❌ Erreur lors du ping: {str(e)}")
            return None
    except Exception as e:
        print(f"❌ Erreur de connexion à Elasticsearch: {str(e)}")
        return None

if __name__ == "__main__":
    es = get_es_client()
    if es:
        print("Connexion réussie et client prêt à l'emploi.")
    else:
        print("Échec de la connexion à Elasticsearch.") 