from dash import html
import dash_bootstrap_components as dbc
from components.header import create_header
from components.footer import create_footer
from components.graphs import create_jobs_distribution

def create_market_page():
    return html.Div([
        create_header(),
        html.Div([
            html.H2(
                "Marché de l'emploi des métiers de la data",
                className="text-center mb-4"
            ),
            html.P(
                "Découvrez les tendances actuelles du marché de l'emploi dans le domaine de la data",
                className="text-center mb-4"
            ),
            
            # Graphique de répartition des jobs
            dbc.Card([
                dbc.CardHeader(
                    "Répartition des Offres d'Emploi par Poste",
                    className="text-center",
                    style={'fontSize': '1.2rem', 'fontWeight': 'bold'}
                ),
                dbc.CardBody(create_jobs_distribution())
            ], className="mb-4")
            
            # Vous pourrez ajouter d'autres graphiques ici
            
        ], className="container"),
        create_footer()
    ]) 