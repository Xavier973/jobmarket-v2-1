import os
from elasticsearch import Elasticsearch
from collections import defaultdict

def get_es_client():
    ES_HOST = os.getenv('ES_HOST', 'elasticsearch:9200')
    ES_PASSWORD = os.getenv('ES_PASSWORD', 'JobMarket2024Secure!')
    return Elasticsearch(
        [f'http://{ES_HOST}'],
        basic_auth=('elastic', ES_PASSWORD),
        verify_certs=False
    )

def detect_duplicates():
    es = get_es_client()
    index_name = "jobmarket"
    scroll = '2m'
    size = 1000  # Nombre de documents par page

    # Dictionnaires pour stocker les potentiels doublons
    jobs_by_title = defaultdict(list)
    jobs_by_link = defaultdict(list)
    total_docs = 0

    # Première requête avec scroll
    response = es.search(
        index=index_name,
        body={"query": {"match_all": {}}},
        scroll=scroll,
        size=size
    )
    scroll_id = response['_scroll_id']
    hits = response['hits']['hits']

    while hits:
        for hit in hits:
            doc = hit['_source']
            doc_id = hit['_id']
            total_docs += 1

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

        # Page suivante
        response = es.scroll(scroll_id=scroll_id, scroll=scroll)
        scroll_id = response['_scroll_id']
        hits = response['hits']['hits']

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
    print(f"Nombre total de documents: {total_docs}")
    duplicate_titles = sum(1 for jobs in jobs_by_title.values() if len(jobs) > 1)
    duplicate_links = sum(1 for jobs in jobs_by_link.values() if len(jobs) > 1)
    print(f"Nombre de titres avec doublons: {duplicate_titles}")
    print(f"Nombre de liens avec doublons: {duplicate_links}")

if __name__ == "__main__":
    print("=================================================")
    print("Détection des doublons dans l'index Elasticsearch")
    print("=================================================")
    print("---> Détection par titre et lien")
    detect_duplicates() 