from dash import dcc
import dash_bootstrap_components as dbc
from utils.es_queries import get_offers_by_source, get_offers_evolution, get_offers_by_job

# Couleurs communes pour tous les graphiques
COLORS = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']

def create_source_distribution():
    """Graphique de répartition des offres par source"""
    sources, counts = get_offers_by_source()
    
    return dcc.Graph(
        id="offres_par_source",
        figure={
            'data': [{
                'type': 'pie',
                'values': counts,
                'labels': sources,
                'hole': .4,
                'marker': {'colors': COLORS}
            }],
            'layout': {
                'height': 450,
                'margin': {'l': 30, 'r': 30, 't': 30, 'b': 30},
                'showlegend': True,
                'legend': {
                    'orientation': 'h',
                    'y': -0.1,
                    'x': 0.5,
                    'xanchor': 'center'
                }
            }
        },
        style={'height': '450px'}
    )

def create_time_evolution():
    """Graphique d'évolution des offres dans le temps"""
    dates, evolution_data = get_offers_evolution()
    
    evolution_traces = []
    for i, (source, values) in enumerate(evolution_data.items()):
        evolution_traces.append({
            'x': dates,
            'y': values,
            'type': 'scatter',
            'mode': 'lines+markers',
            'name': source,
            'line': {'color': COLORS[i % len(COLORS)]},
            'marker': {'size': 6}
        })
    
    return dcc.Graph(
        id="evolution_offres",
        figure={
            'data': evolution_traces,
            'layout': {
                'height': 450,
                'margin': {'l': 50, 'r': 30, 't': 30, 'b': 50},
                'xaxis': {
                    'title': 'Date',
                    'tickangle': -45
                },
                'yaxis': {
                    'title': 'Nombre d\'offres'
                },
                'legend': {
                    'orientation': 'h',
                    'y': -0.2,
                    'x': 0.5,
                    'xanchor': 'center'
                },
                'hovermode': 'x unified'
            }
        },
        style={'height': '450px'}
    )

def create_jobs_distribution():
    """Graphique de répartition des offres par type de poste"""
    jobs, counts = get_offers_by_job()
    
    return dcc.Graph(
        id="offres_par_job",
        figure={
            'data': [{
                'type': 'bar',
                'x': jobs,
                'y': counts,
                'marker': {'color': COLORS[0]}
            }],
            'layout': {
                'height': 450,
                'margin': {'l': 50, 'r': 30, 't': 30, 'b': 100},
                'xaxis': {
                    'title': 'Types de postes',
                    'tickangle': -45
                },
                'yaxis': {
                    'title': 'Nombre d\'offres'
                },
                'hovermode': 'x unified'
            }
        },
        style={'height': '450px'}
    )

# Fonction pour assembler les graphiques de la page d'accueil
def create_home_graphs():
    """Assemblage des graphiques pour la page d'accueil"""
    return dbc.Row([
        dbc.Col([create_source_distribution()], md=6),
        dbc.Col([create_time_evolution()], md=6)
    ])

# Vous pourrez ajouter d'autres fonctions pour les autres pages
def create_market_graphs():
    """Assemblage des graphiques pour la page marché"""
    pass

def create_skills_graphs():
    """Assemblage des graphiques pour la page compétences"""
    pass

def create_salaries_graphs():
    """Assemblage des graphiques pour la page salaires"""
    pass 