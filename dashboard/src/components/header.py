from dash import html
import dash_bootstrap_components as dbc
from styles.styles import nav_link_style

def create_header():
    return dbc.NavbarSimple(
        brand="JobMarket Dashboard",
        brand_href="#",
        color="primary",
        dark=True,
        className="mb-3",
        style={'paddingLeft': '20px'},
        children=[
            dbc.Nav(
                [
                    dbc.NavItem(dbc.NavLink("Accueil", href="/", style=nav_link_style, className="nav-link-custom")),
                    dbc.NavItem(dbc.NavLink("Marché de l'emploi", href="/market", style=nav_link_style, className="nav-link-custom")),
                    dbc.NavItem(dbc.NavLink("Compétences", href="/competences", style=nav_link_style, className="nav-link-custom")),
                    dbc.NavItem(dbc.NavLink("Salaires", href="/salaires", style=nav_link_style, className="nav-link-custom")),
                    dbc.NavItem(dbc.NavLink("Offres d'emploi", href="/offres", style=nav_link_style, className="nav-link-custom")),
                ],
                className="mx-auto",
                navbar=True
            )
        ]
    ) 