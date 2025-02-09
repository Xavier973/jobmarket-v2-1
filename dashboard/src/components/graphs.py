from dash import dcc
import dash_bootstrap_components as dbc
from utils.es_queries import get_offers_by_source, get_offers_evolution, get_offers_by_job, get_offers_by_department, get_offers_by_contract, get_all_skills
import pandas as pd

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

def create_contract_distribution():
    """Graphique de répartition des offres par type de contrat"""
    contracts, counts = get_offers_by_contract()
    
    return dcc.Graph(
        id="offres_par_contrat",
        figure={
            'data': [{
                'type': 'pie',
                'values': counts,
                'labels': contracts,
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
    return dbc.Row([
        dbc.Col([create_wordcloud()], md=6),
        dbc.Col([create_source_distribution()], md=6)
    ])

def create_salaries_graphs():
    """Assemblage des graphiques pour la page salaires"""
    pass

def create_department_map():
    """Carte de France avec la distribution des offres par département"""
    from urllib.request import urlopen
    import json
    import plotly.express as px
    
    # Charger le GeoJSON des départements français
    with urlopen('https://france-geojson.gregoiredavid.fr/repo/departements.geojson') as response:
        departments_json = json.load(response)
    
    # Récupérer les données
    departments_data = get_offers_by_department()
    
    # Créer un DataFrame pour Plotly
    departments_list = []
    values_list = []
    for dept_code, value in departments_data.items():
        departments_list.append(dept_code)
        values_list.append(value)
    
    # Créer la carte
    fig = px.choropleth_mapbox(
        data_frame=pd.DataFrame({
            'department': departments_list,
            'count': values_list
        }),
        geojson=departments_json,
        locations='department',
        featureidkey='properties.code',
        color='count',
        color_continuous_scale='Viridis',
        mapbox_style='carto-positron',
        zoom=4.5,
        center={'lat': 46.8, 'lon': 2.3},  # Centre de la France
        opacity=0.7,
        labels={'count': 'Nombre d\'offres'}
    )
    
    fig.update_layout(
        height=600,
        margin={'r': 0, 'l': 0, 'b': 0, 't': 0}
    )
    
    return dcc.Graph(
        id='carte-departements',
        figure=fig,
        style={'height': '600px'}
    )

def create_wordcloud():
    """Création du nuage de mots des compétences"""
    import plotly.graph_objects as go
    from random import randint
    
    # Récupérer les données
    skills_count = get_all_skills()
    
    # Normaliser les tailles des mots (entre 15 et 50)
    max_count = max(skills_count.values())
    min_count = min(skills_count.values())
    
    def normalize_size(count):
        return 15 + ((count - min_count) * 35) / (max_count - min_count)
    
    # Créer les traces pour chaque mot
    words = list(skills_count.keys())
    counts = list(skills_count.values())
    
    # Générer des positions aléatoires pour chaque mot
    x_positions = [randint(-50, 50) for _ in words]
    y_positions = [randint(-50, 50) for _ in words]
    
    # Créer le graphique
    trace = go.Scatter(
        x=x_positions,
        y=y_positions,
        mode='text',
        text=words,
        hovertext=[f"{word}: {count} offres" for word, count in zip(words, counts)],
        hoverinfo='text',
        textfont={
            'size': [normalize_size(count) for count in counts],
            'color': [f'rgb({randint(0,255)}, {randint(0,255)}, {randint(0,255)})' for _ in words]
        }
    )
    
    layout = go.Layout(
        xaxis={'showgrid': False, 'showticklabels': False, 'zeroline': False},
        yaxis={'showgrid': False, 'showticklabels': False, 'zeroline': False},
        hovermode='closest',
        margin={'l': 10, 'r': 10, 't': 10, 'b': 10},
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    return dcc.Graph(
        id='wordcloud',
        figure={
            'data': [trace],
            'layout': layout
        },
        style={'height': '600px'}
    )

def create_skills_by_category(selected_job=None):
    """Création des graphiques de compétences par catégorie avec filtre optionnel"""
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    
    # Définition des catégories principales et leurs titres en français
    categories = {
        "ProgLanguage": "Langages de Programmation",
        "DataBase": "Bases de Données",
        "DataAnalytics": "Analyse de Données",
        "BigData": "Big Data",
        "MachineLearning": "Machine Learning",
        "CloudComputing": "Cloud Computing",
        "DevTools": "Outils de Développement",
        "Containers": "Conteneurisation",
        "Collaboration": "Collaboration",
        "EnSoftSkils": "Soft Skills"
    }
    
    # Récupérer les données avec le filtre
    result = get_all_skills(selected_job)
    
    # Créer un subplot pour chaque catégorie
    fig = make_subplots(
        rows=len(categories), 
        cols=1,
        subplot_titles=list(categories.values()),
        vertical_spacing=0.03
    )
    
    row = 1
    for category, title in categories.items():
        # Filtrer les compétences pour cette catégorie
        if category in result['aggregations']:
            skills_data = {
                bucket['key']: bucket['doc_count']
                for bucket in result['aggregations'][category]['buckets']
            }
            
            if skills_data:
                # Trier par nombre d'occurrences
                sorted_skills = dict(sorted(skills_data.items(), 
                                         key=lambda x: x[1], 
                                         reverse=True)[:10])
                
                fig.add_trace(
                    go.Bar(
                        x=list(sorted_skills.keys()),
                        y=list(sorted_skills.values()),
                        name=title,
                        hovertemplate="<b>%{x}</b><br>" +
                                    "Nombre d'offres: %{y}<br>" +
                                    "<extra></extra>",
                        marker_color='#1f77b4'
                    ),
                    row=row, 
                    col=1
                )
                
                # Personnaliser l'axe Y
                fig.update_yaxes(title_text="Nombre d'offres", row=row)
        
        row += 1
    
    # Créer le titre avec le filtre sélectionné
    title_suffix = f" pour {selected_job}" if selected_job and selected_job != 'all' else ""
    
    # Mise à jour du layout global
    fig.update_layout(
        height=250 * len(categories),
        showlegend=False,
        margin={'l': 50, 'r': 20, 't': 50, 'b': 20},
        title={
            'text': f"Top 10 des compétences les plus demandées{title_suffix}",
            'y': 0.99,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        }
    )
    
    # Rotation des labels sur l'axe X pour une meilleure lisibilité
    fig.update_xaxes(tickangle=45)
    
    return dcc.Graph(
        id='skills-by-category',
        figure=fig,
        style={'height': f'{250 * len(categories)}px'}
    )