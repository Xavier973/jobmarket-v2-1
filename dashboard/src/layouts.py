from dash import html, dcc
from dash import dash_table
from data import location_options, poste_options



# Définir les différents layouts
index_page = html.Div([
    # Logo avec taille ajustée
   html.Div(
    [
        html.Img(
            src='/assets/JobMarketLogo.png',
            style={
                'height': '150px',  # Taille augmentée
                'marginBottom': '20px',  # Espacement entre le logo et la phrase d'accroche
                'display': 'block'
            }
        ),
        html.P(
            "Explorez les tendances et opportunités du marché de l'emploi dans les métiers de la data.",
            style={
                'textAlign': 'center',
                'fontSize': '18px',
                'color': '#4a5568',  # Gris foncé
                'marginBottom': '30px',  # Espacement sous la phrase
                'fontFamily': 'Roboto, sans-serif',
                'maxWidth': '600px',  # Limite la largeur pour un meilleur rendu
                'lineHeight': '1.5'  # Meilleure lisibilité
            }
        )
    ],
    style={
        'display': 'flex',
        'flexDirection': 'column',
        'alignItems': 'center',
    }
   ),
    # Conteneur pour les boutons
    html.Div([
        html.Button(
            dcc.Link('Statistiques', href='/page-1'), 
            style={
                'width': '250px',
                'height': '50px',
                'margin': '10px',
                'padding': '0',
                'backgroundColor': '#2c5282',  # Bleu foncé
                'color': 'white',
                'border': 'none',
                'borderRadius': '8px',
                'cursor': 'pointer',
                'fontFamily': 'Roboto, sans-serif',
                'fontSize': '16px',
                'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
                'transition': 'all 0.3s ease',
                'textAlign': 'center',
                'display': 'flex',
                'justifyContent': 'center',
                'alignItems': 'center'
            }
        ),
        html.Br(),
        html.Button(
            dcc.Link('Compétences', href='/page-2'), 
            style={
                'width': '250px',
                'height': '50px',
                'margin': '10px',
                'padding': '0',
                'backgroundColor': '#2c5282',  # Bleu foncé
                'color': 'white',
                'border': 'none',
                'borderRadius': '8px',
                'cursor': 'pointer',
                'fontFamily': 'Roboto, sans-serif',
                'fontSize': '16px',
                'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
                'transition': 'all 0.3s ease',
                'textAlign': 'center',
                'display': 'flex',
                'justifyContent': 'center',
                'alignItems': 'center'
            }
        ),
        html.Br(),
        html.Button(
            dcc.Link('Offres d\'emplois', href='/page-3'), 
            style={
                'width': '250px',
                'height': '50px',
                'margin': '10px',
                'padding': '0',
                'backgroundColor': '#2c5282',  # Bleu foncé
                'color': 'white',
                'border': 'none',
                'borderRadius': '8px',
                'cursor': 'pointer',
                'fontFamily': 'Roboto, sans-serif',
                'fontSize': '16px',
                'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
                'transition': 'all 0.3s ease',
                'textAlign': 'center',
                'display': 'flex',
                'justifyContent': 'center',
                'alignItems': 'center'
            }
        )
    ], style={
        'display': 'flex',
        'flexDirection': 'column',
        'alignItems': 'center',
        'marginTop': '20px'
    }),
    # Crédits
    html.Div([
        html.P([
            'Réalisation : ',
            html.Span(
                'Xavier Cuniberti, Mohamed Gassama, Said Chachet', 
                style={
                    'fontStyle': 'italic',
                    'fontFamily': 'Roboto, sans-serif'
                }
            )
        ])
    ], style={
        'position': 'fixed',
        'bottom': '20px',
        'right': '20px',
        'fontSize': '14px',
        'color': '#4a5568',  # Gris foncé
        'backgroundColor': 'rgba(255,255,255,0.9)',
        'padding': '10px',
        'borderRadius': '5px',
        'boxShadow': '0 2px 4px rgba(0,0,0,0.05)'
    })
], style={
    'display': 'flex',
    'flexDirection': 'column',
    'alignItems': 'center',
    'minHeight': '100vh',
    'backgroundColor': '#f7fafc',  # Fond légèrement gris
    'padding': '20px',
    'paddingTop': '40px'  # Ajout d'un padding en haut pour l'espacement
})

