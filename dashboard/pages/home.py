"""
Home page - Multi-year comparison and overview statistics.
"""

import dash_bootstrap_components as dbc
import plotly.express as px  # Added import for Plotly Express
from components.cards import create_year_summary_card
from components.charts import (
    create_line_chart,
    create_simple_bar_chart,
)
from components.geo_charts import create_choropleth_chart
from config.settings import CHART_CONFIG, CHART_HEIGHT, COLOR_CONTINUOS_PALLETTE, COLOR_PALETTE  # Removed unused COLOR_PALETTE import
from dash import Input, Output, dcc, html
from data.loader import data_loader

# Define mappings for indicators
INDICATOR_MAPPINGS = {
    "birth": {
        "absolute": "total_births",
        "relative": "births_per_1k",
        "absolute_title": "Número Absoluto de Nascimentos",
        "relative_title": "Nascimentos por 1.000 Habitantes",
        "label": "Nascimentos",
        "color": "primary",
        "recommended_relative_limit": None,
        "recommended_name": None,
    },
    "cesarean": {
        "absolute": "cesarean_count",
        "relative": "cesarean_pct",
        "absolute_title": "Número Absoluto de Cesáreas",
        "relative_title": "Taxa de Cesáreas (%)",
        "label": "Cesáreas",
        "color": "warning",
        "recommended_relative_limit": 15.0,
        "recommended_name": "Referência OMS",
    },
    "preterm": {
        "absolute": "preterm_count",
        "relative": "preterm_pct",
        "absolute_title": "Número Absoluto de Nascimentos Prematuros",
        "relative_title": "Taxa de Prematuridade (%)",
        "label": "Nascimentos Prematuros",
        "color": "danger",
        "recommended_relative_limit": 10.0,
        "recommended_name": "Referência OMS",
    },
    "adolescent": {
        "absolute": "adolescent_pregnancy_count",
        "relative": "adolescent_pregnancy_pct",
        "absolute_title": "Número Absoluto de Gestações em Adolescentes",
        "relative_title": "Taxa de Gravidez na Adolescência (%)",
        "label": "Gestações em Adolescentes",
        "color": "info",
        "recommended_relative_limit": None,
        "recommended_name": None,
    },
    "low_weight": {
        "absolute": "low_birth_weight_count",
        "relative": "low_birth_weight_pct",
        "absolute_title": "Número Absoluto de Nascimentos com Baixo Peso",
        "relative_title": "Taxa de Baixo Peso ao Nascer (%)",
        "label": "Baixo Peso ao Nascer",
        "color": "info",
        "recommended_relative_limit": None,
        "recommended_name": None,
    },
    "low_apgar": {
        "absolute": "low_apgar5_count",
        "relative": "low_apgar5_pct",
        "absolute_title": "Número Absoluto de APGAR5 Baixo",
        "relative_title": "Taxa de APGAR5 Baixo (%)",
        "label": "APGAR5 Baixo",
        "color": "danger",
        "recommended_relative_limit": None,
        "recommended_name": None,
    },
}


def generate_cards(page):
    """Generate year summary cards for a specific page."""
    items_per_page = 4
    available_years = sorted(data_loader.get_available_years(), reverse=True)  # Most recent first
    start_idx = page * items_per_page
    end_idx = start_idx + items_per_page
    year_group = available_years[start_idx:end_idx]

    cards_in_group = []
    for year in year_group:
        summary = data_loader.get_year_summary(year)
        cards_in_group.append(
            dbc.Col(
                create_year_summary_card(year, summary),
                width=12,
                md=6,
                lg=4,
                xl=3,
                className="mb-3",
            )
        )
    return cards_in_group


