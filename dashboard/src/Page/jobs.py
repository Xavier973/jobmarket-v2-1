import dash_bootstrap_components as dbc
from dash import html, dash_table
from components.header import create_header
from components.footer import create_footer
from utils.es_queries import get_es_client

def get_job_offers():
    es = get_es_client()
    
    query = {
        "size": 10000,  # Limite à 1000 résultats
        "_source": ["source", "ft_reference", "publication_date", "job", 
                   "job_title", "contract_type", "location", "link", 
                   "company", "Remote", "experience", "education_level",
                   "salary"]
    }
    
    result = es.search(index="jobmarket", body=query)
    
    # Conversion des résultats en liste de dictionnaires
    offers = []
    for hit in result['hits']['hits']:
        offer = hit['_source']
        # Création d'un lien markdown avec une icône
        link_md = f"[![Lien]({'https://img.icons8.com/material-outlined/24/external-link.png'})]({offer.get('link', '')})" if offer.get('link') else ""
        
        offers.append({
            'Source': offer.get('source', ''),
            'Référence': offer.get('ft_reference', ''),
            'Date de publication': offer.get('publication_date', '')[:10],  # Format YYYY-MM-DD
            'Métier': offer.get('job', ''),
            'Intitulé': offer.get('job_title', ''),
            'Contrat': offer.get('contract_type', ''),
            'Lieu': offer.get('location', ''),
            'Recruteur': offer.get('company', ''),
            'Teletravail': offer.get('Remote', ''),
            'Experience': offer.get('experience', ''),
            'Niveau d\'étude': offer.get('education_level', ''),
            'Salaire': offer.get('salary', ''),
            'Lien': link_md
        })
    
    return offers

def create_jobs_page():
    offers = get_job_offers()
    
    return html.Div([
        create_header(),
        html.Div([
            html.H2(
                "Offres d'emploi dans la Data",
                className="text-center mb-4"
            ),
            html.P(
                "Explorez les offres d'emploi actuellement disponibles dans le domaine de la data",
                className="text-center mb-4"
            ),
            
            dbc.Card([
                dbc.CardBody([
                    dash_table.DataTable(
                        id='jobs-table',
                        columns=[
                            {'name': 'Source', 'id': 'Source'},
                            {'name': 'Date de publication', 'id': 'Date de publication'},
                            {'name': 'Métier', 'id': 'Métier'},
                            {'name': 'Intitulé', 'id': 'Intitulé'},
                            {'name': 'Contrat', 'id': 'Contrat'},
                            {'name': 'Lieu', 'id': 'Lieu'},
                            {'name': 'Recruteur', 'id': 'Recruteur'},
                            {'name': 'Télétravail', 'id': 'Teletravail'},
                            {'name': 'Expérience', 'id': 'Experience'},
                            {'name': 'Niveau d\'étude', 'id': 'Niveau d\'étude'},
                            {'name': 'Salaire', 'id': 'Salaire'},
                            {'name': 'Lien', 'id': 'Lien', 'presentation': 'markdown'},
                            {'name': 'Référence', 'id': 'Référence'}
                        ],
                        data=offers,
                        style_table={'overflowX': 'auto'},
                        style_cell={
                            'textAlign': 'left',
                            'padding': '10px',
                            'whiteSpace': 'normal',
                            'height': 'auto',
                        },
                        style_cell_conditional=[
                            {
                                'if': {'column_id': 'Lien'},
                                'width': '55px',
                                'maxWidth': '55px',
                                'minWidth': '55px',
                                'textAlign': 'center'
                            },
                            {
                                'if': {'column_id': 'Niveau d\'étude'},
                                'width': '100px',
                                'maxWidth': '100px',
                                'minWidth': '100px'
                            },
                            {
                                'if': {'column_id': 'Salaire'},
                                'width': '120px',
                                'maxWidth': '120px',
                                'minWidth': '120px'
                            }
                        ],
                        style_header={
                            'backgroundColor': 'rgb(230, 230, 230)',
                            'fontWeight': 'bold'
                        },
                        page_size=15,
                        filter_action="native",
                        sort_action="native",
                        sort_mode="multi"
                    )
                ])
            ], className="mb-4")
        ], className="container"),
        create_footer()
    ]) 