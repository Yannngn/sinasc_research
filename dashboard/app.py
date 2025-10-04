"""
SINASC Dashboard - Brazilian Per# Modern Navigation Bar
navbar = dbc.Navbar(
    dbc.Container(
        [
            # Brand
            dbc.NavbarBrand(
                "SINASC Dashboard",
                href="/",
                className="fw-bold",
                style={"fontSize": "1.5rem"},
            ),
            # Toggler for mobile
            dbc.NavbarToggler(id="navbar-toggler", n_clicks=0),
            # Navigation items
            dbc.Collapse(
                dbc.Nav(
                    [
                        dbc.NavItem(dbc.NavLink("🏠 Início", href="/", active="exact", className="nav-link-custom")),
                        dbc.NavItem(dbc.NavLink("📅 Análise Anual", href="/annual", active="exact", className="nav-link-custom")),
                        dbc.NavItem(dbc.NavLink("📈 Temporal", href="/timeline", active="exact", className="nav-link-custom")),
                        dbc.NavItem(dbc.NavLink("🗺️ Geográfico", href="/geographic", active="exact", className="nav-link-custom")),
                        dbc.NavItem(dbc.NavLink("🔍 Insights", href="/insights", active="exact", className="nav-link-custom")),
                    ],
                    className="ms-auto",
                    navbar=True,
                ),
                id="navbar-collapse",
                navbar=True,
            ),
        ],
        fluid=True,
    ),
    color="primary",
    dark=True,
    className="mb-4 shadow-lg",
    style={"borderBottom": "3px solid #1976d2"},
)

# Navbar collapse callback for mobile
@app.callback(
    Output("navbar-collapse", "is_open"),
    Input("navbar-toggler", "n_clicks"),
    State("navbar-collapse", "is_open"),
)
def toggle_navbar_collapse(n, is_open):
    if n:
        return not is_open
    return is_opennalytics

A modern, interactive web dashboard for analyzing Brazilian birth records (SINASC).
Built with Plotly Dash and optimized for free-tier hosting.

Author: Yannngn
License: MIT
"""

import dash_bootstrap_components as dbc
from config.settings import DEBUG, HOST, PORT
from dash import Dash, Input, Output, dcc, html
from pages import annual, home

# Initialize the Dash app with modern theme and custom styles
app = Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        dbc.icons.FONT_AWESOME,
        "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap",
    ],
    suppress_callback_exceptions=True,
    title="SINASC Dashboard - Análise de Saúde Perinatal",
    update_title="Carregando...",
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"},
        {"name": "description", "content": "Dashboard interativo para análise de dados perinatais brasileiros - SINASC/DATASUS"},
        {"name": "theme-color", "content": "#2196f3"},
    ],
)

# Expose server for deployment
server = app.server

# Navigation bar
navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("🏠 Início", href="/", active="exact")),
        dbc.NavItem(dbc.NavLink("📅 Análise Anual", href="/annual", active="exact")),
        dbc.NavItem(dbc.NavLink("📈 Temporal", href="/timeline", active="exact")),
        dbc.NavItem(dbc.NavLink("🗺️ Geográfico", href="/geographic", active="exact")),
        dbc.NavItem(dbc.NavLink("🔍 Insights", href="/insights", active="exact")),
    ],
    brand="SINASC Dashboard",
    brand_href="/",
    color="primary",
    dark=True,
    className="mb-3",
)

# App layout
app.layout = html.Div([dcc.Location(id="url", refresh=False), navbar, html.Div(id="page-content")])


# Register callbacks from pages
home.register_callbacks(app)
annual.register_callbacks(app)


# Routing callback
@app.callback(Output("page-content", "children"), Input("url", "pathname"))
def display_page(pathname):
    """Route to appropriate page based on URL."""
    if pathname == "/":
        return home.layout
    elif pathname == "/annual":
        return annual.layout
    elif pathname == "/timeline":
        return html.Div(
            [html.H2("📈 Análise Temporal", className="text-center mt-5"), html.P("Em desenvolvimento...", className="text-center text-muted")],
            className="container",
        )
    elif pathname == "/geographic":
        return html.Div(
            [
                html.H2("🗺️ Análise Geográfica", className="text-center mt-5"),
                html.P("Em desenvolvimento...", className="text-center text-muted"),
            ],
            className="container",
        )
    elif pathname == "/insights":
        return html.Div(
            [
                html.H2("🔍 Insights Detalhados", className="text-center mt-5"),
                html.P("Em desenvolvimento...", className="text-center text-muted"),
            ],
            className="container",
        )
    else:
        return html.Div(
            [
                html.H2("404 - Página não encontrada", className="text-center mt-5"),
                html.P("A página solicitada não existe.", className="text-center text-muted"),
                dbc.Button("Voltar ao Início", href="/", color="primary", className="d-block mx-auto"),
            ],
            className="container",
        )


if __name__ == "__main__":
    app.run(debug=DEBUG, host=HOST, port=PORT)
