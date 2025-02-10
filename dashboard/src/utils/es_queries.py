from elasticsearch import Elasticsearch

def get_es_client():
    return Elasticsearch(['http://elasticsearch:9200'])

def get_offers_by_source():
    es = get_es_client()
    
    # Agrégation pour compter les offres par source
    query = {
        "size": 0,
        "aggs": {
            "sources": {
                "terms": {
                    "field": "source",
                    "size": 10
                }
            }
        }
    }
    
    result = es.search(index="jobmarket", body=query)
    
    sources = []
    counts = []
    
    # Extraction des données
    for bucket in result['aggregations']['sources']['buckets']:
        sources.append(bucket['key'])
        counts.append(bucket['doc_count'])
        
    return sources, counts 

def get_offers_evolution():
    es = get_es_client()
    
    query = {
        "size": 0,
        "aggs": {
            "evolution": {
                "date_histogram": {
                    "field": "publication_date",
                    "calendar_interval": "week"
                },
                "aggs": {
                    "by_source": {
                        "terms": {
                            "field": "source"
                        }
                    }
                }
            }
        }
    }
    
    result = es.search(index="jobmarket", body=query)
    
    # Préparation des données pour le graphique
    dates = []
    data_by_source = {}
    
    for bucket in result['aggregations']['evolution']['buckets']:
        dates.append(bucket['key_as_string'][:10])  # Format YYYY-MM-DD
        
        # Initialiser les compteurs pour chaque source
        for source_bucket in bucket['by_source']['buckets']:
            source = source_bucket['key']
            if source not in data_by_source:
                data_by_source[source] = []
            
    # Remplir les données
    for bucket in result['aggregations']['evolution']['buckets']:
        sources_in_bucket = {sb['key']: sb['doc_count'] 
                           for sb in bucket['by_source']['buckets']}
        
        for source in data_by_source.keys():
            count = sources_in_bucket.get(source, 0)
            data_by_source[source].append(count)
    
    return dates, data_by_source 

def get_offers_by_job():
    """Récupère la répartition des offres par type de poste"""
    es = get_es_client()
    try:
        result = es.search(
            index="jobmarket",
            body={
                "size": 0,
                "aggs": {
                    "jobs": {
                        "terms": {
                            "field": "job",
                            "size": 10  # Top 10 des postes les plus demandés
                        }
                    }
                }
            }
        )
        
        jobs = []
        counts = []
        for bucket in result['aggregations']['jobs']['buckets']:
            jobs.append(bucket['key'])
            counts.append(bucket['doc_count'])
            
        return jobs, counts
        
    except Exception as e:
        print(f"Erreur lors de la récupération des offres par job: {e}")
        return [], [] 

def get_offers_by_department():
    """Récupère la répartition des offres par département"""
    es = get_es_client()
    try:
        result = es.search(
            index="jobmarket",
            body={
                "size": 0,
                "aggs": {
                    "departments": {
                        "terms": {
                            "field": "location",
                            "size": 100  # Pour avoir tous les départements
                        }
                    }
                }
            }
        )
        
        departments = {}
        for bucket in result['aggregations']['departments']['buckets']:
            dept_code = bucket['key']
            count = bucket['doc_count']
            departments[str(dept_code)] = count
            
        return departments
        
    except Exception as e:
        print(f"Erreur lors de la récupération des offres par département: {e}")
        return {} 

def get_offers_by_contract():
    """Récupère la répartition des offres par type de contrat"""
    es = get_es_client()
    try:
        result = es.search(
            index="jobmarket",
            body={
                "size": 0,
                "aggs": {
                    "contracts": {
                        "terms": {
                            "field": "contract_type",
                            "size": 10
                        }
                    }
                }
            }
        )
        
        contracts = []
        counts = []
        for bucket in result['aggregations']['contracts']['buckets']:
            contracts.append(bucket['key'])
            counts.append(bucket['doc_count'])
            
        return contracts, counts
        
    except Exception as e:
        print(f"Erreur lors de la récupération des offres par contrat: {e}")
        return [], [] 

def get_all_skills(job_filter=None):
    """Récupère toutes les compétences et leurs fréquences avec filtre optionnel par métier"""
    es = get_es_client()
    skills_categories = [
        "ProgLanguage", "DataBase", "DataAnalytics", "BigData", 
        "MachineLearning", "DataSerialization", "DataVisualisation",
        "Statistics", "CloudComputing", "DevTools", "OS", "DBMS",
        "SoftBigDataProcessing", "Automation", "InfrastructureAsCode",
        "NetworkSecurty", "Virtualisation", "Containers", "Collaboration",
        "Other", "EnSoftSkils"
    ]
    
    try:
        # Construire la requête avec filtre optionnel
        query = {
            "size": 0,
            "query": {
                "match_all": {}
            } if job_filter is None else {
                "term": {
                    "job": job_filter
                }
            },
            "aggs": {
                category: {
                    "terms": {
                        "field": f"skills.{category}",
                        "size": 25
                    }
                } for category in skills_categories
            }
        }
        
        result = es.search(index="jobmarket", body=query)
        
        # Le reste de la fonction reste identique
        skills_count = {}
        for category in skills_categories:
            if category in result['aggregations']:
                for bucket in result['aggregations'][category]['buckets']:
                    skill = bucket['key']
                    count = bucket['doc_count']
                    skills_count[skill] = skills_count.get(skill, 0) + count
        
        return skills_count
        
    except Exception as e:
        print(f"Erreur lors de la récupération des compétences: {e}")
        return {}