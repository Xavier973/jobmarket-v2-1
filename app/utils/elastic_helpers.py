from app.elastic import get_es_client, JOBMARKET_INDEX

es = get_es_client()

def get_location_options():
    query = {
        "size": 0,
        "aggs": {
            "locations": {
                "terms": {
                    "field": "location",
                    "size": 50
                }
            }
        }
    }
    res = es.search(index=JOBMARKET_INDEX, body=query)
    buckets = res['aggregations']['locations']['buckets']
    return [{'label': bucket['key'], 'value': bucket['key']} for bucket in buckets]

def get_title_options():
    query = {
        "size": 0,
        "aggs": {
            "postes": {
                "terms": {
                    "field": "job_title.keyword",
                    "size": 50
                }
            }
        }
    }
    res = es.search(index=JOBMARKET_INDEX, body=query)
    buckets = res['aggregations']['postes']['buckets']
    return [{'label': bucket['key'], 'value': bucket['key']} for bucket in buckets]