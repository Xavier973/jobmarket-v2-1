from Elasticsearch.src.elastic import get_es_client, JOBMARKET_INDEX
import sys
import plotly.express as px
import pandas as pd
import dash

es = get_es_client()

# Test connection to Elasticsearch
try:
    if es:
        es.info()
        print("Connected to Elasticsearch")
    else:
        print("Failed to create Elasticsearch client")
except Exception as e:
    print(f"Error connecting to Elasticsearch: {e}")
    sys.exit(1)

# Fonction pour obtenir la liste des localisations
def get_location_options():
    query = {
        "size": 0,
        "aggs": {
            "locations": {
                "terms": {
                    "field": "location",
                    "size": 50  # Limiter le nombre de localisations
                }
            }
        }
    }
    res = es.search(index=JOBMARKET_INDEX, body=query)
    buckets = res['aggregations']['locations']['buckets']
    return [{'label': bucket['key'], 'value': bucket['key']} for bucket in buckets]

location_options = get_location_options()

# Fonction pour obtenir la liste des postes
def get_title_options():
    query = {
        "size": 0,
        "aggs": {
            "postes": {
                "terms": {
                    "field": "job.keyword",
                    "size": 50
                }
            }
        }
    }
    res = es.search(index=JOBMARKET_INDEX, body=query)
    buckets = res['aggregations']['postes']['buckets']
    return [{'label': bucket['key'], 'value': bucket['key']} for bucket in buckets]

# Liste des options pour le dropdown des postes
poste_options = get_title_options()

def debug_location_data(location="Paris"):
    # Requête simple pour voir les documents
    query = {
        "query": {
            "match_phrase": {
                "location": location
            }
        },
        "size": 1  # Juste pour voir un exemple
    }
    
    try:
        result = es.search(index=JOBMARKET_INDEX, body=query)
        print(f"Nombre total de résultats pour {location}: {result['hits']['total']['value']}")
        if result['hits']['hits']:
            print("Exemple de document:")
            print(result['hits']['hits'][0]['_source'])
        else:
            print(f"Aucun résultat trouvé pour {location}")
    except Exception as e:
        print(f"Erreur lors de la requête: {e}")

