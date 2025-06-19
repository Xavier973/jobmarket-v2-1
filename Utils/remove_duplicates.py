import os
from elasticsearch import Elasticsearch
from collections import defaultdict
from datetime import datetime

def get_es_client():
    ES_HOST = os.getenv('ES_HOST', 'elasticsearch:9200')
    ES_PASSWORD = os.getenv('ES_PASSWORD', 'JobMarket2024Secure!')
    return Elasticsearch(
        [f'http://{ES_HOST}'],
        basic_auth=('elastic', ES_PASSWORD),
        verify_certs=False
    )

def parse_date(date_str):
    try:
        return datetime.strptime(date_str, '%Y-%m-%d')
    except:
        return datetime.min

def remove_duplicates():
    es = get_es_client()
    index_name = "jobmarket"
    scroll = '2m'
    size = 1000  # Nombre de documents par page

    # Dictionnaire pour stocker les documents par lien
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
            if 'link' in doc:
                jobs_by_link[doc['link']].append({
                    'id': doc_id,
                    'job_title': doc.get('job_title', 'Non spécifié'),
                    'company': doc.get('company', 'Non spécifié'),
                    'publication_date': doc.get('publication_date', 'Non spécifié'),
                    'source': doc
                })
        # Page suivante
        response = es.scroll(scroll_id=scroll_id, scroll=scroll)
        scroll_id = response['_scroll_id']
        hits = response['hits']['hits']

    # Compter les documents à supprimer
    docs_to_delete = []

    # Pour chaque groupe de doublons par lien
    for link, jobs in jobs_by_link.items():
        if len(jobs) > 1:
            print(f"\nDoublons trouvés pour le lien: {link}")
            print(f"Nombre d'occurrences: {len(jobs)}")
            # Trier les jobs par date de publication (le plus récent d'abord)
            sorted_jobs = sorted(jobs, 
                              key=lambda x: parse_date(x['publication_date']), 
                              reverse=True)
            # Garder le premier (le plus récent) et marquer les autres pour suppression
            keep_job = sorted_jobs[0]
            print(f"\nConservation de:")
            print(f"- ID: {keep_job['id']}")
            print(f"- Titre: {keep_job['job_title']}")
            print(f"- Date: {keep_job['publication_date']}")
            print("\nSuppression de:")
            for job in sorted_jobs[1:]:
                print(f"- ID: {job['id']}")
                print(f"- Titre: {job['job_title']}")
                print(f"- Date: {job['publication_date']}")
                docs_to_delete.append(job['id'])
            print("-" * 50)

    # Demander confirmation avant suppression
    if docs_to_delete:
        print(f"\nNombre total de documents à supprimer: {len(docs_to_delete)}")
        confirmation = input("Voulez-vous procéder à la suppression ? (oui/non): ")
        if confirmation.lower() == 'oui':
            # Supprimer les documents
            for doc_id in docs_to_delete:
                try:
                    es.delete(index=index_name, id=doc_id)
                    print(f"Document supprimé: {doc_id}")
                except Exception as e:
                    print(f"Erreur lors de la suppression du document {doc_id}: {e}")
            print(f"\nSuppression terminée. {len(docs_to_delete)} documents supprimés.")
        else:
            print("Opération annulée.")
    else:
        print("Aucun doublon trouvé.")

if __name__ == "__main__":
    print("Suppression des doublons dans l'index Elasticsearch")
    print("ATTENTION: Cette opération est irréversible!")
    remove_duplicates() 