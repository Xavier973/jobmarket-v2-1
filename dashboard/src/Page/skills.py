from dash import html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc
from components.header import create_header
from components.footer import create_footer
from components.graphs import create_wordcloud
from utils.es_queries import get_offers_by_job

def create_skills_page():
    # Récupérer la liste des métiers pour le menu déroulant
    jobs, _ = get_offers_by_job()
    
    return html.Div([
        create_header(),
        html.Div([
            html.H2(
                "Compétences les plus recherchées",
                className="text-center mb-4"
            ),
            html.P(
                "Découvrez les compétences les plus demandées dans le domaine de la data",
                className="text-center mb-4"
            ),
            
            dbc.Card([
                dbc.CardHeader([
                    html.H5("Nuage de mots des compétences", className="text-center"),
                    dcc.Dropdown(
                        id='job-filter',
                        options=[{'label': 'Tous les métiers', 'value': None}] + 
                                [{'label': job, 'value': job} for job in jobs],
                        value=None,
                        clearable=False,
                        className="mb-3"
                    )
                ]),
                dbc.CardBody(
                    html.Div(id='wordcloud-container')
                )
            ], className="mb-4")
            
        ], className="container"),
        create_footer()
    ])

@callback(
    Output('wordcloud-container', 'children'),
    Input('job-filter', 'value')
)
def update_wordcloud(selected_job):
    return create_wordcloud(selected_job)