def get_data_for_graph_1(n_postes, n_companies, n_locations, selected_location):
    print(f"\n=== DEBUG ===")
    print(f"Fonction appelée avec les paramètres:")
    print(f"n_postes: {n_postes}")
    print(f"n_companies: {n_companies}")
    print(f"n_locations: {n_locations}")
    print(f"selected_location: {selected_location}")
    
    if selected_location:
        print(f"\nDébogage de la localisation: {selected_location}")
        debug_location_data(selected_location)
        
        # Affichons aussi la requête
        location_filter = {
            "bool": {
                "must": [
                    {"match_phrase": {"location": selected_location}}
                ]
            }
        }
        print(f"\nRequête utilisée:")
        print(location_filter)
    
    if es is None:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update

    # Requête pour les postes
    query_postes = {
        "size": 0,
        "aggs": {
            "titles_count": {
                "terms": {
                    "field": "title.keyword",
                    "size": n_postes,
                    "order": {"_count": "desc"}
                }
            }
        }
    }

    # Requête pour les sources
    query_sources = {
        "size": 0,
        "aggs": {
            "sources_count": {
                "terms": {
                    "field": "source",
                    "size": 10
                }
            }
        }
    }

    # Requête pour les entreprises
    query_companies = {
        "size": 0,
        "aggs": {
            "companies_count": {
                "terms": {
                    "field": "company",
                    "size": n_companies,
                    "order": {"_count": "desc"}
                }
            }
        }
    }

    # Requête pour les localisations
    query_locations = {
        "size": 0,
        "aggs": {
            "top_locations": {
                "terms": {
                    "field": "location",
                    "size": n_locations
                }
            }
        }
    }

    # Ajouter le filtre de localisation si nécessaire
    if selected_location:
        location_filter = {
            "bool": {
                "must": [
                    {"match_phrase": {"location": selected_location}}
                ]
            }
        }
        for query in [query_postes, query_sources, query_companies, query_locations]:
            query['query'] = location_filter

    try:
        res_postes = es.search(index=JOBMARKET_INDEX, body=query_postes)
        res_sources = es.search(index=JOBMARKET_INDEX, body=query_sources)
        res_companies = es.search(index=JOBMARKET_INDEX, body=query_companies)
        res_locations = es.search(index=JOBMARKET_INDEX, body=query_locations)
        
        print("\nRésultats des requêtes:")
        print(f"Nombre de postes: {len(res_postes['aggregations']['titles_count']['buckets'])}")
        print(f"Nombre de sources: {len(res_sources['aggregations']['sources_count']['buckets'])}")
        print(f"Nombre d'entreprises: {len(res_companies['aggregations']['companies_count']['buckets'])}")
        print(f"Nombre de localisations: {len(res_locations['aggregations']['top_locations']['buckets'])}")
        
    except Exception as e:
        print(f"Error executing search queries: {e}")
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update

    # Création du graphique donut (sources)
    buckets_sources = res_sources['aggregations']['sources_count']['buckets']
    df_sources = pd.DataFrame({
        'Source': [bucket['key'][:20] for bucket in buckets_sources],
        'Nombre_Offres': [bucket['doc_count'] for bucket in buckets_sources]
    })
    total_sources_offers = df_sources['Nombre_Offres'].sum()
    fig_sources = px.pie(df_sources, names='Source', values='Nombre_Offres', 
                        title='Répartition des offres par source de données')
    fig_sources.update_traces(hole=0.4)
    fig_sources.update_layout(
        annotations=[dict(
            text=f"Total des offres: {total_sources_offers}",
            showarrow=False,
            font=dict(size=14),
            x=0.5,
            y=-0.1,
            xref='paper',
            yref='paper'
        )]
    )

    # Création du graphique nombre d'offres par poste
    buckets_postes = res_postes['aggregations']['titles_count']['buckets']
    if not buckets_postes:  # Si aucun résultat
        print("Aucun poste trouvé pour cette requête")
        fig_postes = px.bar(
            pd.DataFrame({'Poste': [], 'Nombre_Offres': []}),
            x='Poste', 
            y='Nombre_Offres',
            title='Nombre d\'offres par poste'
        )
    else:
        df_postes = pd.DataFrame({
            'Poste': [bucket['key'][:20] for bucket in buckets_postes],
            'Nombre_Offres': [bucket['doc_count'] for bucket in buckets_postes]
        })
        total_offers = sum(bucket['doc_count'] for bucket in buckets_postes)
        fig_postes = px.bar(df_postes, x='Poste', y='Nombre_Offres', 
                           title='Nombre d\'offres par poste')
        fig_postes.update_layout(
            xaxis_tickangle=-45,
            annotations=[dict(
                x=1, y=1,
                text=f'Total des offres: {total_offers}',
                showarrow=False,
                xref='paper', yref='paper',
                font=dict(size=14, color='red'),
                align='right',
                xanchor='right',
                yanchor='top'
            )]
        )

    # Création du graphique companies
    buckets_companies = res_companies['aggregations']['companies_count']['buckets']
    df_companies = pd.DataFrame({
        'Entreprise': [bucket['key'][:20] for bucket in buckets_companies],
        'Nombre_Offres': [bucket['doc_count'] for bucket in buckets_companies]
    })
    fig_companies = px.bar(df_companies, x='Entreprise', y='Nombre_Offres',
                          title='Top 10 des entreprises qui recrutent le plus')
    fig_companies.update_layout(xaxis_tickangle=-45)

    # Création du graphique locations
    buckets_locations = res_locations['aggregations']['top_locations']['buckets']
    df_locations = pd.DataFrame({
        'Location': [loc['key'][:20] for loc in buckets_locations],
        'Nombre_Offres': [loc['doc_count'] for loc in buckets_locations]
    })
    df_locations = df_locations[df_locations['Nombre_Offres'] > 0]
    df_locations = df_locations.sort_values(by='Nombre_Offres', ascending=False)
    fig_locations = px.bar(df_locations, x='Location', y='Nombre_Offres',
                          title='Répartition géographique des offres d\'emploi',
                          color_discrete_sequence=['green'])
    fig_locations.update_layout(xaxis_tickangle=-45)

    return fig_sources, fig_postes, fig_companies, fig_locations

def get_data_for_table_2(pathname, selected_poste):
    # Déplacer la logique de création du tableau depuis main.old.py
    pass

def get_graph_data_for_companies(n_companies, selected_location):
    # Déplacer la logique correspondante depuis main.old.py
    pass

def get_graph_data_for_locations(n_locations, selected_location):
    # Déplacer la logique correspondante depuis main.old.py
    pass

def get_skills_graph_data(active_cell, data):
    # Déplacer la logique correspondante depuis main.old.py
    pass