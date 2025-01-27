from dash import Dash, html, dcc
from layouts import index_page, layout_1, layout_2
from callbacks import register_callbacks

# Initialisation de l'application Dash
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = Dash(__name__, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True)
server = app.server

# Configuration du layout principal avec le système de routage
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

# Enregistrement des callbacks
register_callbacks(app)

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=5000)
