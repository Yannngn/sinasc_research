"""
Home page - Multi-year comparison and overview statistics.
"""

import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from components.cards import create_year_summary_card
from components.charts import create_bar_chart, create_line_chart, create_pie_chart
from components.geo_charts import create_choropleth_chart
from config.constants import INDICATOR_MAPPINGS
from config.settings import CHART_CONFIG, CHART_HEIGHT, COLOR_CONTINUOS_PALETTE
from dash import Input, Output, State, dcc, html
from data.loader import data_loader


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
                lg=6,
                xl=4,
                xxl=3,
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

    # Load default data for stores
    default_year = available_years[0]  # Most recent year
    yearly_aggregates_data = data_loader.load_yearly_aggregates().to_dict("records")
    yearly_state_aggregates_data = data_loader.load_monthly_state_aggregates(default_year).to_dict("records")

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
                # Year summary cards with pagination
                dbc.Row(
                    [
                        dbc.Col(
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
                        )
                    ]
                ),
                dbc.Row(
                    id="home-year-summary-cards",
                    children=initial_cards,
                    className="mt-3 px-2",
                ),
                dbc.Pagination(
                    id="home-year-pagination",
                    max_value=total_pages,
                    active_page=1,
                    fully_expanded=False,
                    className="mt-3 px-2",
                ),
            ],
            className="shadow-sm mb-5",
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
                                    id="home-birth-year-dropdown",
                                    options=[{"label": str(year), "value": year} for year in available_years],
                                    value=available_years[0],  # Default to the most recent year
                                    clearable=False,
                                    className="mb-3",
                                    style={"width": "100%"},
                                ),
                                dcc.Dropdown(
                                    id="home-birth-type-dropdown",
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
                            className="d-flex justify-content-center align-items-end gap-2",
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
                                                id="home-births-evolution-title",
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
                                            ],
                                            className="p-0",
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
                                                id="home-state-level-map-title",
                                                className="mb-0",
                                            ),
                                            className="bg-light",
                                        ),
                                        dbc.CardBody(
                                            [
                                                dcc.Graph(
                                                    id="home-state-level-map",
                                                    config=CHART_CONFIG,  # type:ignore
                                                    style={"height": f"{CHART_HEIGHT}px"},
                                                )
                                            ],
                                            className="p-0",
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
            children=[
                dcc.Loading(
                    id="home-loading",
                    type="default",
                    children=[
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
                                            id="home-indicator-year-dropdown",
                                            options=[{"label": str(year), "value": year} for year in available_years],
                                            value=available_years[0],  # Default to the most recent year
                                            clearable=False,
                                            className="mb-3",
                                            style={"width": "100%"},
                                        ),
                                        dcc.Dropdown(
                                            id="home-indicator-type-dropdown",
                                            options=[
                                                {"label": imv.get_labels()[0], "value": imk}
                                                for imk, imv in list(INDICATOR_MAPPINGS.items())[1:]
                                            ],
                                            value="cesarean",  # Default value
                                            clearable=False,
                                            className="mb-3",
                                            style={"width": "100%"},
                                        ),
                                    ],
                                    width=12,
                                    lg=4,
                                    className="d-flex justify-content-center align-items-end gap-2",
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
                                                        id="home-absolute-indicator-chart-title",
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
                                                    ],
                                                    className="p-0",
                                                ),
                                            ],
                                            className="shadow-sm",
                                        )
                                    ],
                                    width=12,
                                    lg=5,
                                ),
                                dbc.Col(
                                    [
                                        dbc.Card(
                                            [
                                                dbc.CardHeader(
                                                    html.H5(
                                                        id="home-relative-indicator-chart-title",
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
                                                    ],
                                                    className="p-0",
                                                ),
                                            ],
                                            className="shadow-sm",
                                        )
                                    ],
                                    width=12,
                                    lg=5,
                                ),
                                dbc.Col(
                                    [
                                        dbc.Card(
                                            [
                                                dbc.CardHeader(
                                                    html.H5(
                                                        "Distribuição de Indicador no Último Ano",
                                                        id="home-indicator-pie-title",
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
                                                    ],
                                                    className="p-0",
                                                ),
                                            ],
                                            className="shadow-sm",
                                        )
                                    ],
                                    width=12,
                                    lg=2,
                                ),
                            ],
                            className="mb-4",
                        ),
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        dbc.Card(
                                            [
                                                dbc.CardHeader(
                                                    html.H5(
                                                        "Mapa Geográfico do Indicador",
                                                        id="home-indicator-absolute-map-title",
                                                        className="mb-0",
                                                    ),
                                                    className="bg-light",
                                                ),
                                                dbc.CardBody(
                                                    [
                                                        dcc.Graph(
                                                            id="home-indicator-absolute-map-chart",
                                                            config=CHART_CONFIG,  # type:ignore
                                                            style={"height": f"{CHART_HEIGHT}px"},
                                                        )
                                                    ],
                                                    className="p-0",
                                                ),
                                            ],
                                            className="shadow-sm",
                                        )
                                    ],
                                    width=12,
                                    lg=3,
                                ),
                                dbc.Col(
                                    [
                                        dbc.Card(
                                            [
                                                dbc.CardHeader(
                                                    html.H5(
                                                        "Mapa Geográfico do Indicador (Relativo aos Nascimentos)",
                                                        id="home-indicator-relative-map-title",
                                                        className="mb-0",
                                                    ),
                                                    className="bg-light",
                                                ),
                                                dbc.CardBody(
                                                    [
                                                        dcc.Graph(
                                                            id="home-indicator-relative-map-chart",
                                                            config=CHART_CONFIG,  # type:ignore
                                                            style={"height": f"{CHART_HEIGHT}px"},
                                                        )
                                                    ],
                                                    className="p-0",
                                                ),
                                            ],
                                            className="shadow-sm",
                                        )
                                    ],
                                    width=12,
                                    lg=3,
                                ),
                            ],
                            className="mb-4",
                        ),
                    ],
                    className="gap-4",
                )
            ],
            className="mb-4 pb-4 gap-4 shadow-sm",
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
                                f"Total de registros: {metadata.get('total_records', 27_361_628):,} | ",
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
            # Store for shared data
            dcc.Store(id="yearly-aggregates-store", data=yearly_aggregates_data),
            dcc.Store(id="yearly-state-aggregates-store", data=yearly_state_aggregates_data),
            # return_header,
            return_summary_cards(),
            return_yearly_charts(),
            return_indicator_analysis(),
            dbc.Row(
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardHeader(
                                    html.H5(
                                        "Distribuição de Ocupação Materna",
                                        id="home-maternal-occupation-pie-title",
                                        className="mb-0",
                                    ),
                                    className="bg-light",
                                ),
                                dbc.CardBody(
                                    [
                                        dcc.Graph(
                                            id="home-maternal-occupation-pie-chart",
                                            config=CHART_CONFIG,  # type:ignore
                                            style={"height": f"{CHART_HEIGHT}px"},
                                        )
                                    ],
                                    className="p-0",
                                ),
                            ],
                            className="shadow-sm",
                        )
                    ],
                    width=12,
                    lg=3,
                    className="mb-4",
                )
            ),
            # Data source footer
            return_footer(),
        ],
        className="container-fluid p-4",
    )


