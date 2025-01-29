from dash.dependencies import Input, Output
from dash import no_update
import pandas as pd
import plotly.express as px
from app.utils.elastic_helpers import es, JOBMARKET_INDEX

def register_skills_callbacks(app):
    @app.callback(
        Output('table-2-offres', 'data'),
        [Input('url', 'pathname'),
         Input('dropdown-2-postes', 'value'),
         Input('dropdown-2-locations', 'value')]
    )
    def update_table(pathname, selected_poste, selected_location):
        if pathname == '/page-2':
            if es is None:
                return no_update

            if not selected_poste:
                return []

            # Construction de la requête Elasticsearch
            query = {
                "query": {
                    "bool": {
                        "must": []
                    }
                }
            }

            # Ajout des filtres
            if selected_poste:
                query['query']['bool']['must'].append({"match": {"job_title": selected_poste}})

            if selected_location:
                query['query']['bool']['must'].append({"match": {"location": selected_location}})

            # Exécution de la requête
            try:
                res = es.search(index=JOBMARKET_INDEX, body=query, size=3000)
                offres = res['hits']['hits']
                table_data = []
                
                for offre in offres:
                    source = offre['_source']
                    details = source.get('details', {})

                    # Traitement des expériences et salaires
                    experiences = details.get('Experience', source.get('Experience', []))
                    salary = details.get('Salary', source.get('Salary', []))

                    # Conversion en liste si nécessaire
                    if not isinstance(experiences, list):
                        experiences = [experiences]
                    if not isinstance(salary, list):
                        salary = [salary]

                    # Filtrage des valeurs None
                    experiences = [exp for exp in experiences if exp is not None]
                    salary = [sal for sal in salary if sal is not None]

                    # Formatage du lien
                    link = source.get('link', '')
                    if link:
                        link = f"[Lien]({link})"

                    # Construction de l'entrée pour la table
                    table_data.append({
                        'id': offre['_id'],
                        'title': source.get('job_title', ''),
                        'company': source.get('company', ''),
                        'location': source.get('location', ''),
                        'experiences': ', '.join(experiences) if experiences else '',
                        'salary': ', '.join(salary) if salary else '',
                        'link': link
                    })

                return table_data

            except Exception as e:
                print(f"Error in update_table: {e}")
                return []

        return no_update

    @app.callback(
        Output('graph-2-skills', 'figure'),
        [Input('table-2-offres', 'active_cell'),
         Input('table-2-offres', 'data')]
    )
    def update_skills_graph(active_cell, data):
        if not active_cell or not data:
            return {}

        try:
            # Récupération de l'offre sélectionnée
            row = active_cell['row']
            offer_id = data[row]['id']

            # Requête Elasticsearch pour obtenir les compétences
            query = {
                "query": {
                    "match": {
                        "_id": offer_id
                    }
                }
            }

            res = es.search(index=JOBMARKET_INDEX, body=query)
            offre = res['hits']['hits'][0]
            skills_data = offre['_source'].get('skills', {})

            # Préparation des données pour le graphique
            skills = []
            frequencies = []
            for category, skills_list in skills_data.items():
                for skill in skills_list:
                    skills.append(skill)
                    frequencies.append(1)

            df = pd.DataFrame({'Compétences': skills, 'Fréquence': frequencies})

            # Création du graphique
            fig = px.bar(
                df,
                x='Compétences',
                y='Fréquence',
                title=f"Compétences requises pour le poste : {offre['_source'].get('job_title', '')}",
                template='plotly_white'
            )

            # Personnalisation du graphique
            fig.update_layout(
                plot_bgcolor='white',
                paper_bgcolor='white',
                font={'family': 'Roboto, sans-serif'},
                title={'font': {'size': 16}},
                margin={'t': 50, 'l': 50, 'r': 30, 'b': 50}
            )

            fig.update_traces(
                marker_color='#2c5282',
                hovertemplate='Compétence: %{x}<br>Fréquence: %{y}<extra></extra>'
            )

            return fig

        except Exception as e:
            print(f"Error in update_skills_graph: {e}")
            return {}