def create_layout() -> html.Div:
    """
    Create home page layout with multi-year comparison.

    Returns:
        Dash HTML Div with page layout
    """
    # Get metadata
    metadata = data_loader.get_metadata()
    available_years = sorted(data_loader.get_available_years(), reverse=True)  # Most recent first

    # Pagination setup
    items_per_page = 4
    total_pages = (len(available_years) + items_per_page - 1) // items_per_page

    # Initial cards for the first page
    initial_cards = generate_cards(0)

    # Header
    def return_header() -> dbc.Row:
        return dbc.Row(
            [
                dbc.Col(
                    [
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.H1(
                                            "SINASC Dashboard",
                                            className="mb-3 text-primary fw-extrabold",
                                        ),
                                        html.P(
                                            "Sistema de Informações sobre Nascidos Vivos",
                                            className="lead mb-2 fontsize-4",
                                        ),
                                        html.P(
                                            "Análise Comparativa de Indicadores de Saúde Perinatal (2015-2024)",
                                            className="text-muted fontsize-4",
                                        ),
                                    ],
                                    className="text-center mb-4 p-4 rounded bg-transparent",
                                    style={
                                        "background": "linear-gradient(135deg, #f5f5f5 0%, white 100%)",
                                        # "border": "2px solid #e3f2fd",
                                    },
                                )
                            ],
                            className="mb-4",
                        )
                    ]
                )
            ]
        )

    def return_summary_cards() -> dbc.Row:
        return dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Row(
                            [
                                # Year summary cards with pagination
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            [
                                                html.Div(
                                                    [
                                                        html.H4(
                                                            "Resumo por Ano",
                                                        ),
                                                        html.P(
                                                            "Principais indicadores de qualidade perinatal organizados por período",
                                                            className="text-muted small",
                                                        ),
                                                    ],
                                                    className="mb-3 mx-0",
                                                ),
                                            ]
                                        )
                                    ]
                                ),
                                dbc.Row(
                                    id="year-summary-cards",
                                    children=initial_cards,
                                    className="mt-3 px-2",
                                ),
                                dbc.Pagination(
                                    id="year-pagination",
                                    max_value=total_pages,
                                    active_page=1,
                                    fully_expanded=False,
                                    className="mt-3 px-2",
                                ),
                            ],
                            className="shadow-sm",
                        )
                    ]
                )
            ],
            className="mb-5",
        )

    def return_yearly_charts() -> dbc.Row:
        return dbc.Row(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.Div(
                                    [
                                        html.H4(
                                            "Análise Temporal",
                                            className="mb-0",
                                        ),
                                        html.P(
                                            "Evolução dos Nascimentos ao longo dos anos",
                                            className="text-muted small mb-0 mt-1",
                                        ),
                                    ],
                                    className="mb-3 mt-4",
                                ),
                            ],
                            width=12,
                            lg=8,
                        ),
                        dbc.Col(
                            [
                                dcc.Dropdown(
                                    id="yearly-charts-year-dropdown",
                                    options=[{"label": str(year), "value": year} for year in available_years],
                                    value=available_years[0],  # Default to the most recent year
                                    clearable=False,
                                    className="mb-3",
                                    style={"width": "100%"},
                                ),
                                dcc.Dropdown(
                                    id="yearly-charts-type-dropdown",
                                    options=[
                                        {"label": "Absoluto", "value": "absolute"},
                                        {"label": "Por 1.000 Hab", "value": "per_1k"},
                                    ],
                                    value="absolute",
                                    clearable=False,
                                    className="mb-3",
                                    style={"width": "100%"},
                                ),
                            ],
                            width=12,
                            lg=4,
                            className="d-flex justify-content-center align-items-end",
                        ),
                    ],
                ),
                dbc.Row(
                    [
                        # Evolução do Total de Nascimentos
                        dbc.Col(
                            [
                                dbc.Card(
                                    [
                                        dbc.CardHeader(
                                            html.H5(
                                                "Evolução do Total de Nascimentos",
                                                className="mb-0",
                                            ),
                                            className="bg-light",
                                        ),
                                        dbc.CardBody(
                                            [
                                                dcc.Graph(
                                                    id="home-births-evolution",
                                                    config=CHART_CONFIG,  # type:ignore
                                                    style={"height": f"{CHART_HEIGHT}px"},
                                                )
                                            ]
                                        ),
                                    ],
                                    className="shadow-sm",
                                )
                            ],
                            width=12,
                            lg=8,
                        ),
                        # Mapa de Nascimentos por estado do ultimo ano
                        dbc.Col(
                            [
                                dbc.Card(
                                    [
                                        dbc.CardHeader(
                                            html.H5(
                                                "Distribuição Geográfica",
                                                className="mb-0",
                                            ),
                                            className="bg-light",
                                        ),
                                        dbc.CardBody(
                                            [
                                                dcc.Graph(
                                                    id="state-level-map",
                                                    config=CHART_CONFIG,  # type:ignore
                                                    style={"height": f"{CHART_HEIGHT}px"},
                                                )
                                            ]
                                        ),
                                    ],
                                    className="shadow-sm",
                                )
                            ],
                            width=12,
                            lg=4,
                        ),
                    ],
                ),
            ],
            className="mb-4 gap-4",
        )

    def return_indicator_analysis() -> dbc.Row:
        return dbc.Row(
            [
                # Header
                dbc.Row(
                    [
                        # Title
                        dbc.Col(
                            [
                                html.Div(
                                    [
                                        html.H4(
                                            "Análise Temporal de Indicadores",
                                            className="mb-0",
                                        ),
                                        html.P(
                                            "Evolução dos indicadores ao longo dos anos",
                                            className="text-muted small mb-0 mt-1",
                                        ),
                                    ],
                                    className="mb-3 mt-4",
                                ),
                            ],
                            width=12,
                            lg=8,
                        ),
                        # Indicator selector
                        dbc.Col(
                            [
                                dcc.Dropdown(
                                    id="indicator-dropdown",
                                    options=[
                                        {"label": "Cesáreas", "value": "cesarean"},
                                        {"label": "Nascimentos Prematuros", "value": "preterm"},
                                        {"label": "Gestações em Adolescentes", "value": "adolescent"},
                                        {"label": "Baixo Peso ao Nascer", "value": "low_weight"},
                                        {"label": "APGAR5 Baixo", "value": "low_apgar"},
                                    ],
                                    value="cesarean",  # Default value
                                    clearable=False,
                                    className="mb-3",
                                    style={"width": "100%"},
                                )
                            ],
                            width=12,
                            lg=4,
                            className="d-flex justify-content-center align-items-end",
                        ),
                    ],
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Card(
                                    [
                                        dbc.CardHeader(
                                            html.H5(
                                                id="absolute-indicator-chart-title",
                                                className="mb-0",
                                            ),
                                            className="bg-light",
                                        ),
                                        dbc.CardBody(
                                            [
                                                dcc.Graph(
                                                    id="home-absolute-indicator-chart",
                                                    config=CHART_CONFIG,  # type:ignore
                                                    style={"height": f"{CHART_HEIGHT}px"},
                                                )
                                            ]
                                        ),
                                    ],
                                    className="shadow-sm",
                                )
                            ],
                            width=12,
                            lg=6,
                        ),
                        dbc.Col(
                            [
                                dbc.Card(
                                    [
                                        dbc.CardHeader(
                                            html.H5(
                                                id="relative-indicator-chart-title",
                                                className="mb-0",
                                            ),
                                            className="bg-light",
                                        ),
                                        dbc.CardBody(
                                            [
                                                dcc.Graph(
                                                    id="home-relative-indicator-chart",
                                                    config=CHART_CONFIG,  # type:ignore
                                                    style={"height": f"{CHART_HEIGHT}px"},
                                                )
                                            ]
                                        ),
                                    ],
                                    className="shadow-sm",
                                )
                            ],
                            width=12,
                            lg=6,
                        ),
                    ],
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Card(
                                    [
                                        dbc.CardHeader(
                                            html.H5(
                                                "Distribuição de Indicador no Último Ano",
                                                className="mb-0",
                                            ),
                                            className="bg-light",
                                        ),
                                        dbc.CardBody(
                                            [
                                                dcc.Graph(
                                                    id="home-indicator-pie-chart",
                                                    config=CHART_CONFIG,  # type:ignore
                                                    style={"height": f"{CHART_HEIGHT}px"},
                                                )
                                            ]
                                        ),
                                    ],
                                    className="shadow-sm",
                                )
                            ],
                            width=12,
                            lg=4,
                        ),
                        dbc.Col(
                            [
                                dbc.Card(
                                    [
                                        dbc.CardHeader(
                                            html.H5(
                                                "Mapa Geográfico do Indicador",
                                                className="mb-0",
                                            ),
                                            className="bg-light",
                                        ),
                                        dbc.CardBody(
                                            [
                                                dcc.Graph(
                                                    id="indicator-choropleth-map",
                                                    config=CHART_CONFIG,  # type:ignore
                                                    style={"height": f"{CHART_HEIGHT}px"},
                                                )
                                            ]
                                        ),
                                    ],
                                    className="shadow-sm",
                                )
                            ],
                            width=12,
                            lg=4,
                        ),
                        dbc.Col(
                            [
                                dbc.Card(
                                    [
                                        dbc.CardHeader(
                                            html.H5(
                                                "Mapa Geográfico do Indicador (Relativo aos Nascimentos)",
                                                className="mb-0",
                                            ),
                                            className="bg-light",
                                        ),
                                        dbc.CardBody(
                                            [
                                                dcc.Graph(
                                                    id="indicator-relative-choropleth-map",
                                                    config=CHART_CONFIG,  # type:ignore
                                                    style={"height": f"{CHART_HEIGHT}px"},
                                                )
                                            ]
                                        ),
                                    ],
                                    className="shadow-sm",
                                )
                            ],
                            width=12,
                            lg=4,
                        ),
                    ]
                ),
            ],
            className="mb-4 gap-4",
        )

    def return_footer() -> dbc.Row:
        return dbc.Row(
            [
                dbc.Col(
                    [
                        html.Hr(),
                        html.P(
                            [
                                html.I(className="fas fa-database me-2"),
                                "Fonte: DATASUS - SINASC | ",
                                f"Total de registros: {metadata.get('total_records', 0):,} | ",
                                f"Anos disponíveis: {', '.join(map(str, available_years))}",
                            ],
                            className="text-muted small text-center",
                        ),
                    ]
                )
            ]
        )

    return html.Div(
        [
            # return_header,
            return_summary_cards(),
            return_yearly_charts(),
            return_indicator_analysis(),
            # Data source footer
            return_footer(),
        ],
        className="container-fluid p-4",
    )


