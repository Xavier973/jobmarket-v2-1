from elastic import get_es_client, JOBMARKET_INDEX
from Elasticsearch.src.elastic import get_es_client, JOBMARKET_INDEX

def create_index():
    es = get_es_client()
    
    # Vérifier si l'index existe déjà
    if not es.indices.exists(index=JOBMARKET_INDEX):
        # Définition du mapping pour l'index
        mapping = {
            "mappings": {
                "properties": {
                    "source": {"type": "keyword"},
                    "job_title": {"type": "text"},
                    "job": {"type": "keyword"},
                    "contract_type": {"type": "keyword"},
                    "salary": {"type": "keyword"},
                    "company": {"type": "keyword"},
                    "location": {"type": "keyword"},
                    "remote": {"type": "keyword"},
                    "experience": {"type": "keyword"},
                    "education_level": {"type": "keyword"},
                    "publication_date": {"type": "date"},
                    "company_data": {
                        "properties": {
                            "sector": {"type": "keyword"},
                            "company_size": {"type": "keyword"},
                            "creation_date": {"type": "keyword"},
                            "address": {"type": "keyword"},
                            "average_age_of_employees": {"type": "keyword"},
                            "turnover_in_millions": {"type": "keyword"},
                            "proportion_female": {"type": "keyword"},
                            "proportion_male": {"type": "keyword"}
                        }
                    },
                    "skills": {
                        "properties": {
                            "ProgLanguage": {"type": "keyword"},
                            "DataBase": {"type": "keyword"},
                            "DataAnalytics": {"type": "keyword"},
                            "BigData": {"type": "keyword"},
                            "MachineLearning": {"type": "keyword"},
                            "DataSerialization": {"type": "keyword"},
                            "DataVisualisation": {"type": "keyword"},
                            "Statistics": {"type": "keyword"},
                            "CloudComputing": {"type": "keyword"},
                            "DevTools": {"type": "keyword"},
                            "OS": {"type": "keyword"},
                            "DBMS": {"type": "keyword"},
                            "SoftBigDataProcessing": {"type": "keyword"},
                            "Automation": {"type": "keyword"},
                            "InfrastructureAsCode": {"type": "keyword"},
                            "NetworkSecurty": {"type": "keyword"},
                            "Virtualisation": {"type": "keyword"},
                            "Containers": {"type": "keyword"},
                            "Collaboration": {"type": "keyword"},
                            "Other": {"type": "keyword"},
                            "EnSoftSkils": {"type": "keyword"}
                        }
                    },
                    "link": {"type": "keyword"},
                    "description": {"type": "text"}
                }
            }
        }
        
        # Créer l'index seulement s'il n'existe pas
        es.indices.create(index=JOBMARKET_INDEX, body=mapping)
        print(f"Index {JOBMARKET_INDEX} créé avec succès")
    else:
        print(f"Index {JOBMARKET_INDEX} existe déjà")

if __name__ == "__main__":
    print(f"Execution : {__file__}")
    create_index()
