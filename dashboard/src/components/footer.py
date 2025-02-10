from dash import html
import dash_bootstrap_components as dbc

def create_footer():
    return html.Footer(
        dbc.Container([
            html.Hr(),  # Ligne de séparation
            dbc.Row([
                dbc.Col([
                    html.A(
                        html.Img(
                            src="https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png",
                            height="30px"
                        ),
                        href="https://github.com/Xavier973/jobmarket-v2-1",
                        target="_blank"
                    )
                ], className="text-center"),
            ], className="justify-content-center"),
            dbc.Row([
                dbc.Col([
                    html.P("Réalisation : Xavier Cuniberti, Mohamed Gassama, Said Chachet", 
                           className="text-center mb-0")
                ])
            ])
        ]),
        className="mt-4 py-3 bg-light"
    )