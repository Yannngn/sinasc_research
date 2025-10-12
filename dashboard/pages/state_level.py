"""
State-Level Geographic Analysis page - Territorial distribution and regional comparisons.

This page provides interactive maps and regional analysis of birth data across
Brazilian states, enabling state-level pattern identification and health outcome comparisons.
"""

import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go
from components.charts import create_colored_bar_chart
from components.geo_charts import create_choropleth_chart, create_state_scatter_plot
from config.constants import INDICATOR_MAPPINGS
from config.geographic import get_region_from_id_code, get_state_from_id_code
from config.settings import CHART_CONFIG, CHART_HEIGHT
from dash import Input, Output, callback, dcc, html
from data.loader import data_loader
from utils import format_brazilian_number, format_indicator_value


def _create_ranking_table(df_subset: pd.DataFrame, indicator: str, metric: str, label: str) -> dbc.Table:
    """Helper to create a ranking table for top or bottom states."""
    rows = []
    for _, row in df_subset.iterrows():
        state_name = row["state_name"]
        value = row[indicator]
        births = row.get("total_births", 0)
        rows.append(
            html.Tr(
                [
                    html.Td(html.Strong(state_name), className="text-start"),
                    html.Td(format_indicator_value(value, metric), className="text-end"),
                    html.Td(format_brazilian_number(births), className="text-end text-muted small"),
                ]
            )
        )
    return dbc.Table(
        [
            html.Thead(
                html.Tr(
                    [
                        html.Th("Estado", className="text-start"),
                        html.Th(label, className="text-end"),
                        html.Th("Nascimentos", className="text-end"),
                    ]
                )
            ),
            html.Tbody(rows),
        ],
        striped=True,
        hover=True,
        size="sm",
        className="mb-0",
    )


def create_layout() -> html.Div:
    """
    Create geographic analysis page layout.

    Returns:
        Dash HTML Div with page layout.
    """
    available_years = sorted(data_loader.get_available_years(), reverse=True)

    # Use INDICATOR_MAPPINGS to create dropdown options, skipping the first item ('birth')
    indicator_options = [{"label": config.absolute_title, "value": key} for key, config in list(INDICATOR_MAPPINGS.items())[1:]]

    return html.Div(
        [
            # Header
            dbc.Row(
                dbc.Col(
                    [
                        html.H1("Análise por Estado (UF)", className="mb-3 text-primary fw-bold"),
                        html.P("Distribuição territorial dos nascimentos e indicadores de saúde perinatal", className="lead mb-2"),
                        html.P(f"Dados disponíveis: {', '.join(map(str, available_years))}", className="text-muted small"),
                    ]
                ),
                className="mb-4",
            ),
            # Controls
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Label("Ano:", className="fw-bold mb-2"),
                            dcc.Dropdown(
                                id="states-year-dropdown",
                                options=[{"label": str(year), "value": year} for year in available_years],
                                value=available_years[0],
                                clearable=False,
                                className="mb-3",
                            ),
                        ],
                        width=12,
                        md=4,
                    ),
                    dbc.Col(
                        [
                            html.Label("Indicador:", className="fw-bold mb-2"),
                            dcc.Dropdown(
                                id="states-indicator-dropdown",
                                options=indicator_options,  # type: ignore
                                value="cesarean",  # Use the key from the mapping
                                clearable=False,
                                className="mb-3",
                            ),
                        ],
                        width=12,
                        md=4,
                    ),
                    dbc.Col(
                        [
                            html.Label("Métrica:", className="fw-bold mb-2"),
                            dcc.Dropdown(
                                id="states-metric-dropdown",
                                options=[
                                    {"label": "Valores Absolutos", "value": "absolute"},
                                    {"label": "Porcentagem (%)", "value": "percentage"},
                                    {"label": "Por 1.000 Habitantes", "value": "per_1k"},
                                ],
                                value="percentage",
                                clearable=False,
                                className="mb-3",
                            ),
                        ],
                        width=12,
                        md=4,
                    ),
                ],
                className="mb-4",
            ),
            # Summary cards
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    html.H6("Maior Valor", className="text-muted mb-2"),
                                    html.H4(id="states-max-card", className="text-success mb-0"),
                                ]
                            ),
                            className="shadow-sm",
                        ),
                        width=6,
                        md=3,
                        className="mb-3",
                    ),
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    html.H6("Menor Valor", className="text-muted mb-2"),
                                    html.H4(id="states-min-card", className="text-danger mb-0"),
                                ]
                            ),
                            className="shadow-sm",
                        ),
                        width=6,
                        md=3,
                        className="mb-3",
                    ),
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    html.H6("Média Nacional", className="text-muted mb-2"),
                                    html.H4(id="states-mean-card", className="text-primary mb-0"),
                                ]
                            ),
                            className="shadow-sm",
                        ),
                        width=6,
                        md=3,
                        className="mb-3",
                    ),
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    html.H6("Desvio Padrão", className="text-muted mb-2"),
                                    html.H4(id="states-std-card", className="text-info mb-0"),
                                ]
                            ),
                            className="shadow-sm",
                        ),
                        width=6,
                        md=3,
                        className="mb-3",
                    ),
                ],
                className="mb-4",
            ),
            # Main content: Map and Rankings
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader(html.H5("🇧🇷 Mapa de Indicadores por Estado", className="mb-0"), className="bg-light"),
                                dbc.CardBody(
                                    dcc.Graph(id="states-choropleth-map", config=CHART_CONFIG, style={"height": "750px"})  # type: ignore
                                ),
                            ],
                            className="shadow-sm",
                        ),
                        width=12,
                        lg=7,
                        className="mb-4",
                    ),
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    dbc.CardHeader(html.H5("🏆 Top 10 Estados (Maior Valor)", className="mb-0"), className="bg-light"),
                                    dbc.CardBody(
                                        html.Div(id="states-top-states-table"),
                                        className="p-2",
                                        style={"maxHeight": "350px", "overflowY": "auto"},
                                    ),
                                ],
                                className="shadow-sm mb-4",
                            ),
                            dbc.Card(
                                [
                                    dbc.CardHeader(html.H5("📉 Bottom 10 Estados (Menor Valor)", className="mb-0"), className="bg-light"),
                                    dbc.CardBody(
                                        html.Div(id="states-bottom-states-table"),
                                        className="p-2",
                                        style={"maxHeight": "350px", "overflowY": "auto"},
                                    ),
                                ],
                                className="shadow-sm",
                            ),
                        ],
                        width=12,
                        lg=5,
                        className="mb-4",
                    ),
                ],
                className="mb-4",
            ),
            # Secondary charts: Regional and Scatter
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader(html.H5("🌎 Comparação por Região", className="mb-0"), className="bg-light"),
                                dbc.CardBody(
                                    dcc.Graph(
                                        id="states-regional-comparison",
                                        config=CHART_CONFIG,  # type: ignore
                                        style={"height": f"{CHART_HEIGHT}px"},  # type: ignore
                                    )
                                ),
                            ],
                            className="shadow-sm",
                        ),
                        width=12,
                        lg=6,
                        className="mb-4",
                    ),
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader(html.H5("🔬 Volume de Nascimentos vs. Indicador", className="mb-0"), className="bg-light"),
                                dbc.CardBody(dcc.Graph(id="states-scatter-plot", config=CHART_CONFIG, style={"height": f"{CHART_HEIGHT}px"})),  # type: ignore
                            ],
                            className="shadow-sm",
                        ),
                        width=12,
                        lg=6,
                        className="mb-4",
                    ),
                ],
                className="mb-4",
            ),
            # Data source footer
            dbc.Row(
                dbc.Col(
                    [
                        html.Hr(),
                        html.P(
                            [
                                html.I(className="fas fa-map-marked-alt me-2"),
                                "Fonte: DATASUS - SINASC | ",
                                "Análise por Unidade Federativa (UF)",
                            ],
                            className="text-muted small text-center",
                        ),
                    ]
                )
            ),
        ],
        className="container-fluid p-4",
    )