layout_1 = html.Div([
    html.H2('Statistiques', style={'color': 'aquamarine', 'textAlign': 'center'}),
    html.Div([
        html.Div([
            #html.Button("Retour", id="button-retour-1", style={'margin-bottom': '20px', 'margin-right': 'auto', 'backgroundColor': 'lightgrey'})
            html.Button(dcc.Link('Retour', href='/'), style={'margin-bottom': '20px', 'margin-right': 'auto', 'backgroundColor': 'lightgrey'})
        ], style={'display': 'flex', 'align-items': 'center'}),
        html.Div([
            dcc.Dropdown(
                id='dropdown-locations',
                options=location_options,
                value=None,  # Valeur initiale par défaut
                clearable=True,
                placeholder='Sélectionner une localisation',
                style={'width': '300px', 'margin-bottom': '20px'}
            )
        ], style={'display': 'flex', 'justify-content': 'center', 'flex-grow': '1'}),
    ], style={'display': 'flex', 'justify-content': 'space-between', 'align-items': 'center'}),

    html.Div(style={'display': 'flex', 'justify-content': 'space-around'}, children=[
        html.Div([
            dcc.Graph(id='graph-1-donut')
        ], style={'width': '48%'}),
        html.Div([
            dcc.Dropdown(
                id='dropdown-nbrlocations',
                options=[
                    {'label': str(i), 'value': i} for i in [5, 10, 15, 20]
                ],
                value=10,
                clearable=False,
                style={'width': '200px', 'margin-left': '15px'}),
            dcc.Graph(id='graph-1-locations')
        ], style={'width': '48%'}),
    ]),
    html.Div(style={'display': 'flex', 'justify-content': 'space-around'}, children=[
        html.Div([
           dcc.Dropdown(
               id='dropdown-postes',
               options=[
                   {'label': str(i), 'value': i} for i in [5, 10, 15, 20]
                ],
                value=10,
                clearable=False,
                style={'width': '200px'}
            ),
            dcc.Graph(id='graph-1-postes')
        ], style={'width': '48%'}),
        html.Div([
            dcc.Dropdown(
                id='dropdown-companies',
                options=[
                    {'label': str(i), 'value': i} for i in [5, 10, 15, 20]
                ],
                value=10,
                clearable=False,
                style={'width': '200px'}
            ),
            dcc.Graph(id='graph-1-companies')
        ], style={'width': '48%'})
    ])
])

layout_2 = html.Div([
    html.H2('Compétences par poste', style={'color': 'aquamarine', 'textAlign': 'center'}),
    html.Div([
        html.Div([
            html.Button(dcc.Link('Retour', href='/'), style={'margin-bottom': '20px', 'margin-right': 'auto', 'backgroundColor': 'lightgrey'})
        ], style={'display': 'flex', 'align-items': 'center'}),
        html.Div([
            dcc.Dropdown(
                id='dropdown-2-postes',
                options=poste_options,
                value=None,  # Valeur initiale par défaut
                clearable=True,
                placeholder='Sélectionner un poste',
                style={'width': '300px', 'margin-bottom': '20px'}
            ),
            dcc.Dropdown(
                id='dropdown-2-locations',
                options=location_options,
                value=None,  # Valeur initiale par défaut
                clearable=True,
                placeholder='Sélectionner une localisation',
                style={'width': '300px', 'margin-bottom': '20px', 'margin-left': '20px'}
            )
        ], style={'display': 'flex', 'justify-content': 'center', 'flex-grow': '1'}),
    ], style={'display': 'flex', 'justify-content': 'space-between', 'align-items': 'center'}),

    html.Div([
        dash_table.DataTable(
            id='table-2-offres',
            columns=[
                {'name': 'Titre', 'id': 'title'},
                {'name': 'Entreprise', 'id': 'company'},
                {'name': 'Localisation', 'id': 'location'},
                {'name': 'Expériences', 'id': 'experiences'},
                {'name': 'Salaire', 'id': 'salary'},
                {'name': 'Lien', 'id': 'link', 'presentation': 'markdown'},
            ],
            data=[],
            style_table={'overflowX': 'auto'},
            style_cell={'textAlign': 'left'},
            page_size=10,
            page_action='native',
        )
    ], style={'margin-bottom': '20px', 'width': '90%', 'padding': '10px', 'margin-left': '10px'}),
    html.Div([
        dcc.Graph(id='graph-2-skills')
    ], style={'margin-bottom': '20px', 'width': '90%', 'padding': '10px', 'margin-left': '10px'})
])
