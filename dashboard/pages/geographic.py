"""
Geographic Analysis page - Territorial distribution and regional comparisons.

Note: This file uses extended line length (140) for readability of nested Dash components.

This page provides interactive maps and regional analysis of birth data across
Brazilian states and municipalities, enabling geographic pattern identification
and regional health outcome comparisons.
"""

import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from components.charts import format_brazilian_number
from config.geographic import get_region_from_id_code, get_state_from_id_code
from config.settings import CHART_CONFIG, CHART_HEIGHT
from dash import Input, Output, callback, dcc, html
from data.loader import data_loader


def format_indicator_value(value: float, indicator: str) -> str:
    """
    Format indicator value with appropriate units and Brazilian formatting.

    Args:
        value: Numeric value to format
        indicator: Indicator name to determine formatting

    Returns:
        Formatted string with units
    """
    if pd.isna(value):
        return "N/A"

    if "_pct" in indicator or "rate" in indicator.lower():
        return f"{value:.1f}%".replace(".", ",")
    elif "peso" in indicator.lower() or "weight" in indicator.lower():
        return f"{value:.0f}g"
    elif "idade" in indicator.lower() or "age" in indicator.lower():
        return f"{value:.1f} anos".replace(".", ",")
    elif "apgar" in indicator.lower():
        return f"{value:.1f}".replace(".", ",")
    else:
        return format_brazilian_number(value)


def create_layout() -> html.Div:
    """
    Create geographic analysis page layout.

    Returns:
        Dash HTML Div with page layout
    """
    # Get metadata for year selection
    metadata = data_loader.get_metadata()
    available_years = sorted(data_loader.get_available_years(), reverse=True)

    # Indicator options with descriptive labels
    indicator_options = [
        {"label": "Taxa de Cesárea (%)", "value": "cesarean_pct"},
        {"label": "Taxa de Prematuridade (%)", "value": "preterm_pct"},
        {"label": "Taxa de Prematuridade Extrema (%)", "value": "extreme_preterm_pct"},
        {"label": "Taxa de Gravidez na Adolescência (%)", "value": "adolescent_pregnancy_pct"},
        {"label": "Taxa de Baixo Peso ao Nascer (%)", "value": "low_birth_weight_pct"},
        {"label": "Taxa de APGAR5 Baixo (%)", "value": "low_apgar5_pct"},
        {"label": "Taxa de Nascimentos Hospitalares (%)", "value": "hospital_birth_pct"},
        {"label": "Peso Médio ao Nascer (g)", "value": "peso_mean"},
        {"label": "Idade Materna Média (anos)", "value": "idademae_mean"},
        {"label": "APGAR5 Médio", "value": "apgar5_mean"},
    ]

    return html.Div(
        [
            # Header
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.H1("🗺️ Análise Geográfica", className="mb-3 text-primary fw-bold"),
                            html.P(
                                "Distribuição territorial dos nascimentos e indicadores de saúde perinatal",
                                className="lead mb-2",
                            ),
                            html.P(
                                f"Dados disponíveis: {', '.join(map(str, available_years))}",
                                className="text-muted small",
                            ),
                        ]
                    )
                ],
                className="mb-4",
            ),
            # Controls
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Label("Ano:", className="fw-bold mb-2"),
                            dcc.Dropdown(
                                id="geo-year-dropdown",
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
                                id="geo-indicator-dropdown",
                                options=indicator_options,  # type:ignore
                                value="cesarean_pct",
                                clearable=False,
                                className="mb-3",
                            ),
                        ],
                        width=12,
                        md=8,
                    ),
                ],
                className="mb-4",
            ),
            # Removed developer-only UF exclusion control after geometry fix
            # Summary cards
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    html.H6("Maior Valor", className="text-muted mb-2"),
                                    html.H4(id="geo-max-card", className="text-success mb-0"),
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
                                    html.H4(id="geo-min-card", className="text-danger mb-0"),
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
                                    html.H4(id="geo-mean-card", className="text-primary mb-0"),
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
                                    html.H4(id="geo-std-card", className="text-info mb-0"),
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
            # Choropleth Map
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            [
                                dbc.CardHeader(html.H5("🇧🇷 Mapa de Indicadores por Estado", className="mb-0"), className="bg-light"),
                                dbc.CardBody(
                                    dcc.Graph(
                                        id="geo-choropleth-map",
                                        config=CHART_CONFIG,  # type:ignore
                                        style={"height": f"{int(CHART_HEIGHT * 2)}px"},
                                    )
                                ),
                            ],
                            className="shadow-sm",
                        ),
                        width=12,
                    )
                ],
                className="mb-4",
            ),
            # State rankings and regional comparison
            dbc.Row(
                [
                    # Top 10 states
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    dbc.CardHeader(html.H5("📊 Top 10 Estados", className="mb-0"), className="bg-light"),
                                    dbc.CardBody(html.Div(id="geo-top-states-table"), style={"maxHeight": "400px", "overflowY": "auto"}),
                                ],
                                className="shadow-sm",
                            )
                        ],
                        width=12,
                        md=4,
                        className="mb-3",
                    ),
                    # Regional comparison chart
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    dbc.CardHeader(html.H5("🌎 Comparação por Região", className="mb-0"), className="bg-light"),
                                    dbc.CardBody(
                                        [
                                            dcc.Graph(
                                                id="geo-regional-comparison",
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
                        md=8,
                        className="mb-3",
                    ),
                ],
                className="mb-4",
            ),
            # State-level bar chart (full width)
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    dbc.CardHeader(html.H5("📍 Ranking por Estado", className="mb-0"), className="bg-light"),
                                    dbc.CardBody(
                                        [
                                            dcc.Graph(
                                                id="geo-state-ranking-chart",
                                                config=CHART_CONFIG,  # type:ignore
                                                style={"height": f"{int(CHART_HEIGHT * 1.5)}px"},
                                            )
                                        ]
                                    ),
                                ],
                                className="shadow-sm",
                            )
                        ],
                        width=12,
                    )
                ],
                className="mb-4",
            ),
            # Data source footer
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Hr(),
                            html.P(
                                [
                                    html.I(className="fas fa-map-marked-alt me-2"),
                                    "Fonte: DATASUS - SINASC | ",
                                    "Análise por Unidade Federativa (UF) | ",
                                    f"Total de registros: {metadata.get('total_records', 0):,}",
                                ],
                                className="text-muted small text-center",
                            ),
                        ]
                    )
                ]
            ),
        ],
        className="container-fluid p-4",
    )


