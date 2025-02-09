from dash import html
import dash_bootstrap_components as dbc
from components.header import create_header
from components.footer import create_footer
from components.graphs import create_jobs_distribution, create_department_map, create_contract_distribution

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
            
            # Row pour les deux premiers graphiques
            dbc.Row([
                # Graphique de répartition des jobs
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(
                            "Répartition des offres d'emploi par poste",
                            className="text-center",
                            style={'fontSize': '1.2rem', 'fontWeight': 'bold'}
                        ),
                        dbc.CardBody(create_jobs_distribution())
                    ], className="mb-4")
                ], md=6),
                
                # Graphique de répartition par type de contrat
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(
                            "Répartition par type de contrat",
                            className="text-center",
                            style={'fontSize': '1.2rem', 'fontWeight': 'bold'}
                        ),
                        dbc.CardBody(create_contract_distribution())
                    ], className="mb-4")
                ], md=6)
            ]),
            
            # Carte des départements
            dbc.Card([
                dbc.CardHeader(
                    "Distribution Géographique des Offres",
                    className="text-center",
                    style={'fontSize': '1.2rem', 'fontWeight': 'bold'}
                ),
                dbc.CardBody(create_department_map())
            ], className="mb-4")
            
        ], className="container"),
        create_footer()
    ]) 