from dash import html, dcc, dash_table
from app.utils.elastic_helpers import get_location_options, get_title_options

# Récupérer les options
location_options = get_location_options()
poste_options = get_title_options()

def create_skills_layout():
    return html.Div([
        html.H2('Compétences par poste', 
                style={
                    'color': '#2c5282', 
                    'textAlign': 'center',
                    'marginBottom': '30px',
                    'fontFamily': 'Roboto, sans-serif'
                }),
        
        # En-tête avec bouton retour et dropdowns
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
            
            # Dropdowns
            html.Div([
                dcc.Dropdown(
                    id='dropdown-2-postes',
                    options=poste_options,
                    value=None,
                    clearable=True,
                    placeholder='Sélectionner un poste',
                    style={
                        'width': '300px',
                        'marginBottom': '20px',
                        'backgroundColor': 'white'
                    }
                ),
                dcc.Dropdown(
                    id='dropdown-2-locations',
                    options=location_options,
                    value=None,
                    clearable=True,
                    placeholder='Sélectionner une localisation',
                    style={
                        'width': '300px',
                        'marginBottom': '20px',
                        'marginLeft': '20px',
                        'backgroundColor': 'white'
                    }
                )
            ], style={'display': 'flex', 'justify-content': 'center', 'flex-grow': '1'})
        ], style={'display': 'flex', 'justify-content': 'space-between', 'align-items': 'center'}),

        # Table des offres
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
                style_table={
                    'overflowX': 'auto'
                },
                style_cell={
                    'textAlign': 'left',
                    'padding': '10px',
                    'fontFamily': 'Roboto, sans-serif'
                },
                style_header={
                    'backgroundColor': '#2c5282',
                    'color': 'white',
                    'fontWeight': 'bold'
                },
                style_data={
                    'backgroundColor': 'white',
                    'color': '#2d3748'
                },
                style_data_conditional=[
                    {
                        'if': {'row_index': 'odd'},
                        'backgroundColor': '#f7fafc'
                    }
                ],
                page_size=10,
                page_action='native',
            )
        ], style={
            'marginBottom': '20px',
            'width': '95%',
            'margin': '20px auto',
            'backgroundColor': 'white',
            'padding': '20px',
            'borderRadius': '8px',
            'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
        }),

        # Graphique des compétences
        html.Div([
            dcc.Graph(id='graph-2-skills')
        ], style={
            'marginBottom': '20px',
            'width': '95%',
            'margin': '20px auto',
            'backgroundColor': 'white',
            'padding': '20px',
            'borderRadius': '8px',
            'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
        })
    ], style={
        'padding': '20px',
        'backgroundColor': '#f7fafc',
        'minHeight': '100vh'
    })