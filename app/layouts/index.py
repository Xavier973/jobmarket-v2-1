from dash import html, dcc

def create_index_layout():
    return html.Div([
        # Logo avec taille ajustée
        html.Img(
            src='/assets/JobMarketLogo.png',
            style={
                'height': '150px',  # Taille augmentée
                'margin': '40px auto',  # Plus d'espace autour
                'display': 'block'
            }
        ),
        # Container pour les boutons
        html.Div([
            html.Button(
                dcc.Link('Statistiques', href='/page-1'), 
                style={
                    'width': '250px',
                    'margin': '10px',
                    'padding': '12px 20px',
                    'backgroundColor': '#2c5282',  # Bleu foncé
                    'color': 'white',
                    'border': 'none',
                    'borderRadius': '8px',
                    'cursor': 'pointer',
                    'fontFamily': 'Roboto, sans-serif',
                    'fontSize': '16px',
                    'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
                    'transition': 'all 0.3s ease'
                }
            ),
            html.Br(),
            html.Button(
                dcc.Link('Compétences', href='/page-2'), 
                style={
                    'width': '250px',
                    'margin': '10px',
                    'padding': '12px 20px',
                    'backgroundColor': '#2c5282',  # Bleu foncé
                    'color': 'white',
                    'border': 'none',
                    'borderRadius': '8px',
                    'cursor': 'pointer',
                    'fontFamily': 'Roboto, sans-serif',
                    'fontSize': '16px',
                    'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
                    'transition': 'all 0.3s ease'
                }
            )
        ], style={
            'textAlign': 'center',
            'marginTop': '20px'
        }),
        
        # Crédits avec style amélioré
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
        'alignItems': 'center',
        'minHeight': '100vh',
        'backgroundColor': '#f7fafc',  # Fond légèrement gris
        'padding': '20px'
    })