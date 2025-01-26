from dash import html, dcc
from app.utils.elastic_helpers import get_location_options

# Récupérer les options de localisation
location_options = get_location_options()

def create_statistics_layout():
    return html.Div([
        html.H2('Vue générale des données', style={'color': '#2c5282', 'textAlign': 'center'}),
        
        # En-tête avec bouton retour et dropdown
        html.Div([
            # Bouton retour
            html.Div([
                html.Button(
                    dcc.Link('Retour', href='/'), 
                    style={
                        'margin-bottom': '20px',
                        'padding': '8px 15px',
                        'backgroundColor': '#718096',
                        'color': 'white',
                        'border': 'none',
                        'borderRadius': '5px',
                        'cursor': 'pointer'
                    }
                )
            ], style={'display': 'flex', 'align-items': 'center'}),
            
            # Dropdown localisation
            html.Div([
                dcc.Dropdown(
                    id='dropdown-locations',
                    options=location_options,
                    value=None,
                    clearable=True,
                    placeholder='Sélectionner une localisation',
                    style={
                        'width': '300px',
                        'margin-bottom': '20px',
                        'backgroundColor': 'white'
                    }
                )
            ], style={'display': 'flex', 'justify-content': 'center', 'flex-grow': '1'})
        ], style={'display': 'flex', 'justify-content': 'space-between', 'align-items': 'center'}),

        # Première rangée de graphiques
        html.Div(style={'display': 'flex', 'justify-content': 'space-around'}, children=[
            # Graphique donut
            html.Div([
                dcc.Graph(id='graph-1-donut')
            ], style={'width': '48%', 'backgroundColor': 'white', 'padding': '15px', 'borderRadius': '8px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}),
            
            # Graphique locations
            html.Div([
                dcc.Dropdown(
                    id='dropdown-nbrlocations',
                    options=[{'label': str(i), 'value': i} for i in [5, 10, 15, 20]],
                    value=10,
                    clearable=False,
                    style={'width': '200px', 'margin-left': '15px'}
                ),
                dcc.Graph(id='graph-1-locations')
            ], style={'width': '48%', 'backgroundColor': 'white', 'padding': '15px', 'borderRadius': '8px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'})
        ]),

        # Deuxième rangée de graphiques
        html.Div(style={'display': 'flex', 'justify-content': 'space-around', 'marginTop': '20px'}, children=[
            # Graphique postes
            html.Div([
                dcc.Dropdown(
                    id='dropdown-postes',
                    options=[{'label': str(i), 'value': i} for i in [5, 10, 15, 20]],
                    value=10,
                    clearable=False,
                    style={'width': '200px'}
                ),
                dcc.Graph(id='graph-1-postes')
            ], style={'width': '48%', 'backgroundColor': 'white', 'padding': '15px', 'borderRadius': '8px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}),
            
            # Graphique entreprises
            html.Div([
                dcc.Dropdown(
                    id='dropdown-companies',
                    options=[{'label': str(i), 'value': i} for i in [5, 10, 15, 20]],
                    value=10,
                    clearable=False,
                    style={'width': '200px'}
                ),
                dcc.Graph(id='graph-1-companies')
            ], style={'width': '48%', 'backgroundColor': 'white', 'padding': '15px', 'borderRadius': '8px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'})
        ])
    ], style={'padding': '20px', 'backgroundColor': '#f7fafc'})