def register_callbacks(app):
    """Register callbacks for geographic page."""

    @callback(
        [
            Output("geo-max-card", "children"),
            Output("geo-min-card", "children"),
            Output("geo-mean-card", "children"),
            Output("geo-std-card", "children"),
        ],
        [Input("geo-year-dropdown", "value"), Input("geo-indicator-dropdown", "value")],
    )
    def update_summary_cards(year: int, indicator: str):
        """Update summary statistics cards."""
        # Data will be fetched from the new agg_state_yearly table
        df = data_loader.load_yearly_state_aggregates(year)

        if df.empty or indicator not in df.columns:
            return "N/A", "N/A", "N/A", "N/A"

        df["state_code"] = df["state_code"].astype(str).str.zfill(2)
        df["state_name"] = df["state_code"].map(get_state_from_id_code)
        df["region_name"] = df["state_code"].map(get_region_from_id_code)

        values = df[indicator].dropna()
        if values.empty:
            return "N/A", "N/A", "N/A", "N/A"

        max_val = values.max()
        min_val = values.min()
        mean_val = values.mean()
        std_val = values.std()

        max_state_name = df.loc[df[indicator] == max_val, "state_name"].iloc[0]  # type:ignore
        min_state_name = df.loc[df[indicator] == min_val, "state_name"].iloc[0]  # type:ignore

        return (
            html.Div(
                [
                    html.Div(format_indicator_value(max_val, indicator), className="fw-bold"),
                    html.Small(max_state_name, className="text-muted"),
                ]
            ),
            html.Div(
                [
                    html.Div(format_indicator_value(min_val, indicator), className="fw-bold"),
                    html.Small(min_state_name, className="text-muted"),
                ]
            ),
            format_indicator_value(mean_val, indicator),
            format_indicator_value(std_val, indicator),
        )

    @callback(
        Output("geo-top-states-table", "children"),
        [Input("geo-year-dropdown", "value"), Input("geo-indicator-dropdown", "value")],
    )
    def update_top_states_table(year: int, indicator: str):
        """Update top 10 states table."""
        df = data_loader.load_yearly_state_aggregates(year)

        if df.empty or indicator not in df.columns:
            return html.P("Indicador não disponível", className="text-muted text-center")

        df["state_code"] = df["state_code"].astype(str).str.zfill(2)
        df["state_name"] = df["state_code"].map(get_state_from_id_code)
        df["region_name"] = df["state_code"].map(get_region_from_id_code)

        # Sort by indicator (descending) and get top 10
        top_states = df.nlargest(10, indicator)

        # Create table rows
        rows = []
        for _, row in top_states.iterrows():
            state_name = row["state_name"]
            value = row[indicator]
            births = row.get("total_births", 0)

            rows.append(
                html.Tr(
                    [
                        html.Td(html.Strong(state_name), className="text-start"),
                        html.Td(format_indicator_value(value, indicator), className="text-end"),
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
                            html.Th("Valor", className="text-end"),
                            html.Th("Nascimentos", className="text-end"),
                        ]
                    )
                ),
                html.Tbody(rows),
            ],
            striped=True,
            hover=True,
            size="sm",
        )

    @callback(
        Output("geo-regional-comparison", "figure"),
        [Input("geo-year-dropdown", "value"), Input("geo-indicator-dropdown", "value")],
    )
    def update_regional_comparison(year: int, indicator: str):
        """Update regional comparison chart."""
        df = data_loader.load_yearly_state_aggregates(year)

        if df.empty or indicator not in df.columns:
            return go.Figure().add_annotation(
                text="Indicador não disponível",
                xref="paper",
                yref="paper",
                showarrow=False,
            )

        df["state_code"] = df["state_code"].astype(str).str.zfill(2)
        df["state_name"] = df["state_code"].map(get_state_from_id_code)
        df["region_name"] = df["state_code"].map(get_region_from_id_code)

        # Aggregate by region (weighted average by births)
        regional_data = []
        for region_name, group in df.groupby("region_name"):
            if not group.empty:
                # Weighted average
                weights = group["total_births"]
                weighted_value = (group[indicator] * weights).sum() / weights.sum()
                total_births = weights.sum()

                regional_data.append({"region_name": region_name, indicator: weighted_value, "total_births": total_births})

        regional_df = pd.DataFrame(regional_data)

        # Add a formatted text column for the bar labels to ensure correct display
        regional_df["formatted_indicator"] = regional_df[indicator].apply(lambda val: format_indicator_value(val, indicator))

        # Create bar chart
        fig = px.bar(
            regional_df,
            x="region_name",
            y=indicator,
            text="formatted_indicator",
            color="region_name",
            color_discrete_sequence=px.colors.qualitative.Set2,
        )

        # Position the text labels outside the bars
        fig.update_traces(textposition="outside")

        fig.update_layout(
            template="plotly_white",
            showlegend=False,
            xaxis_title="Região",
            yaxis_title="",
            margin=dict(l=40, r=40, t=20, b=40),
            font=dict(family="Inter, sans-serif"),
        )

        return fig

    @callback(
        Output("geo-choropleth-map", "figure"),
        [Input("geo-year-dropdown", "value"), Input("geo-indicator-dropdown", "value")],
    )
    def update_choropleth_map(year: int, indicator: str):
        """Update the choropleth map of Brazil."""
        import plotly.express as px  # Local import to avoid circulars on Dash reload

        # Load data and geojson
        df = data_loader.load_yearly_state_aggregates(year)
        geojson = data_loader._load_brazil_states_geojson()

        # Guard: missing data or indicator
        if df.empty or indicator not in df.columns:
            return {
                "data": [],
                "layout": {
                    "xaxis": {"visible": False},
                    "yaxis": {"visible": False},
                    "annotations": [
                        {
                            "text": "Sem dados para o ano/indicador selecionado",
                            "showarrow": False,
                            "xref": "paper",
                            "yref": "paper",
                            "x": 0.5,
                            "y": 0.5,
                        }
                    ],
                },
            }

        # Guard: geojson failed to load
        if not isinstance(geojson, dict) or not geojson.get("features"):
            return {
                "data": [],
                "layout": {
                    "xaxis": {"visible": False},
                    "yaxis": {"visible": False},
                    "annotations": [
                        {
                            "text": "Falha ao carregar o mapa do Brasil (GeoJSON)",
                            "showarrow": False,
                            "xref": "paper",
                            "yref": "paper",
                            "x": 0.5,
                            "y": 0.5,
                        }
                    ],
                },
            }

        # Ensure state codes are strings with two digits to match GeoJSON properties.id
        df = df.copy()
        if "state_code" in df.columns:
            df["state_code"] = df["state_code"].astype(str).str.zfill(2)

        # Ensure state_name for nicer hover
        if "state_name" not in df.columns:
            df["state_name"] = df["state_code"].apply(get_state_from_id_code)

        if "state_code" not in df.columns:
            return {
                "data": [],
                "layout": {
                    "xaxis": {"visible": False},
                    "yaxis": {"visible": False},
                    "annotations": [
                        {
                            "text": "Coluna state_code ausente nos dados",
                            "showarrow": False,
                            "xref": "paper",
                            "yref": "paper",
                            "x": 0.5,
                            "y": 0.5,
                        }
                    ],
                },
            }

        # Build figure
        is_percent = ("_pct" in indicator) or ("rate" in indicator.lower())
        color_continuous_scale = "YlOrRd" if is_percent else "Blues"

        fig = px.choropleth(
            df,
            geojson=geojson,
            locations="state_code",
            featureidkey="properties.id",  # our GeoJSON has state code under properties.id
            color=indicator,
            color_continuous_scale=color_continuous_scale,
            hover_name="state_name" if "state_name" in df.columns else None,
            hover_data={
                "state_code": True,
                indicator: ":.1f" if is_percent else True,
                "total_births": ":," if "total_births" in df.columns else False,
            },
        )

        # Improve geos rendering and zoom to Brazil bounds
        fig.update_geos(
            fitbounds="locations",
            visible=False,
            projection_type="mercator",
            center=dict(lat=-14.2350, lon=-51.9253),
        )

        # Title and legend formatting
        fig.update_layout(
            template="plotly_white",
            margin=dict(l=10, r=10, t=20, b=10),
            coloraxis_colorbar=dict(
                title="%" if is_percent else "",
                ticksuffix="%" if is_percent else "",
            ),
            font=dict(family="Inter, sans-serif"),
        )

        return fig

    @callback(
        Output("geo-state-ranking-chart", "figure"),
        [Input("geo-year-dropdown", "value"), Input("geo-indicator-dropdown", "value")],
    )
    def update_state_ranking_chart(year: int, indicator: str):
        """Update state ranking horizontal bar chart."""
        df = data_loader.load_yearly_state_aggregates(year)

        if df.empty or indicator not in df.columns:
            return go.Figure().add_annotation(
                text="Indicador não disponível",
                xref="paper",
                yref="paper",
                showarrow=False,
            )

        df["state_code"] = df["state_code"].astype(str).str.zfill(2)
        df["state_name"] = df["state_code"].map(get_state_from_id_code)
        df["region_name"] = df["state_code"].map(get_region_from_id_code)

        df_sorted = df.sort_values(indicator, ascending=True)

        # Create horizontal bar chart
        fig = px.bar(
            df_sorted,
            y="state_name",
            x=indicator,
            orientation="h",
            color="region_name",
            color_discrete_sequence=px.colors.qualitative.Set2,
            hover_data={"total_births": ":,"},
        )

        fig.update_layout(
            template="plotly_white",
            xaxis_title="",
            yaxis_title="",
            showlegend=True,
            legend=dict(title="Região", orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=100, r=40, t=40, b=40),
            font=dict(family="Inter, sans-serif"),
        )

        return fig


# Layout for routing
layout = create_layout()