def register_callbacks(app):
    """Register callbacks for home page."""

    @app.callback(
        Output("year-summary-cards", "children"),
        Input("year-pagination", "active_page"),
    )
    def update_year_cards(active_page):
        """Update year summary cards based on the active pagination page."""
        return generate_cards(active_page - 1)

    @app.callback(
        [
            Output("home-absolute-indicator-chart", "figure"),
            Output("home-relative-indicator-chart", "figure"),
            Output("absolute-indicator-chart-title", "children"),
            Output("relative-indicator-chart-title", "children"),
        ],
        Input("indicator-dropdown", "value"),
    )
    def update_indicator_charts(selected_indicator):
        """Update the absolute and relative indicator charts based on the selected indicator."""
        df = data_loader.load_yearly_aggregates()

        # Get the selected indicator's data
        indicator_data = INDICATOR_MAPPINGS[selected_indicator]

        # Create absolute chart
        absolute_chart = create_simple_bar_chart(
            df=df,
            x_col="year",
            y_col=indicator_data["absolute"],
            x_title="Ano",
            y_title=indicator_data["absolute_title"],
            color=indicator_data["color"],
        )

        # Create relative chart with reference line if available
        reference_line = None
        if indicator_data["recommended_relative_limit"] is not None:
            reference_line = {
                "y": indicator_data["recommended_relative_limit"],
                "text": indicator_data["recommended_name"],
                "color": COLOR_PALETTE[indicator_data["color"]],
            }

        relative_chart = create_line_chart(
            df=df,
            x_col="year",
            y_col=indicator_data["relative"],
            x_title="Ano",
            y_title=indicator_data["relative_title"],
            color=indicator_data["color"],
            reference_line=reference_line,
        )

        return (
            absolute_chart,
            relative_chart,
            indicator_data["absolute_title"],
            indicator_data["relative_title"],
        )

    @app.callback(
        Output("home-indicator-pie-chart", "figure"),
        Input("indicator-dropdown", "value"),
    )
    def update_indicator_pie_chart(selected_indicator):
        """Update the pie chart based on the selected indicator."""
        df = data_loader.load_yearly_aggregates()

        # Get the selected indicator's data
        indicator_data = INDICATOR_MAPPINGS[selected_indicator]

        # Aggregate data for the pie chart
        total = df[indicator_data["absolute"]].sum()
        other = df["total_births"].sum() - total

        pie_data = {
            "labels": [indicator_data["label"], "Outros"],
            "values": [total, other],
            "color": [COLOR_PALETTE[indicator_data["color"]], "#E0E0E0"],
        }

        # Create pie chart
        pie_chart = px.pie(
            pie_data,
            names="labels",
            values="values",
            color="labels",
            # title=indicator_data["absolute_title"],
            color_discrete_sequence=pie_data["color"],
        )

        # Add recommended limit annotation if available
        if indicator_data["recommended_relative_limit"] is not None:
            pie_chart.add_annotation(
                text=f"{indicator_data['recommended_name']}: {indicator_data['recommended_relative_limit']}%",
                x=0.5,
                y=-0.2,
                showarrow=False,
                font=dict(size=12, color="gray"),
                xref="paper",
                yref="paper",
            )

        return pie_chart

    @app.callback(
        [
            Output("indicator-choropleth-map", "figure"),
            Output("indicator-relative-choropleth-map", "figure"),
        ],
        Input("indicator-dropdown", "value"),
        Input("year-pagination", "active_page"),
    )
    def update_indicator_maps(selected_indicator, active_page):
        """Update both absolute and relative choropleth maps for the selected indicator and page."""
        year = data_loader.get_available_years()[active_page - 1]
        df = data_loader.load_yearly_state_aggregates(year)
        geojson = data_loader._load_brazil_states_geojson()
        indicator_data = INDICATOR_MAPPINGS[selected_indicator]

        abs_map = create_choropleth_chart(
            df.loc[df["year"] == year],
            geojson=geojson,
            indicator=indicator_data["label"],
            color=indicator_data["absolute"],
            color_scale=COLOR_CONTINUOS_PALLETTE[indicator_data["color"]],
            title=indicator_data["label"],
        )

        rel_map = create_choropleth_chart(
            df.loc[df["year"] == year],
            geojson=geojson,
            indicator=indicator_data["label"],
            color=indicator_data["relative"],
            color_scale=COLOR_CONTINUOS_PALLETTE[indicator_data["color"]],
            title=indicator_data["label"],
        )

        return abs_map, rel_map

    @app.callback(
        Output("state-level-map", "figure"),
        [
            Input("yearly-charts-year-dropdown", "value"),
            Input("yearly-charts-type-dropdown", "value"),
        ],
    )
    def update_yearly_charts(selected_year, selected_type):
        """Update yearly charts based on the selected year."""
        # Load state-level aggregates for the selected year
        df = data_loader.load_state_aggregates_with_population(selected_year)

        # Load GeoJSON data for Brazil's states
        geojson = data_loader._load_brazil_states_geojson()
        indicator_data = INDICATOR_MAPPINGS["birth"]
        col = indicator_data["absolute"] if selected_type == "absolute" else indicator_data["relative"]

        # Update state-level map
        state_level_map = create_choropleth_chart(df=df, geojson=geojson, indicator=col, color=col, color_scale="Blues", title="Nascimentos")

        return state_level_map

    @app.callback(
        Output("home-births-evolution", "figure"),
        Input("yearly-charts-type-dropdown", "value"),
    )
    def update_births_evolution(selected_type):
        """Update births evolution chart based on selected year and type."""
        df = data_loader.load_yearly_aggregates()
        if "births_per_1k" not in df.columns:
            df["births_per_1k"] = df["total_births"].mul(1000 / 190_755_799).round(2)

        if selected_type == "absolute":
            y_title = "Número de Nascimentos"
            y_col = "total_births"
        else:
            y_title = "Nascimentos por 1.000 Habitantes"
            y_col = "births_per_1k"

        return create_simple_bar_chart(
            df=df,
            x_col="year",
            y_col=y_col,
            x_title="Ano",
            y_title=y_title,
            color="primary",
        )


layout = create_layout()
