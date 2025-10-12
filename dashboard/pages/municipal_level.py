"""
Municipal-Level Geographic Analysis page - Detailed municipality birth statistics.

This page provides interactive analysis of birth data at the municipal level,
enabling detailed examination of health outcomes within selected states,
with month-by-month trends and municipality comparisons.
"""

import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go
from components import (
    calculate_metric_column,
    create_ranking_bar_chart,
    format_brazilian_number,
    format_indicator_value,
)
from config.constants import GEOGRAPHIC_INDICATORS
from config.settings import CHART_CONFIG, CHART_HEIGHT
from dash import Input, Output, callback, dcc, html
from data.loader import data_loader

# Generate indicator options dynamically from configuration
INDICATOR_OPTIONS = []
for key, config in GEOGRAPHIC_INDICATORS.items():
    # Add absolute count option
    INDICATOR_OPTIONS.append({"label": config.absolute_title, "value": config.get_absolute_columns()[0]})


def create_layout() -> html.Div:
    """
    Create municipal analysis page layout.

    Returns:
        Dash HTML Div with page layout
    """
    metadata = data_loader.get_metadata()
    available_years = sorted(data_loader.get_available_years(), reverse=True)

    # Get state options sorted by name
    state_mapping = data_loader.load_state_id_mapping()
    state_options = [{"label": name, "value": code} for code, name in sorted(state_mapping.items(), key=lambda x: x[1])]  # type: ignore

    return html.Div(
        [
            # Header
            dbc.Row(
                dbc.Col(
                    [
                        html.H1("🏘️ Análise Municipal", className="mb-3 text-primary fw-bold"),
                        html.P(
                            "Análise detalhada por município dentro de cada estado, com tendências mensais e comparações de indicadores",
                            className="lead mb-2",
                        ),
                        html.P(f"Dados disponíveis: {', '.join(map(str, available_years))}", className="text-muted small"),
                    ]
                ),
                className="mb-4",
            ),
            # Hidden data store for sharing data between callbacks
            dcc.Store(id="municipal-data-store", data=None),
            dcc.Store(id="municipal-processed-store", data=None),
            # Controls
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Label("Estado:", className="fw-bold mb-2"),
                            dcc.Dropdown(
                                id="municipal-state-dropdown",
                                options=state_options,  # type: ignore
                                value=state_options[14]["value"],
                                placeholder="Selecione um Estado",
                                clearable=False,
                                className="mb-3",
                            ),
                        ],
                        width=12,
                        md=3,
                    ),
                    dbc.Col(
                        [
                            html.Label("Ano:", className="fw-bold mb-2"),
                            dcc.Dropdown(
                                id="municipal-year-dropdown",
                                options=[{"label": str(year), "value": year} for year in available_years],
                                value=available_years[0],
                                clearable=False,
                                className="mb-3",
                            ),
                        ],
                        width=12,
                        md=3,
                    ),
                    dbc.Col(
                        [
                            html.Label("Indicador:", className="fw-bold mb-2"),
                            dcc.Dropdown(
                                id="municipal-indicator-dropdown",
                                options=INDICATOR_OPTIONS,  # type: ignore
                                value=INDICATOR_OPTIONS[0]["value"] if INDICATOR_OPTIONS else "cesarean_pct",
                                clearable=False,
                                className="mb-3",
                            ),
                        ],
                        width=12,
                        md=3,
                    ),
                    dbc.Col(
                        [
                            html.Label("Métrica do Mapa:", className="fw-bold mb-2"),
                            dcc.Dropdown(
                                id="municipal-metric-type-dropdown",
                                options=[
                                    {"label": "Valores Absolutos", "value": "absolute"},
                                    {"label": "Percentual", "value": "percentage"},
                                    {"label": "Por 1.000 Habitantes", "value": "per_1k"},
                                ],
                                value="per_1k",
                                className="mb-3",
                            ),
                        ],
                        width=12,
                        md=3,
                    ),
                ],
                className="mb-4",
            ),
            # Map metric type selector
            dbc.Row(
                className="mb-4",
            ),
            # Summary Cards
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    html.H6("Nascimentos no Estado", className="text-muted mb-2"),
                                    html.H4(id="municipal-births-card", className="text-primary mb-0"),
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
                                    html.H6("Municípios", className="text-muted mb-2"),
                                    html.H4(id="municipal-count-card", className="text-info mb-0"),
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
                                    html.H6(id="municipal-indicator-label", className="text-muted mb-2"),
                                    html.H4(id="municipal-indicator-card", className="text-success mb-0"),
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
                                    html.H6("Variação", className="text-muted mb-2"),
                                    html.H4(id="municipal-std-card", className="text-warning mb-0"),
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
            # Rankings
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader(html.H5("🏆 Top 10 Municípios (Maior Valor)", className="mb-0"), className="bg-light"),
                                dbc.CardBody(
                                    dcc.Loading(
                                        dcc.Graph(
                                            id="municipal-top-ranking",
                                            config=CHART_CONFIG,  # type:ignore
                                            style={"height": f"{CHART_HEIGHT}px"},
                                        ),
                                        type="default",
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
                                dbc.CardHeader(html.H5("📉 Top 10 Municípios (Menor Valor)", className="mb-0"), className="bg-light"),
                                dbc.CardBody(
                                    dcc.Loading(
                                        dcc.Graph(
                                            id="municipal-bottom-ranking",
                                            config=CHART_CONFIG,  # type:ignore
                                            style={"height": f"{CHART_HEIGHT}px"},
                                        ),
                                        type="default",
                                    )
                                ),
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
            # Map
            dbc.Row(
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardHeader(html.H5("🗺️ Mapa Municipal", className="mb-0"), className="bg-light"),
                            dbc.CardBody(
                                dcc.Loading(
                                    dcc.Graph(
                                        id="municipal-choropleth-map",
                                        config=CHART_CONFIG,  # type:ignore
                                        style={"height": "750px"},
                                    ),
                                    type="default",
                                )
                            ),
                        ],
                        className="shadow-sm",
                    ),
                    width=12,
                    className="mb-4",
                ),
                className="mb-4",
            ),
            # Data source footer
            dbc.Row(
                dbc.Col(
                    [
                        html.Hr(),
                        html.P(
                            [
                                html.I(className="fas fa-city me-2"),
                                "Fonte: DATASUS - SINASC | ",
                                "Análise por Município | ",
                                f"Total de registros: {metadata.get('total_records', 0):,}",
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
    """Register callbacks for municipal page."""

    @callback(
        Output("municipal-data-store", "data"),
        [
            Input("municipal-state-dropdown", "value"),
            Input("municipal-year-dropdown", "value"),
        ],
    )
    def load_municipal_data(state_code: str | None, year: int):
        """Load and cache municipality data for the selected state and year."""
        if not state_code:
            return None

        try:
            df = data_loader.load_yearly_municipality_aggregates(year, state_code, True)
            df = df[df["total_births"].fillna(0) > 0]
            df["municipality_name"] = df["municipality_code"].map(data_loader.load_municipality_id_mapping())

            # Convert to dict for storage (only essential columns to reduce memory)
            essential_cols = [
                "municipality_code",
                "municipality_name",
                "total_births",
                "population",
                "cesarean_count",
                "preterm_count",
                "extreme_preterm_count",
                "low_birth_weight_count",
                "low_apgar5_count",
                "adolescent_pregnancy_count",
            ]

            # Only keep columns that exist in the dataframe
            cols_to_keep = [col for col in essential_cols if col in df.columns]
            return df[cols_to_keep].to_dict("records")
        except Exception as e:
            raise ValueError("Exception during data load", e)

    @callback(
        Output("municipal-processed-store", "data"),
        [
            Input("municipal-data-store", "data"),
            Input("municipal-indicator-dropdown", "value"),
            Input("municipal-metric-type-dropdown", "value"),
        ],
    )
    def process_municipal_data(data, indicator: str, metric_type: str):
        """Process data with selected indicator and metric type."""
        if not data:
            return None

        try:
            df = pd.DataFrame(data)
            if df.empty:
                return None

            # Calculate metric column
            metric_column, metric_suffix = calculate_metric_column(df, indicator, metric_type)

            # Return processed data with metric
            result = {"metric_column": metric_column, "metric_suffix": metric_suffix, "data": df.to_dict("records")}
            return result
        except Exception:
            return None

    @callback(
        [
            Output("municipal-births-card", "children"),
            Output("municipal-count-card", "children"),
            Output("municipal-indicator-label", "children"),
            Output("municipal-indicator-card", "children"),
            Output("municipal-std-card", "children"),
        ],
        [
            Input("municipal-processed-store", "data"),
            Input("municipal-state-dropdown", "value"),
            Input("municipal-indicator-dropdown", "value"),
        ],
    )
    def update_summary_cards(processed_data, state_code: str | None, indicator: str):
        """Update summary cards with key metrics."""
        if not processed_data or not state_code:
            return "N/A", "N/A", "Selecione Estado", "N/A", "N/A"

        try:
            df = pd.DataFrame(processed_data["data"])
            metric_column = processed_data["metric_column"]
            metric_suffix = processed_data["metric_suffix"]

            if df.empty:
                return "N/A", "N/A", "Sem Dados", "N/A", "N/A"

            # Get labels
            state_mapping = data_loader.load_state_id_mapping()
            state_name = state_mapping.get(state_code, "Estado")
            indicator_labels = {opt["value"]: opt["label"] for opt in INDICATOR_OPTIONS}
            indicator_label = indicator_labels.get(indicator, indicator).replace("(%)", "").strip() + metric_suffix

            # Calculate statistics
            total_births = df["total_births"].sum()
            total_mun = df["municipality_code"].nunique()

            # Calculate state-level metric (weighted average by births)
            if "total_births" in df.columns and total_births > 0:
                state_indicator_value = (df[metric_column] * df["total_births"]).sum() / total_births
            else:
                state_indicator_value = df[metric_column].mean()

            std_value = df[metric_column].std()

            return (
                format_brazilian_number(total_births),
                str(total_mun),
                f"{indicator_label} - {state_name}",
                format_indicator_value(state_indicator_value, metric_column if metric_column == "metric_value" else indicator),
                format_indicator_value(std_value, metric_column if metric_column == "metric_value" else indicator),
            )

        except Exception as e:
            return "Erro", "Erro", "Erro", str(e)[:50], "Erro"

    @callback(
        [
            Output("municipal-top-ranking", "figure"),
            Output("municipal-bottom-ranking", "figure"),
        ],
        [
            Input("municipal-processed-store", "data"),
            Input("municipal-indicator-dropdown", "value"),
        ],
    )
    def update_ranking_charts(processed_data, indicator: str):
        """Update ranking charts."""
        if not processed_data:
            empty_fig = go.Figure().add_annotation(text="Carregando...", showarrow=False)
            return empty_fig, empty_fig

        try:
            df = pd.DataFrame(processed_data["data"])
            df = df[df[indicator].notna() & (df[indicator] != 0)]

            metric_column = processed_data["metric_column"]
            metric_suffix = processed_data["metric_suffix"]

            if df.empty or len(df) < 3:
                empty_fig = go.Figure().add_annotation(text="Sem dados suficientes", showarrow=False)
                return empty_fig, empty_fig

            # Get labels
            indicator_labels = {opt["value"]: opt["label"] for opt in INDICATOR_OPTIONS}
            indicator_label = indicator_labels.get(indicator, indicator).replace("(%)", "").strip() + metric_suffix

            # Get top and bottom municipalities
            actual_n = min(10, len(df))
            top_n_mun = df.nlargest(actual_n, metric_column)[["municipality_name", metric_column, "total_births"]]
            bottom_n_mun = df.nsmallest(actual_n, metric_column)[["municipality_name", metric_column, "total_births"]]

            # Create figures
            top_fig = _create_municipality_ranking_figure(top_n_mun, metric_column, indicator_label, ascending=False)
            bottom_fig = _create_municipality_ranking_figure(bottom_n_mun, metric_column, indicator_label, ascending=True)

            return top_fig, bottom_fig

        except Exception as e:
            error_fig = go.Figure().add_annotation(text=f"Erro: {str(e)[:100]}", showarrow=False)
            return error_fig, error_fig

    @callback(
        Output("municipal-choropleth-map", "figure"),
        [
            Input("municipal-processed-store", "data"),
            Input("municipal-state-dropdown", "value"),
            Input("municipal-indicator-dropdown", "value"),
        ],
    )
    def update_choropleth_map(processed_data, state_code: str | None, indicator: str):
        """Update choropleth map."""
        if not processed_data or not state_code:
            return go.Figure().add_annotation(text="Carregando...", showarrow=False)

        try:
            df = pd.DataFrame(processed_data["data"])
            metric_column = processed_data["metric_column"]
            metric_suffix = processed_data["metric_suffix"]

            if df.empty or len(df) < 3:
                return go.Figure().add_annotation(text="Sem dados suficientes", showarrow=False)

            # Get labels
            indicator_labels = {opt["value"]: opt["label"] for opt in INDICATOR_OPTIONS}
            indicator_label = indicator_labels.get(indicator, indicator).replace("(%)", "").strip() + metric_suffix

            # Create map figure
            return _create_municipal_map_figure(df, state_code, metric_column, indicator_label)

        except Exception as e:
            return go.Figure().add_annotation(text=f"Erro: {str(e)[:100]}", showarrow=False)


def _create_municipality_ranking_figure(df: pd.DataFrame, indicator: str, indicator_label: str, ascending: bool = False) -> go.Figure:
    """
    Create a horizontal bar chart for municipality rankings.

    Args:
        df: DataFrame with municipality data
        indicator: Indicator column name
        indicator_label: Human-readable label for the indicator
        ascending: If True, show highest values at top (sorts descending for plotly display)

    Returns:
        Plotly Figure object
    """
    df = df.sort_values(by=indicator, ascending=not ascending)

    return create_ranking_bar_chart(
        df=df,
        x_col=indicator,
        y_col="municipality_name",
        x_title=indicator_label,
        y_title="",
        text_formatter=lambda x: format_indicator_value(x, indicator),
        orientation="h",
        color="primary",
        height=None,
    )


def _create_municipal_map_figure(df: pd.DataFrame, state_code: str, indicator: str, indicator_label: str) -> go.Figure:
    """
    Create a choropleth map of municipalities within a state, showing municipalities
    with missing indicator values in a distinct (gray) style and a hover "Sem dados".
    """
    import plotly.graph_objects as go

    # Load state-filtered GeoJSON
    geojson_data = data_loader.load_geojson_municipalities(limiter=state_code)

    if not geojson_data or not geojson_data.get("features"):
        return go.Figure().add_annotation(text="Dados geográficos não disponíveis", showarrow=False)

    # Build a DataFrame of all municipality ids from the GeoJSON so we include municipalities without data
    all_mun_codes = [feat["properties"]["id"] for feat in geojson_data["features"]]
    full_df = pd.DataFrame({"municipality_code": all_mun_codes})

    # Merge provided data (may have only some municipalities) into the full list
    merged = full_df.merge(df, how="left", on="municipality_code")
    merged["municipality_name"] = merged["municipality_code"].map(data_loader.load_municipality_id_mapping())

    # Prepare masks
    valid_mask = merged[indicator].notna()
    valid_df = merged[valid_mask]
    missing_df = merged[~valid_mask]

    # If nothing to show at all
    if (valid_df.empty and missing_df.empty) or len(merged) == 0:
        return go.Figure().add_annotation(text="Sem dados suficientes", showarrow=False)

    fig = go.Figure()

    # Add a trace for municipalities that have values (continuous color)
    if not valid_df.empty:
        fig.add_trace(
            go.Choropleth(
                geojson=geojson_data,
                locations=valid_df["municipality_code"],
                z=valid_df[indicator],
                featureidkey="properties.id",
                colorscale="RdYlGn_r" if "_pct" in indicator else "Blues",
                colorbar=dict(title=indicator_label),
                hovertemplate=(
                    f"<b>%{{customdata[0]}}</b><br>{indicator_label}: %{{z:.2f}}<br>Nascimentos: %{{customdata[1]:,}}<extra></extra>"
                ),
                customdata=list(
                    zip(valid_df.get("municipality_name", valid_df["municipality_code"]), valid_df.get("total_births", [None] * len(valid_df)))
                ),
                zmin=valid_df[indicator].min(),
                zmax=valid_df[indicator].max(),
                showscale=True,
            )
        )

    # Add a trace for municipalities with missing values (solid gray fill, no colorbar)
    if not missing_df.empty:
        fig.add_trace(
            go.Choropleth(
                geojson=geojson_data,
                locations=missing_df["municipality_code"],
                z=[0] * len(missing_df),  # dummy z
                featureidkey="properties.id",
                colorscale=[[0, "#e0e0e0"], [1, "#e0e0e0"]],  # flat gray
                showscale=False,
                hovertemplate="<b>%{customdata[0]}</b><br>Sem dados<extra></extra>",
                customdata=list(zip(missing_df.get("municipality_name", missing_df["municipality_code"]))),
            )
        )

    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0}, height=750)

    return fig


# Layout for routing
layout = create_layout()
