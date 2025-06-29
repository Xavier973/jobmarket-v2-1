import json
import glob
import os
from elasticsearch import Elasticsearch
import shutil

# Configuration pour le conteneur
ES_HOST = os.getenv('ES_HOST', 'elasticsearch:9200')
ES_PASSWORD = os.getenv('ES_PASSWORD', 'JobMarket2024Secure!')
JOBMARKET_INDEX = "jobmarket"
# DATA_PATH = "/app/data/transformed/francetravail/*.json"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__)) 
BASE_PATH = os.path.dirname(os.path.dirname(SCRIPT_DIR))
DATA_PROCESSED_FOLDER = os.path.join(BASE_PATH, "data", "processed", "francetravail")
DATA_TRANSFORM_FOLDER = os.path.join(BASE_PATH, "data", "transformed", "francetravail")

def get_es_client():
    try:
        print(f"Tentative de connexion à Elasticsearch sur {ES_HOST}")
        print(f"Authentification activée: {'Oui' if ES_PASSWORD else 'Non'}")
        
        # Configuration de base
        es_config = {
            'hosts': [f'http://{ES_HOST}'],
            'retry_on_timeout': True,
            'request_timeout': 30,
            'verify_certs': False,
            'basic_auth': ('elastic', ES_PASSWORD)
        }
        
        es = Elasticsearch(**es_config)
        
        # Test de connexion plus détaillé
        try:
            if es.ping():
                print(f"✅ Connecté à Elasticsearch sur {ES_HOST}")
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

def load_json_files():
    es = get_es_client()
    if not es:
        return
    
    # Compteurs pour le suivi
    total_docs = 0
    success_docs = 0
    
    # Parcourir tous les fichiers JSON
    for file_path in glob.glob(os.path.join(DATA_TRANSFORM_FOLDER, "*.json")):
        try:
            print(f"\nTraitement du fichier : {os.path.basename(file_path)}")
            
            # Lire le fichier JSON
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                
                file_processed_successfully = True  # Flag pour suivre le succès du traitement
                
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
                            file_processed_successfully = False
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
                        file_processed_successfully = False
                
                # Déplacer le fichier si le traitement est réussi
                if file_processed_successfully:
                    try:
                        filename = os.path.basename(file_path)
                        destination = os.path.join(DATA_PROCESSED_FOLDER, filename)
                        os.makedirs(DATA_PROCESSED_FOLDER, exist_ok=True)
                        shutil.move(file_path, destination)
                        print(f"Fichier déplacé vers : {destination}")
                    except Exception as e:
                        print(f"Erreur lors du déplacement du fichier : {e}")
                    
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
