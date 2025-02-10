import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from Page.home import create_home_page
from Page.market import create_market_page
from Page.skills import create_skills_page
from Page.jobs import create_jobs_page

# Initialisation de l'application Dash
app = dash.Dash(
    __name__, 
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True
)

# Pour Gunicorn
server = app.server

# Layout principal avec un conteneur pour les pages
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

# Callback pour le routage des pages
@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)
def display_page(pathname):
    if pathname == '/market':
        return create_market_page()
    elif pathname == '/skills':
        return create_skills_page()
    elif pathname == '/jobs':
        return create_jobs_page()
    else:  # Page d'accueil par défaut
        return create_home_page()

# Exécution de l'application
if __name__ == "__main__":
    app.run_server(debug=True, host='0.0.0.0', port=8050)
