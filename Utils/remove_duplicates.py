from elasticsearch import Elasticsearch
from collections import defaultdict
from datetime import datetime

def get_es_client():
    return Elasticsearch(['http://elasticsearch:9200'])

def parse_date(date_str):
    try:
        return datetime.strptime(date_str, '%Y-%m-%d')
    except:
        return datetime.min

def remove_duplicates():
    es = get_es_client()
    
    # Requête pour récupérer tous les documents
    query = {
        "size": 10000,
        "query": {
            "match_all": {}
        }
    }
    
    try:
        # Exécuter la requête
        response = es.search(index="jobmarket", body=query)
        hits = response['hits']['hits']
        
        # Dictionnaires pour stocker les documents par lien
        jobs_by_link = defaultdict(list)
        
        # Parcourir tous les documents
        for hit in hits:
            doc = hit['_source']
            doc_id = hit['_id']
            
            if 'link' in doc:
                jobs_by_link[doc['link']].append({
                    'id': doc_id,
                    'job_title': doc.get('job_title', 'Non spécifié'),
                    'company': doc.get('company', 'Non spécifié'),
                    'publication_date': doc.get('publication_date', 'Non spécifié'),
                    'source': doc
                })
        
        # Compter les documents à supprimer
        docs_to_delete = []
        
        # Pour chaque groupe de doublons
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
                        es.delete(index="jobmarket", id=doc_id)
                        print(f"Document supprimé: {doc_id}")
                    except Exception as e:
                        print(f"Erreur lors de la suppression du document {doc_id}: {e}")
                
                print(f"\nSuppression terminée. {len(docs_to_delete)} documents supprimés.")
            else:
                print("Opération annulée.")
        else:
            print("Aucun doublon trouvé.")
        
    except Exception as e:
        print(f"Erreur lors du traitement: {e}")

if __name__ == "__main__":
    print("Suppression des doublons dans l'index Elasticsearch")
    print("ATTENTION: Cette opération est irréversible!")
    remove_duplicates() 