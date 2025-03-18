from elasticsearch import Elasticsearch
from collections import defaultdict

def get_es_client():
    return Elasticsearch(['http://elasticsearch:9200'])

def detect_duplicates():
    es = get_es_client()
    
    # Requête pour récupérer tous les documents
    query = {
        "size": 10000,  # Ajustez selon la taille de votre index
        "query": {
            "match_all": {}
        }
    }
    
    try:
        # Exécuter la requête
        response = es.search(index="jobmarket", body=query)
        hits = response['hits']['hits']
        
        # Dictionnaires pour stocker les potentiels doublons
        jobs_by_title = defaultdict(list)
        jobs_by_link = defaultdict(list)
        
        # Parcourir tous les documents
        for hit in hits:
            doc = hit['_source']
            doc_id = hit['_id']
            
            # Regrouper par titre
            if 'job_title' in doc:
                jobs_by_title[doc['job_title']].append({
                    'id': doc_id,
                    'link': doc.get('link', 'Non spécifié'),
                    'company': doc.get('company', 'Non spécifié'),
                    'publication_date': doc.get('publication_date', 'Non spécifié')
                })
            
            # Regrouper par lien
            if 'link' in doc:
                jobs_by_link[doc['link']].append({
                    'id': doc_id,
                    'job_title': doc.get('job_title', 'Non spécifié'),
                    'company': doc.get('company', 'Non spécifié'),
                    'publication_date': doc.get('publication_date', 'Non spécifié')
                })
        
        # Afficher les doublons par titre
        print("\n=== Doublons par titre ===")
        for title, jobs in jobs_by_title.items():
            if len(jobs) > 1:
                print(f"\nTitre: {title}")
                print(f"Nombre d'occurrences: {len(jobs)}")
                for job in jobs:
                    print(f"- ID: {job['id']}")
                    print(f"  Lien: {job['link']}")
                    print(f"  Entreprise: {job['company']}")
                    print(f"  Date de publication: {job['publication_date']}")
                print("-" * 50)
        
        # Afficher les doublons par lien
        print("\n=== Doublons par lien ===")
        for link, jobs in jobs_by_link.items():
            if len(jobs) > 1:
                print(f"\nLien: {link}")
                print(f"Nombre d'occurrences: {len(jobs)}")
                for job in jobs:
                    print(f"- ID: {job['id']}")
                    print(f"  Titre: {job['job_title']}")
                    print(f"  Entreprise: {job['company']}")
                    print(f"  Date de publication: {job['publication_date']}")
                print("-" * 50)
        
        # Afficher les statistiques
        print("\n=== Statistiques ===")
        print(f"Nombre total de documents: {len(hits)}")
        duplicate_titles = sum(1 for jobs in jobs_by_title.values() if len(jobs) > 1)
        duplicate_links = sum(1 for jobs in jobs_by_link.values() if len(jobs) > 1)
        print(f"Nombre de titres avec doublons: {duplicate_titles}")
        print(f"Nombre de liens avec doublons: {duplicate_links}")
        
    except Exception as e:
        print(f"Erreur lors de la détection des doublons: {e}")

if __name__ == "__main__":
    print("=================================================")
    print("Détection des doublons dans l'index Elasticsearch")
    print("=================================================")
    print("---> Détection par titre et lien")
    detect_duplicates() 