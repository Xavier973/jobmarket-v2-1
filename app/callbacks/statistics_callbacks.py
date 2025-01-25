from dash.dependencies import Input, Output
from dash import no_update
import plotly.express as px
import pandas as pd
from app.utils.elastic_helpers import es, JOBMARKET_INDEX

def register_statistics_callbacks(app):
    @app.callback(
        [Output('graph-1-donut', 'figure'),
         Output('graph-1-postes', 'figure'),
         Output('graph-1-companies', 'figure'),
         Output('graph-1-locations', 'figure')],
        [Input('url', 'pathname'),
         Input('dropdown-postes', 'value'),
         Input('dropdown-companies', 'value'),
         Input('dropdown-nbrlocations', 'value'),
         Input('dropdown-locations', 'value')]
    )
    def update_statistics_graphs(pathname, n_postes, n_companies, n_locations, selected_location):
        if pathname != '/page-1':
            return no_update, no_update, no_update, no_update
        
        if es is None:
            return no_update, no_update, no_update, no_update

        try:
            # Requêtes Elasticsearch
            queries = {
                'postes': {
                    "size": 0,
                    "aggs": {
                        "titles_count": {
                            "terms": {
                                "field": "job_title.keyword",
                                "size": n_postes,
                                "order": {"_count": "desc"}
                            }
                        }
                    }
                },
                'sources': {
                    "size": 0,
                    "aggs": {
                        "sources_count": {
                            "terms": {
                                "field": "source",
                                "size": 10
                            }
                        }
                    }
                },
                'companies': {
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
                },
                'locations': {
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
            }

            # Ajout du filtre de localisation si sélectionné
            if selected_location:
                location_filter = {"query": {"match": {"location.keyword": selected_location}}}
                for query in queries.values():
                    query.update(location_filter)

            # Exécution des requêtes
            results = {
                name: es.search(index=JOBMARKET_INDEX, body=query)
                for name, query in queries.items()
            }

            # Création des graphiques
            # 1. Graphique en donut pour les sources
            source_data = pd.DataFrame([
                {'Source': bucket['key'], 'Nombre_Offres': bucket['doc_count']}
                for bucket in results['sources']['aggregations']['sources_count']['buckets']
            ])
            fig_sources = px.pie(
                source_data,
                names='Source',
                values='Nombre_Offres',
                title='Répartition des offres par source',
                hole=0.4,
                template='plotly_white'
            )
            fig_sources.update_traces(textinfo='percent+label')
            fig_sources.update_layout(
                showlegend=False,
                plot_bgcolor='white',
                paper_bgcolor='white',
                font={'family': 'Roboto, sans-serif'},
                title={'font': {'size': 16}}
            )

            # 2. Graphique en barres pour les postes
            postes_data = pd.DataFrame([
                {'Poste': bucket['key'][:30], 'Nombre_Offres': bucket['doc_count']}
                for bucket in results['postes']['aggregations']['titles_count']['buckets']
            ])
            fig_postes = px.bar(
                postes_data,
                x='Poste',
                y='Nombre_Offres',
                title='Nombre d\'offres par poste',
                template='plotly_white'
            )
            fig_postes.update_layout(
                xaxis_tickangle=-45,
                plot_bgcolor='white',
                paper_bgcolor='white',
                font={'family': 'Roboto, sans-serif'},
                title={'font': {'size': 16}},
                margin={'b': 100}
            )
            fig_postes.update_traces(marker_color='#2c5282')

            # 3. Graphique en barres pour les entreprises
            companies_data = pd.DataFrame([
                {'Entreprise': bucket['key'][:30], 'Nombre_Offres': bucket['doc_count']}
                for bucket in results['companies']['aggregations']['companies_count']['buckets']
            ])
            fig_companies = px.bar(
                companies_data,
                x='Entreprise',
                y='Nombre_Offres',
                title='Top entreprises qui recrutent',
                template='plotly_white'
            )
            fig_companies.update_layout(
                xaxis_tickangle=-45,
                plot_bgcolor='white',
                paper_bgcolor='white',
                font={'family': 'Roboto, sans-serif'},
                title={'font': {'size': 16}},
                margin={'b': 100}
            )
            fig_companies.update_traces(marker_color='#4299e1')

            # 4. Graphique en barres pour les localisations
            locations_data = pd.DataFrame([
                {'Location': bucket['key'], 'Nombre_Offres': bucket['doc_count']}
                for bucket in results['locations']['aggregations']['top_locations']['buckets']
            ])
            fig_locations = px.bar(
                locations_data,
                x='Location',
                y='Nombre_Offres',
                title='Répartition géographique des offres',
                template='plotly_white'
            )
            fig_locations.update_layout(
                xaxis_tickangle=-45,
                plot_bgcolor='white',
                paper_bgcolor='white',
                font={'family': 'Roboto, sans-serif'},
                title={'font': {'size': 16}},
                margin={'b': 100}
            )
            fig_locations.update_traces(marker_color='#48bb78')

            return fig_sources, fig_postes, fig_companies, fig_locations

        except Exception as e:
            print(f"Error in update_statistics_graphs: {e}")
            return no_update, no_update, no_update, no_update
