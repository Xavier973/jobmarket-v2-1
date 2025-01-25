# Modifier la configuration en haut du fichier
ES_HOST = "elasticsearch:9200"  # Si vous exécutez depuis le conteneur
# OU
ES_HOST = "localhost:9200"      # Si vous exécutez depuis la VM

def get_es_client():
    try:
        # Ajout de retry_on_timeout et timeout
        es = Elasticsearch(
            [f"http://{ES_HOST}"],
            retry_on_timeout=True,
            timeout=30
        )
        if es.ping():
            print(f"Connecté à Elasticsearch sur {ES_HOST}")
            return es
        else:
            print("Impossible de se connecter à Elasticsearch")
            return None
    except Exception as e:
        print(f"Erreur de connexion : {e}")
        return None