def register_callbacks(app):
    """Register callbacks for home page."""

    # Data loading callbacks - populate stores on page load
    @app.callback(
        Output("yearly-aggregates-store", "data"),
        Input("home-indicator-type-dropdown", "value"),  # Trigger on any indicator change
    )
    def load_yearly_aggregates(_):
        """Load yearly aggregates data once and store it."""
        return data_loader.load_yearly_aggregates().to_dict("records")

    @app.callback(
        Output("yearly-state-aggregates-store", "data"),
        Input("home-indicator-year-dropdown", "value"),
    )
    def load_yearly_state_aggregates(selected_year):
        """Load yearly state aggregates for the selected year."""
        return data_loader.load_monthly_state_aggregates(selected_year).to_dict("records")

    @app.callback(
        Output("home-year-summary-cards", "children"),
        Input("home-year-pagination", "active_page"),
    )
    def update_year_cards(active_page):
        """Update year summary cards based on the active pagination page."""
        return generate_cards(active_page - 1)

    @app.callback(
        [
            Output("home-absolute-indicator-chart", "figure"),
            Output("home-relative-indicator-chart", "figure"),
            Output("home-absolute-indicator-chart-title", "children"),
            Output("home-relative-indicator-chart-title", "children"),
        ],
        Input("home-indicator-type-dropdown", "value"),
        State("yearly-aggregates-store", "data"),
    )
    def update_indicator_charts(selected_indicator, yearly_data):
        """Update the absolute and relative indicator charts based on the selected indicator."""
        if yearly_data is None:
            # Return empty figures if data not loaded yet
            empty_fig = {"data": [], "layout": {}}
            return empty_fig, empty_fig, "Carregando...", "Carregando..."

        df = pd.DataFrame(yearly_data)

        # Get the selected indicator's data
        indicator_data = INDICATOR_MAPPINGS[selected_indicator]

        # Create absolute chart
        absolute_columns = indicator_data.get_absolute_columns()
        if len(absolute_columns) == 1:
            # Single column - use bar chart
            absolute_chart = create_bar_chart(
                df=df,
                x_col="year",
                y_col=absolute_columns[0],
                label=indicator_data.get_labels()[0],
                color=indicator_data.get_colors()[0],
                x_title="Ano",
                y_title=indicator_data.absolute_title,
            )
        else:
            # Multiple columns - use stacked bar chart
            from components.charts import create_stacked_bar_chart

            absolute_chart = create_stacked_bar_chart(
                df=df,
                x_col="year",
                y_cols=absolute_columns,
                labels=indicator_data.get_labels(),
                colors=indicator_data.get_colors(),
                x_title="Ano",
                y_title=indicator_data.absolute_title,
            )

        # Create relative chart with reference line if available
        reference_line = indicator_data.get_reference_line()

        relative_columns = indicator_data.get_relative_columns()
        if len(relative_columns) == 1:
            # Single column - use line chart
            relative_chart = create_line_chart(
                df=df,
                x_col="year",
                y_col=relative_columns[0],
                label=indicator_data.get_labels()[0],
                color=indicator_data.get_colors()[0],
                x_title="Ano",
                y_title=indicator_data.relative_title,
                reference_line=reference_line,
            )
        else:
            # Multiple columns - use multi-line chart
            from components.charts import create_multi_line_chart

            relative_chart = create_multi_line_chart(
                df=df,
                x_col="year",
                y_cols=relative_columns,
                labels=indicator_data.get_labels(),
                colors=indicator_data.get_colors(),  # Could be made more flexible
                x_title="Ano",
                y_title=indicator_data.relative_title,
                reference_line=reference_line,
            )

        return (
            absolute_chart,
            relative_chart,
            indicator_data.absolute_title,
            indicator_data.relative_title,
        )

    @app.callback(
        [
            Output("home-indicator-pie-chart", "figure"),
            Output("home-indicator-pie-title", "children"),
        ],
        Input("home-indicator-type-dropdown", "value"),
        Input("home-indicator-year-dropdown", "value"),
        State("yearly-aggregates-store", "data"),
    )
    def update_indicator_pie_chart(selected_indicator, selected_year, yearly_data):
        """Update the pie chart based on the selected indicator."""
        if yearly_data is None:
            empty_fig = {"data": [], "layout": {}}
            return empty_fig, "Carregando..."

        df = pd.DataFrame(yearly_data)

        # Get the selected indicator's data
        indicator_data = INDICATOR_MAPPINGS[selected_indicator]

        # For pie chart, we use the first absolute column
        absolute_col = indicator_data.get_absolute_columns()[0]

        # Aggregate data for the pie chart
        total: int = df.loc[df["year"] == selected_year, absolute_col].sum()  # type: ignore
        other: int = df.loc[df["year"] == selected_year, "total_births"].sum() - total  # type: ignore

        # For labels, use the first label
        labels = indicator_data.get_labels()
        main_label = labels[0] if labels else "Indicador"

        pie_data = pd.DataFrame(
            {
                "labels": [main_label, "Outros"],
                "values": [total, other],
                "color": [indicator_data.get_colors()[0], "#E0E0E0"],
            }
        )

        # Create pie chart
        pie_chart = create_pie_chart(
            pie_data,
            names_col="labels",
            values_col="values",
            color_keys=pie_data["color"].tolist(),
        )

        # Add recommended limit annotation if available
        if indicator_data.recommended_relative_limit is not None:
            pie_chart.add_annotation(
                text=f"{indicator_data.recommended_name}: {indicator_data.recommended_relative_limit}%",
                x=0.5,
                y=-0.2,
                showarrow=False,
                font=dict(size=12, color="gray"),
                xref="paper",
                yref="paper",
            )

        title_text = f"Distribuição de {main_label} ({selected_year})"
        return pie_chart, title_text

    @app.callback(
        [
            Output("home-indicator-absolute-map-chart", "figure"),
            Output("home-indicator-relative-map-chart", "figure"),
            Output("home-indicator-absolute-map-title", "children"),
            Output("home-indicator-relative-map-title", "children"),
        ],
        Input("home-indicator-type-dropdown", "value"),
        Input("home-indicator-year-dropdown", "value"),
        State("yearly-state-aggregates-store", "data"),
    )
    def update_indicator_maps(selected_indicator, selected_year, state_data):
        """Update both absolute and relative choropleth maps for the selected indicator and year."""
        if state_data is None:
            empty_fig = {"data": [], "layout": {}}
            return empty_fig, empty_fig, "Carregando...", "Carregando..."

        df = pd.DataFrame(state_data)
        geojson = data_loader.load_geojson_states()
        indicator_data = INDICATOR_MAPPINGS[selected_indicator]

        # Use first absolute/relative column and label for maps
        abs_col = indicator_data.get_absolute_columns()[0]
        rel_col = indicator_data.get_relative_columns()[0]
        label = indicator_data.get_labels()[0]

        abs_map = create_choropleth_chart(
            df,
            geojson=geojson,
            indicator=label,
            color=abs_col,
            color_scale=COLOR_CONTINUOS_PALETTE[indicator_data.get_colors()[0]],
            title=label,
        )

        rel_map = create_choropleth_chart(
            df,
            geojson=geojson,
            indicator=label,
            color=rel_col,
            color_scale=COLOR_CONTINUOS_PALETTE[indicator_data.get_colors()[0]],
            title=label,
        )

        title_text = f"Mapa de {label} ({selected_year})"
        rel_title_text = f"Mapa de Taxa de {label} ({selected_year})"

        return abs_map, rel_map, title_text, rel_title_text

    @app.callback(
        [
            Output("home-state-level-map", "figure"),
            Output("home-state-level-map-title", "children"),
        ],
        Input("home-birth-year-dropdown", "value"),
        Input("home-birth-type-dropdown", "value"),
    )
    def update_yearly_charts(selected_year, selected_type):
        """Update yearly charts based on the selected year."""
        # Load state-level aggregates for the selected year
        df = data_loader.load_monthly_state_aggregates(selected_year, True)

        # Load GeoJSON data for Brazil's states
        geojson = data_loader.load_geojson_states()
        indicator_data = INDICATOR_MAPPINGS["birth"]

        # Use first absolute/relative column
        abs_col = indicator_data.get_absolute_columns()[0]
        rel_col = indicator_data.get_relative_columns()[0]
        col = abs_col if selected_type == "absolute" else rel_col

        # Title depending on selection
        title_text = "Nascimentos" if selected_type == "absolute" else "Nascimentos por 1.000 Hab"

        # Update state-level map
        state_level_map = create_choropleth_chart(df=df, geojson=geojson, indicator=col, color=col, color_scale="Blues", title=title_text)

        return state_level_map, title_text

    @app.callback(
        [
            Output("home-births-evolution", "figure"),
            Output("home-births-evolution-title", "children"),
        ],
        Input("home-birth-type-dropdown", "value"),
        State("yearly-aggregates-store", "data"),
    )
    def update_births_evolution(selected_type, yearly_data):
        """Update births evolution chart based on selected year and type."""
        if yearly_data is None:
            empty_fig = {"data": [], "layout": {}}
            return empty_fig, "Carregando..."

        df = pd.DataFrame(yearly_data)

        if "births_per_1k" not in df.columns:
            df["births_per_1k"] = df["total_births"].mul(1000 / 190_755_799).round(2)

        if selected_type == "absolute":
            y_title = "Número de Nascimentos"
            y_col = "total_births"
            header_text = "Evolução do Total de Nascimentos"
        else:
            y_title = "Nascimentos por 1.000 Habitantes"
            y_col = "births_per_1k"
            header_text = "Evolução por 1.000 Habitantes"

        fig = create_bar_chart(
            df=df,
            x_col="year",
            y_col=y_col,
            label="Nascimentos",
            x_title="Ano",
            y_title=y_title,
            color="primary",
        )

        return fig, header_text

    @app.callback(
        [
            Output("home-maternal-occupation-pie-chart", "figure"),
            Output("home-maternal-occupation-pie-title", "children"),
        ],
        Input("home-birth-year-dropdown", "value"),
    )
    def update_maternal_occupation_chart(year: int):
        """
        Update maternal occupation distribution chart using metadata summary.

        Args:
            year: Selected year for data filtering

        Returns:
            Tuple of (Plotly figure object, dynamic title string)
        """
        summary = data_loader.get_year_summary(year)
        maternal_occupation = summary.get("maternal_occupation", {})

        # Build a clean DataFrame: expected structure is {code: {"label": str, "count": int}}
        rows = []
        if isinstance(maternal_occupation, dict) and maternal_occupation:
            for code, info in maternal_occupation.items():
                if isinstance(info, dict):
                    label = info.get("label", str(code))
                    count = int(info.get("count", 0) or 0)
                else:
                    # backward compatibility: if value is just a count
                    label = str(code)
                    try:
                        count = int(info)
                    except Exception:
                        count = 0

                rows.append({"code": str(code), "label": label, "count": count})

        occupation_counts = pd.DataFrame(rows)

        # Remove zero counts (they clutter the pie) and sort by count desc
        occupation_counts = occupation_counts[occupation_counts["count"] > 0].sort_values("count", ascending=False)

        palette = px.colors.qualitative.Prism
        colors = [palette[i % len(palette)] for i in range(len(occupation_counts))]

        # Create pie chart with smaller text and tighter margins so the pie fills the card
        fig = go.Figure(
            data=[
                go.Pie(
                    labels=occupation_counts["label"],
                    values=occupation_counts["count"],
                    hole=0.4,
                    textinfo="label+percent",
                    textposition="inside",
                    marker=dict(colors=colors, line=dict(color="white", width=0.5)),
                )
            ]
        )

        fig.update_traces(textfont_size=12, insidetextorientation="radial")

        fig.update_layout(
            template="plotly_white",
            showlegend=False,
            legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.02),
            margin=dict(t=40, b=10, l=10, r=80),
            height=int(CHART_HEIGHT),
        )

        title = f"Distribuição de Ocupação Materna - {year}"

        return fig, title


layout = create_layout()
