from dash.dependencies import Output, Input
from data import get_data_for_graph_1, get_data_for_table_2
from layouts import layout_1, layout_2, index_page
from dash import html
import dash

def register_callbacks(app):
    @app.callback(
        [Output('graph-1-donut', 'figure'),
         Output('graph-1-postes', 'figure'),
         Output('graph-1-companies', 'figure'),
         Output('graph-1-locations', 'figure')],
        [Input('url', 'pathname'),
         Input('dropdown-postes', 'value'),
         Input('dropdown-companies', 'value'),
         Input('dropdown-nbrlocations', 'value'),
         Input('dropdown-locations', 'value')]
    )
    def update_graph_1(pathname, n_postes, n_companies, n_locations, selected_location):
        if pathname == '/page-1':
            return get_data_for_graph_1(n_postes, n_companies, n_locations, selected_location)
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update

    @app.callback(
        Output('table-2-offres', 'data'),
        [Input('url', 'pathname'), Input('dropdown-2-postes', 'value')]
    )
    def update_table(pathname, selected_poste):
        return get_data_for_table_2(pathname, selected_poste)

    @app.callback(
        Output('page-content', 'children'),
        [Input('url', 'pathname')]
    )
    def display_page(pathname):
        if pathname == '/page-1':
            return layout_1
        elif pathname == '/page-2':
            return layout_2
        elif pathname == '/page-3':
            return html.Div()  # Page blanche pour l'instant
        else:
            return index_page

    @app.callback(
        Output('graph-2-skills', 'figure'),
        [Input('table-2-offres', 'active_cell'), 
         Input('table-2-offres', 'data')]
    )
    def update_graph(active_cell, data):
        # Déplacer la logique correspondante depuis main.old.py
        pass
