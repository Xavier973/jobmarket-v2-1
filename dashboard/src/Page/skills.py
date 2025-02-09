from dash import html, dcc, Input, Output
import dash_bootstrap_components as dbc
from components.header import create_header
from components.footer import create_footer
from components.graphs import create_skills_by_category
from utils.es_queries import get_offers_by_job

def create_skills_page():
    # Récupérer la liste des jobs pour le dropdown
    jobs, _ = get_offers_by_job()
    
    return html.Div([
        create_header(),
        html.Div([
            html.H2(
                "Compétences les plus recherchées",
                className="text-center mb-4"
            ),
            html.P(
                "Analyse détaillée des compétences demandées par catégorie",
                className="text-center mb-4"
            ),
            
            # Ajout du filtre
            dbc.Row([
                dbc.Col([
                    html.Label("Filtrer par type de poste:", className="mb-2"),
                    dcc.Dropdown(
                        id='job-filter',
                        options=[
                            {'label': 'Tous les postes', 'value': 'all'}
                        ] + [
                            {'label': job, 'value': job} for job in jobs
                        ],
                        value='all',
                        clearable=False,
                        className="mb-4"
                    )
                ], width={"size": 6, "offset": 3})
            ]),
            
            dbc.Card([
                dbc.CardHeader(
                    "Compétences par Catégorie",
                    className="text-center",
                    style={'fontSize': '1.2rem', 'fontWeight': 'bold'}
                ),
                dbc.CardBody(id='skills-content')
            ], className="mb-4")
            
        ], className="container"),
        create_footer()
    ]) 