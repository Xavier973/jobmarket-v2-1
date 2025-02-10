from dash import html
import dash_bootstrap_components as dbc
from components.header import create_header
from components.footer import create_footer
from components.graphs import create_source_distribution, create_time_evolution

def create_home_page():
    return html.Div([
        create_header(),
        html.Div([
            html.Img(
                src='/assets/JobMarketLogo.png',
                style={
                    'height': '150px',
                    'marginBottom': '20px',
                    'display': 'block',
                    'marginLeft': 'auto',
                    'marginRight': 'auto'
                }
            ),
            html.H2(
                "Explorez les tendances et opportunités du marché de l'emploi dans les métiers de la data",
                className="text-center mb-4"
            ),
            html.P("Dernière mise à jour: ...", className="text-center"),
            
            # Conteneur pour les cartes avec les graphiques
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(
                            "Distribution des Sources d'Offres",
                            className="text-center",
                            style={'fontSize': '1.2rem', 'fontWeight': 'bold'}
                        ),
                        dbc.CardBody(create_source_distribution())
                    ], className="mb-4")
                ], md=6),
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader(
                            "Évolution Temporelle des Offres",
                            className="text-center",
                            style={'fontSize': '1.2rem', 'fontWeight': 'bold'}
                        ),
                        dbc.CardBody(create_time_evolution())
                    ], className="mb-4")
                ], md=6)
            ], className="mt-4")
        ], className="container"),
        create_footer()
    ])