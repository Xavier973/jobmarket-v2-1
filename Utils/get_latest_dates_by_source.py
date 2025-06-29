import os
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import ConnectionError
from es_connection import get_es_client

ES_HOST = os.getenv('ES_HOST', 'localhost:9200')
ES_USER = os.getenv('ES_USER', 'elastic')
ES_PASSWORD = os.getenv('ELASTIC_PASSWORD', '')
ES_INDEX = 'jobmarket'


def get_latest_dates_by_source():
    es = get_es_client()
    if es is None:
        print("Erreur de connexion à Elasticsearch.")
        return None
    try:
        # Agrégation pour obtenir la date la plus récente par source
        body = {
            "size": 0,
            "aggs": {
                "sources": {
                    "terms": {"field": "source", "size": 20},
                    "aggs": {
                        "latest_date": {"max": {"field": "publication_date"}}
                    }
                }
            }
        }
        resp = es.search(index=ES_INDEX, body=body)
        results = {}
        for bucket in resp['aggregations']['sources']['buckets']:
            source = bucket['key']
            latest_date = bucket['latest_date']['value_as_string'] if bucket['latest_date']['value_as_string'] else None
            results[source] = latest_date
        return results
    except Exception as e:
        print(f"Erreur: {e}")
        return None

if __name__ == "__main__":
    latest_dates = get_latest_dates_by_source()
    if latest_dates:
        print("Dates les plus récentes par source :")
        for source, date in latest_dates.items():
            print(f"{source}: {date}")
    else:
        print("Aucune donnée trouvée ou erreur.") 