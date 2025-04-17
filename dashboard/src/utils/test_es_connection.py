from es_queries import get_es_client

def test_connection():
    try:
        # Tentative de connexion
        es = get_es_client()
        info = es.info()
        print("✅ Connexion à Elasticsearch réussie!")
        print(f"Version: {info['version']['number']}")
        print(f"Cluster: {info['cluster_name']}")
        
        # Test d'une requête simple
        try:
            count = es.count(index="jobmarket")
            print(f"✅ Nombre total de documents dans l'index jobmarket: {count['count']}")
        except Exception as e:
            print(f"❌ Erreur lors de la requête sur l'index: {str(e)}")
            
    except Exception as e:
        print(f"❌ Erreur de connexion: {str(e)}")

if __name__ == "__main__":
    test_connection() 