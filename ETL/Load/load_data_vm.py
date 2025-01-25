import json
import glob
import os
from elasticsearch import Elasticsearch

# Configuration pour la VM
ES_HOST = "localhost:9200"
JOBMARKET_INDEX = "jobmarket"
DATA_PATH = "/home/ubuntu/JobmarketV2/ETL/data/*.json"

def get_es_client():
    try:
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

def load_json_files():
    es = get_es_client()
    if not es:
        return
    
    # Compteurs pour le suivi
    total_docs = 0
    success_docs = 0
    
    # Parcourir tous les fichiers JSON
    for file_path in glob.glob(DATA_PATH):
        try:
            print(f"\nTraitement du fichier : {os.path.basename(file_path)}")
            
            # Lire le fichier JSON
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                
                # Si le fichier contient une liste
                if isinstance(data, list):
                    print(f"Fichier contenant {len(data)} documents")
                    for doc in data:
                        total_docs += 1
                        try:
                            response = es.index(index=JOBMARKET_INDEX, document=doc)
                            if response['result'] == 'created':
                                success_docs += 1
                            if total_docs % 100 == 0:  # Log tous les 100 documents
                                print(f"Progression : {success_docs}/{total_docs}")
                        except Exception as e:
                            print(f"Erreur lors de l'indexation du document {total_docs}: {e}")
                else:
                    # Si le fichier contient un seul document
                    total_docs += 1
                    try:
                        response = es.index(index=JOBMARKET_INDEX, document=data)
                        if response['result'] == 'created':
                            success_docs += 1
                            print("Document unique indexé avec succès")
                    except Exception as e:
                        print(f"Erreur lors de l'indexation du document: {e}")
                    
        except Exception as e:
            print(f"Erreur lors du traitement du fichier {file_path}: {e}")
    
    print(f"\nChargement terminé : {success_docs}/{total_docs} documents indexés")
    
    # Forcer le rafraîchissement de l'index
    es.indices.refresh(index=JOBMARKET_INDEX)
    
    # Afficher le nombre total de documents dans l'index
    try:
        count = es.count(index=JOBMARKET_INDEX)
        print(f"Nombre total de documents dans l'index : {count['count']}")
    except Exception as e:
        print(f"Erreur lors du comptage des documents : {e}")

if __name__ == "__main__":
    load_json_files()