def register_callbacks(app):
    """Register callbacks for geographic page."""

    def get_active_indicator(indicator_key: str, metric: str) -> tuple[str, str, str]:
        """
        Determines the correct DataFrame column name based on the selected indicator and metric.
        """
        if indicator_key not in INDICATOR_MAPPINGS:
            indicator = "total_births"  # Fallback

        config = INDICATOR_MAPPINGS[indicator_key]

        if metric == "percentage":
            # Find the corresponding percentage column, usually ending in _pct
            indicator = next((col for col in config.get_relative_columns() if col.endswith("_pct")), config.get_absolute_columns()[0])
            title = config.relative_title
        elif metric == "per_1k":
            # Construct the per_1k column name from the absolute count column
            indicator = config.get_absolute_columns()[0].replace("_count", "_per_1k")
            title = f"{config.absolute_title} por 1.000 Habitantes"
        else:
            indicator = config.get_absolute_columns()[0]
            title = config.absolute_title
        label = config.get_labels()[0]

        return indicator, title, label

    @callback(
        [
            Output("states-max-card", "children"),
            Output("states-min-card", "children"),
            Output("states-mean-card", "children"),
            Output("states-std-card", "children"),
        ],
        [Input("states-year-dropdown", "value"), Input("states-indicator-dropdown", "value"), Input("states-metric-dropdown", "value")],
    )
    def update_summary_cards(year: int, indicator_key: str, metric: str):
        """Update summary statistics cards."""
        df = data_loader.load_monthly_state_aggregates(year, True)
        indicator, _, _ = get_active_indicator(indicator_key, metric)

        if df.empty or indicator not in df.columns:
            return "N/A", "N/A", "N/A", "N/A"

        df["state_name"] = df["state_code"].map(get_state_from_id_code)
        values = df[indicator].dropna()

        if values.empty:
            return "N/A", "N/A", "N/A", "N/A"

        max_val, min_val, mean_val, std_val = values.max(), values.min(), values.mean(), values.std()

        max_state_name = df.iloc[values.argmax()]["state_name"]
        min_state_name = df.iloc[values.argmin()]["state_name"]

        return (
            html.Div(
                [
                    html.Div(format_indicator_value(max_val, metric), className="fw-bold"),
                    html.Small(max_state_name, className="text-muted"),
                ]
            ),
            html.Div(
                [
                    html.Div(format_indicator_value(min_val, metric), className="fw-bold"),
                    html.Small(min_state_name, className="text-muted"),
                ]
            ),
            format_indicator_value(mean_val, metric),
            format_indicator_value(std_val, metric),
        )

    @callback(
        [Output("states-top-states-table", "children"), Output("states-bottom-states-table", "children")],
        Input("states-year-dropdown", "value"),
        Input("states-indicator-dropdown", "value"),
        Input("states-metric-dropdown", "value"),
    )
    def update_ranking_tables(year: int, indicator_key: str, metric: str):
        """Update top 10 and bottom 10 states tables."""
        df = data_loader.load_monthly_state_aggregates(year, True)
        indicator, _, label = get_active_indicator(indicator_key, metric)

        if df.empty or indicator not in df.columns:
            msg = html.P("Indicador não disponível", className="text-muted text-center p-3")
            return msg, msg

        df["state_name"] = df["state_code"].map(get_state_from_id_code)
        top_states = df.nlargest(10, indicator)
        bottom_states = df.nsmallest(10, indicator).sort_values(indicator, ascending=True)

        return _create_ranking_table(top_states, indicator, metric, label), _create_ranking_table(bottom_states, indicator, metric, label)

    @callback(
        Output("states-regional-comparison", "figure"),
        Input("states-year-dropdown", "value"),
        Input("states-indicator-dropdown", "value"),
        Input("states-metric-dropdown", "value"),
    )
    def update_regional_comparison(year: int, indicator_key: str, metric: str):
        """Update regional comparison chart."""
        df = data_loader.load_monthly_state_aggregates(year, True)
        indicator, title, label = get_active_indicator(indicator_key, metric)

        if df.empty or indicator not in df.columns:
            return go.Figure().add_annotation(text="Indicador não disponível", showarrow=False)

        df = df.copy()
        df["region_name"] = df["state_code"].apply(get_region_from_id_code)

        # Weighted average by total_births for percentage and per_1k metrics
        if metric in ["percentage", "per_1k"] and "total_births" in df.columns:
            regional_agg = df.groupby("region_name").apply(
                lambda x: (x[indicator] * x["total_births"]).sum() / x["total_births"].sum(),  # type: ignore
                include_groups=False,  # type: ignore
            )
        else:
            # Simple mean for absolute values
            regional_agg = df.groupby("region_name")[indicator].mean()

        regional_df = regional_agg.reset_index(name=indicator)
        regional_df["formatted_indicator"] = regional_df[indicator].apply(lambda val: format_indicator_value(val, metric))

        return create_colored_bar_chart(
            regional_df,
            "region_name",
            indicator,
            "region_name",
            label,
            "primary",
            "Região",
            y_title=title,
        )

    @callback(
        Output("states-choropleth-map", "figure"),
        Input("states-year-dropdown", "value"),
        Input("states-indicator-dropdown", "value"),
        Input("states-metric-dropdown", "value"),
    )
    def update_choropleth_map(year: int, indicator_key: str, metric: str):
        """Update the choropleth map of Brazil."""
        df = data_loader.load_monthly_state_aggregates(year, True)
        geojson = data_loader.load_geojson_states()
        indicator, title, label = get_active_indicator(indicator_key, metric)

        error_layout = {"xaxis": {"visible": False}, "yaxis": {"visible": False}}
        if df.empty or indicator not in df.columns:
            return {"data": [], "layout": {**error_layout, "annotations": [{"text": "Sem dados para a seleção", "showarrow": False}]}}
        if not geojson or not geojson.get("features"):
            return {"data": [], "layout": {**error_layout, "annotations": [{"text": "Falha ao carregar mapa", "showarrow": False}]}}

        return create_choropleth_chart(
            df,
            geojson,
            indicator,
            color=indicator,
            title="Mapa de Indicadores por Estado",
            color_scale="YlOrRd",
        )

    @callback(
        Output("states-scatter-plot", "figure"),
        Input("states-year-dropdown", "value"),
        Input("states-indicator-dropdown", "value"),
        Input("states-metric-dropdown", "value"),
    )
    def update_scatter_plot(year: int, indicator_key: str, metric: str):
        """Update scatter plot of birth volume vs. indicator."""
        df = data_loader.load_yearly_state_aggregates(True)
        df = df[df["year"] == year]

        indicator, title, label = get_active_indicator(indicator_key, metric)

        if df.empty or indicator not in df.columns or "total_births" not in df.columns:
            return go.Figure().add_annotation(text="Dados insuficientes para o gráfico", showarrow=False)

        return create_state_scatter_plot(df, indicator, title)


# Layout for routing
layout = create_layout()
