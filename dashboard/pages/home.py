"""
Home page - Multi-year comparison and overview statistics.
"""

import dash_bootstrap_components as dbc
import plotly.express as px
from config.settings import (
    CHART_CONFIG,
    CHART_HEIGHT,
    COLOR_PALETTE,
    COMMON_LAYOUT,
    LEGEND_CONFIG,
    TEMPLATE,
)
from dash import Input, Output, dcc, html
from data.loader import data_loader


def create_year_summary_card(year: int, summary: dict) -> dbc.Card:
    """
    Create a card summarizing a specific year's statistics.

    Args:
        year: Year number
        summary: Dictionary with year summary data

    Returns:
        Bootstrap Card component
    """
    # Format numbers with Brazilian format (dots as thousands separator)
    total_births = summary.get("total_births", 0)
    formatted_births = f"{total_births:_}".replace("_", ".")

    # Get statistics - prioritizing rates (quality indicators)
    low_birth_weight_rate = summary.get("health_indicators", {}).get("low_birth_weight_pct", 0)
    adolescent_pregnancy_rate = summary.get("pregnancy", {}).get("adolescent_pregnancy_pct", 0)
    low_apgar5_rate = summary.get("health_indicators", {}).get("low_apgar5_pct", 0)
    cesarean_rate = summary.get("delivery_type", {}).get("cesarean_rate_pct", 0)
    preterm_rate = summary.get("pregnancy", {}).get("preterm_birth_pct", 0)
    hospital_rate = summary.get("location", {}).get("hospital_birth_pct", 0)

    return dbc.Card(
        [
            dbc.CardHeader(html.H3(f"📅 {year}", className="mb-0 text-center fw-bold"), className="bg-primary text-white py-3"),
            dbc.CardBody(
                [
                    # Total births - destacado
                    html.Div(
                        [
                            html.I(className="fas fa-baby fa-2x text-primary mb-2"),
                            html.H3(formatted_births, className="text-primary fw-bold mb-1"),
                            html.P("Nascimentos Totais", className="text-muted mb-0 small"),
                        ],
                        className="text-center mb-3 pb-3 border-bottom",
                    ),
                    # Metrics in two columns - Quality indicators prioritized
                    dbc.Row(
                        [
                            # Left column - Health quality indicators
                            dbc.Col(
                                [
                                    # Low birth weight rate
                                    html.Div(
                                        [
                                            html.I(className="fas fa-weight-hanging text-warning me-1", style={"fontSize": "14px"}),
                                            html.Strong("Baixo Peso: ", className="small"),
                                            html.Span("_", className="text-white"),  # Spacer
                                            html.Span(f"{low_birth_weight_rate:.1f}%".replace(".", ","), className="small text-muted"),
                                        ],
                                        className="mb-2 d-flex align-items-center",
                                    ),
                                    # Adolescent pregnancy rate
                                    html.Div(
                                        [
                                            html.I(className="fas fa-user-friends text-info me-1", style={"fontSize": "14px"}),
                                            html.Strong("Adolescentes: ", className="small"),
                                            html.Span("_", className="text-white"),  # Spacer
                                            html.Span(f"{adolescent_pregnancy_rate:.1f}%".replace(".", ","), className="small text-muted"),
                                        ],
                                        className="mb-2 d-flex align-items-center",
                                    ),
                                    # Low APGAR5 rate
                                    html.Div(
                                        [
                                            html.I(className="fas fa-heartbeat text-danger me-1", style={"fontSize": "14px"}),
                                            html.Strong("APGAR5 Baixo: ", className="small"),
                                            html.Span("_", className="text-white"),  # Spacer
                                            html.Span(f"{low_apgar5_rate:.1f}%".replace(".", ","), className="small text-muted"),
                                        ],
                                        className="mb-0 d-flex align-items-center",
                                    ),
                                ],
                                width=6,
                            ),
                            # Right column - Process and coverage indicators
                            dbc.Col(
                                [
                                    # Cesarean rate
                                    html.Div(
                                        [
                                            html.I(className="fas fa-procedures text-warning me-1", style={"fontSize": "14px"}),
                                            html.Strong("Cesárea: ", className="small"),
                                            html.Span("_", className="text-white"),  # Spacer
                                            html.Span(f"{cesarean_rate:.1f}%".replace(".", ","), className="small text-muted"),
                                        ],
                                        className="mb-2 d-flex align-items-center",
                                    ),
                                    # Preterm rate
                                    html.Div(
                                        [
                                            html.I(className="fas fa-exclamation-triangle text-danger me-1", style={"fontSize": "14px"}),
                                            html.Strong("Prematuros: ", className="small"),
                                            html.Span("_", className="text-white"),  # Spacer
                                            html.Span(f"{preterm_rate:.1f}%".replace(".", ","), className="small text-muted"),
                                        ],
                                        className="mb-2 d-flex align-items-center",
                                    ),
                                    # Hospital births
                                    html.Div(
                                        [
                                            html.I(className="fas fa-hospital text-primary me-1", style={"fontSize": "14px"}),
                                            html.Strong("Hospitalar: ", className="small"),
                                            html.Span("_", className="text-white"),  # Spacer
                                            html.Span(f"{hospital_rate:.1f}%".replace(".", ","), className="small text-muted"),
                                        ],
                                        className="mb-0 d-flex align-items-center",
                                    ),
                                ],
                                width=6,
                            ),
                        ],
                        className="g-2",
                    ),
                ]
            ),
        ],
        className="shadow h-100",
    )


def create_layout() -> html.Div:
    """
    Create home page layout with multi-year comparison.

    Returns:
        Dash HTML Div with page layout
    """
    # Get metadata
    metadata = data_loader.get_metadata()
    available_years = sorted(data_loader.get_available_years(), reverse=True)  # Most recent first

    # Create year summary cards
    year_cards = []
    for year in available_years:
        summary = data_loader.get_year_summary(year)
        year_cards.append(
            dbc.Col(
                create_year_summary_card(year, summary),
                width=12,
                md=6,
                lg=4,
                className="mb-3",
            )
        )

    return html.Div(
        [
            # Header
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Div(
                                [
                                    html.H1("📊 SINASC Dashboard", className="mb-2 text-primary fw-bold"),
                                    html.P("Sistema de Informações sobre Nascidos Vivos - Visão Geral", className="lead text-muted mb-1"),
                                    html.P("Análise Comparativa entre Anos", className="text-muted"),
                                ],
                                className="text-center mb-4",
                            )
                        ]
                    )
                ]
            ),
            # Year summary cards carousel
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.H4("📅 Resumo por Ano", className="mb-3 fw-bold text-secondary"),
                        ]
                    )
                ]
            ),
            dbc.Row(year_cards, className="mb-5"),
            # Comparative charts
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.H4("📈 Análise Temporal", className="mb-3 fw-bold text-secondary"),
                        ]
                    )
                ]
            ),
            # Main evolution chart - full width
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    dbc.CardHeader(html.H5("Evolução do Total de Nascimentos", className="mb-0"), className="bg-light"),
                                    dbc.CardBody(
                                        [
                                            dcc.Graph(
                                                id="home-births-evolution",
                                                config=CHART_CONFIG,  # type:ignore
                                                style={"height": f"{int(CHART_HEIGHT * 1.2)}px"},
                                            )
                                        ]
                                    ),
                                ],
                                className="shadow-sm",
                            )
                        ]
                    )
                ],
                className="mb-4",
            ),
            # Cesarean section charts
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    dbc.CardHeader(html.H5("Número Absoluto de Cesáreas", className="mb-0"), className="bg-light"),
                                    dbc.CardBody(
                                        [
                                            dcc.Graph(
                                                id="home-absolute-cesarean-comparison",
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
                        md=6,
                        className="mb-3",
                    ),
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    dbc.CardHeader(html.H5("Taxa de Cesáreas", className="mb-0"), className="bg-light"),
                                    dbc.CardBody(
                                        [
                                            dcc.Graph(
                                                id="home-relative-cesarean-comparison",
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
                        md=6,
                        className="mb-3",
                    ),
                ],
                className="mb-4",
            ),
            # Preterm births charts
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    dbc.CardHeader(html.H5("Nascimentos Prematuros", className="mb-0"), className="bg-light"),
                                    dbc.CardBody(
                                        [
                                            dcc.Graph(
                                                id="home-absolute-preterm-comparison",
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
                        md=6,
                        className="mb-3",
                    ),
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    dbc.CardHeader(html.H5("Taxa de Prematuridade", className="mb-0"), className="bg-light"),
                                    dbc.CardBody(
                                        [
                                            dcc.Graph(
                                                id="home-relative-preterm-comparison",
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
                        md=6,
                        className="mb-3",
                    ),
                ],
                className="mb-4",
            ),
            # Adolescent pregnancy charts
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    dbc.CardHeader(html.H5("Gestações em Adolescentes", className="mb-0"), className="bg-light"),
                                    dbc.CardBody(
                                        [
                                            dcc.Graph(
                                                id="home-absolute-adolescent-comparison",
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
                        md=6,
                        className="mb-3",
                    ),
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    dbc.CardHeader(html.H5("Taxa de Gravidez na Adolescência", className="mb-0"), className="bg-light"),
                                    dbc.CardBody(
                                        [
                                            dcc.Graph(
                                                id="home-relative-adolescent-comparison",
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
                        md=6,
                        className="mb-3",
                    ),
                ],
                className="mb-4",
            ),
            # Low birth weight charts
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    dbc.CardHeader(html.H5("Baixo Peso ao Nascer (<2.500g)", className="mb-0"), className="bg-light"),
                                    dbc.CardBody(
                                        [
                                            dcc.Graph(
                                                id="home-absolute-low-weight-comparison",
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
                        md=6,
                        className="mb-3",
                    ),
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    dbc.CardHeader(html.H5("Taxa de Baixo Peso ao Nascer", className="mb-0"), className="bg-light"),
                                    dbc.CardBody(
                                        [
                                            dcc.Graph(
                                                id="home-relative-low-weight-comparison",
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
                        md=6,
                        className="mb-3",
                    ),
                ],
                className="mb-4",
            ),
            # Low APGAR5 charts
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    dbc.CardHeader(html.H5("APGAR5 Baixo (<7)", className="mb-0"), className="bg-light"),
                                    dbc.CardBody(
                                        [
                                            dcc.Graph(
                                                id="home-absolute-low-apgar-comparison",
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
                        md=6,
                        className="mb-3",
                    ),
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    dbc.CardHeader(html.H5("Taxa de APGAR5 Baixo", className="mb-0"), className="bg-light"),
                                    dbc.CardBody(
                                        [
                                            dcc.Graph(
                                                id="home-relative-low-apgar-comparison",
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
                        md=6,
                        className="mb-3",
                    ),
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
            ),
        ],
        className="container-fluid p-4",
    )


def register_callbacks(app):
    """Register callbacks for home page."""

    @app.callback(
        Output("home-births-evolution", "figure"),
        Input("url", "pathname"),  # Trigger on page load
    )
    def update_births_evolution(_):
        """Update births evolution chart with text inside bars."""
        import plotly.graph_objects as go

        # Load yearly aggregates
        df = data_loader.load_yearly_aggregates()

        fig = go.Figure()

        fig.add_trace(
            go.Bar(
                x=df["year"],
                y=df["total_births"],
                text=[f"{int(val):_}".replace("_", ".") for val in df["total_births"]],
                textposition="inside",
                marker_color=COLOR_PALETTE["primary"],
                name="Nascimentos",
                textfont=dict(size=12, color="white"),
            )
        )

        fig.update_layout(
            **COMMON_LAYOUT,
            xaxis_title="Ano",
            yaxis_title="Número de Nascimentos",
            showlegend=False,
            yaxis=dict(rangemode="tozero"),
        )

        return fig

    @app.callback(Output("home-absolute-cesarean-comparison", "figure"), Input("url", "pathname"))
    def update_absolute_cesarean_comparison(_):
        """Update indicators comparison chart with cesarean absolute values."""
        import plotly.graph_objects as go

        df = data_loader.load_yearly_aggregates()

        # Calculate absolute cesarean count if not present
        if "cesarean_count" not in df.columns:
            df["cesarean_count"] = (df["total_births"] * df["cesarean_rate_pct"] / 100).round().astype(int)

        fig = go.Figure()

        fig.add_trace(
            go.Bar(
                x=df["year"],
                y=df["cesarean_count"],
                text=[f"{int(val):_}".replace("_", ".") for val in df["cesarean_count"]],
                textposition="inside",
                marker_color=COLOR_PALETTE["warning"],
                textfont=dict(size=12, color="white"),
            )
        )

        fig.update_layout(
            **COMMON_LAYOUT,
            xaxis_title="Ano",
            yaxis_title="Número de Cesáreas",
            showlegend=False,
            yaxis=dict(rangemode="tozero"),
        )

        return fig

    @app.callback(Output("home-relative-cesarean-comparison", "figure"), Input("url", "pathname"))
    def update_cesarean_comparison(_):
        """Update cesarean rate comparison chart."""
        df = data_loader.load_yearly_aggregates()

        fig = px.line(
            df,
            x="year",
            y="cesarean_rate_pct",
            labels={"year": "Ano", "cesarean_rate_pct": "Taxa (%)"},
            template=TEMPLATE,
            markers=True,
            color_discrete_sequence=[COLOR_PALETTE["warning"]],
        )

        fig.update_traces(line=dict(width=3), marker=dict(size=10))

        fig.update_layout(
            **COMMON_LAYOUT,
            xaxis_title="Ano",
            yaxis_title="Taxa de Cesárea (%)",
            showlegend=False,
            yaxis=dict(rangemode="tozero"),
            margin=dict(r=125),  # Right margin for annotation text
        )

        # Add reference line at 15% (WHO recommendation)
        fig.add_hline(
            y=15, line_dash="dash", line_color=COLOR_PALETTE["danger"], annotation_text="Recomendação OMS", annotation_position="right"
        )

        return fig

    @app.callback(Output("home-absolute-preterm-comparison", "figure"), Input("url", "pathname"))
    def update_preterm_absolute(_):
        """Update preterm births absolute count chart with stacked bars."""
        df = data_loader.load_yearly_aggregates()

        # Calculate non-extreme preterm (preterm but not extreme)
        df["moderate_preterm_count"] = df["preterm_birth_count"] - df["extreme_preterm_birth_count"]

        # Create stacked bar chart
        import plotly.graph_objects as go

        fig = go.Figure()

        # Add moderate preterm
        fig.add_trace(
            go.Bar(
                x=df["year"],
                y=df["moderate_preterm_count"],
                name="Prematuros Moderados (32-36 sem)",
                marker_color=COLOR_PALETTE["warning"],
                text=[f"{int(val):_}".replace("_", ".") for val in df["moderate_preterm_count"]],
                textposition="inside",
                textfont=dict(size=11, color="white"),
            )
        )

        # Add extreme preterm
        fig.add_trace(
            go.Bar(
                x=df["year"],
                y=df["extreme_preterm_birth_count"],
                name="Prematuros Extremos (<32 sem)",
                marker_color=COLOR_PALETTE["danger"],
                text=[f"{int(val):_}".replace("_", ".") for val in df["extreme_preterm_birth_count"]],
                textposition="outside",
                textfont=dict(size=11),
            )
        )

        # Calculate max value for y-axis with padding for outside text
        max_value = df["preterm_birth_count"].max()
        y_axis_max = max_value * 1.25  # 25% padding above for outside text

        fig.update_layout(
            **COMMON_LAYOUT,
            xaxis_title="Ano",
            yaxis_title="Número de Nascimentos Prematuros",
            barmode="stack",
            yaxis=dict(range=[0, y_axis_max]),
            legend=LEGEND_CONFIG,
        )

        return fig

    @app.callback(Output("home-relative-preterm-comparison", "figure"), Input("url", "pathname"))
    def update_preterm_rate(_):
        """Update preterm birth rate chart with multiple lines."""
        df = data_loader.load_yearly_aggregates()

        import plotly.graph_objects as go

        fig = go.Figure()

        # Add total preterm line
        fig.add_trace(
            go.Scatter(
                x=df["year"],
                y=df["preterm_birth_pct"],
                mode="lines+markers",
                name="Prematuros Total (<37 sem)",
                line=dict(color=COLOR_PALETTE["warning"], width=3),
                marker=dict(size=10),
            )
        )

        # Add extreme preterm line
        fig.add_trace(
            go.Scatter(
                x=df["year"],
                y=df["extreme_preterm_birth_pct"],
                mode="lines+markers",
                name="Prematuros Extremos (<32 sem)",
                line=dict(color=COLOR_PALETTE["danger"], width=3),
                marker=dict(size=10),
            )
        )

        fig.update_layout(
            **COMMON_LAYOUT,
            xaxis_title="Ano",
            yaxis_title="Taxa de Prematuridade (%)",
            yaxis=dict(rangemode="tozero"),
            legend=LEGEND_CONFIG,
            margin=dict(r=125),  # Right margin for annotation text
        )

        # Add reference line at 10% (WHO guideline for preterm births)
        fig.add_hline(
            y=10, line_dash="dash", line_color=COLOR_PALETTE["neutral"], annotation_text="Referência OMS", annotation_position="right"
        )

        return fig

    @app.callback(Output("home-absolute-adolescent-comparison", "figure"), Input("url", "pathname"))
    def update_adolescent_absolute(_):
        """Update adolescent pregnancy absolute count chart with stacked bars."""
        df = data_loader.load_yearly_aggregates()

        # Calculate adolescents 15-19 years (adolescent but not very young)
        df["older_adolescent_count"] = df["adolescent_pregnancy_count"] - df["very_young_pregnancy_count"]

        # Create stacked bar chart
        import plotly.graph_objects as go

        fig = go.Figure()

        fig.add_trace(
            go.Bar(
                x=df["year"],
                y=df["older_adolescent_count"],
                name="Adolescentes 15-19 anos",
                marker_color=COLOR_PALETTE["info"],
                text=[f"{int(val):_}".replace("_", ".") for val in df["older_adolescent_count"]],
                textposition="inside",
                textfont=dict(size=11, color="white"),
            )
        )

        fig.add_trace(
            go.Bar(
                x=df["year"],
                y=df["very_young_pregnancy_count"],
                name="Menores de 15 anos",
                marker_color=COLOR_PALETTE["danger"],
                text=[f"{int(val):_}".replace("_", ".") for val in df["very_young_pregnancy_count"]],
                textposition="outside",
                textfont=dict(size=11),
            )
        )

        # Calculate max value for y-axis with padding for outside text
        max_value = df["adolescent_pregnancy_count"].max()
        y_axis_max = max_value * 1.25  # 25% padding above for outside text

        fig.update_layout(
            **COMMON_LAYOUT,
            xaxis_title="Ano",
            yaxis_title="Número de Gestações em Adolescentes",
            barmode="stack",
            yaxis=dict(range=[0, y_axis_max]),
            legend=LEGEND_CONFIG,
        )

        return fig

    @app.callback(Output("home-relative-adolescent-comparison", "figure"), Input("url", "pathname"))
    def update_adolescent_rate(_):
        """Update adolescent pregnancy rate chart with multiple lines."""
        df = data_loader.load_yearly_aggregates()

        import plotly.graph_objects as go

        fig = go.Figure()

        # Add total adolescent line
        fig.add_trace(
            go.Scatter(
                x=df["year"],
                y=df["adolescent_pregnancy_pct"],
                mode="lines+markers",
                name="Adolescentes Total (<20 anos)",
                line=dict(color=COLOR_PALETTE["info"], width=3),
                marker=dict(size=10),
            )
        )

        # Add very young line
        fig.add_trace(
            go.Scatter(
                x=df["year"],
                y=df["very_young_pregnancy_pct"],
                mode="lines+markers",
                name="Menores de 15 anos",
                line=dict(color=COLOR_PALETTE["danger"], width=3),
                marker=dict(size=10),
            )
        )
        max_value = df["very_young_pregnancy_pct"].max()
        y_axis_max = max_value * 1.25

        fig.update_layout(
            **COMMON_LAYOUT,
            xaxis_title="Ano",
            yaxis_title="Taxa de Gravidez na Adolescência (%)",
            yaxis=dict(range=[0, y_axis_max]),
            legend=LEGEND_CONFIG,
        )

        return fig

    @app.callback(Output("home-absolute-low-weight-comparison", "figure"), Input("url", "pathname"))
    def update_low_weight_absolute(_):
        """Update low birth weight absolute numbers chart."""
        df = data_loader.load_yearly_aggregates()

        fig = px.bar(
            df,
            x="year",
            y="low_birth_weight_count",
            text="low_birth_weight_count",
            template=TEMPLATE,
            color_discrete_sequence=[COLOR_PALETTE["warning"]],
        )

        fig.update_traces(texttemplate="%{text:_}".replace("_", "."), textposition="outside")

        fig.update_layout(
            **COMMON_LAYOUT,
            xaxis_title="Ano",
            yaxis_title="Número de Nascimentos <2.500g",
            showlegend=False,
        )

        return fig

    @app.callback(Output("home-relative-low-weight-comparison", "figure"), Input("url", "pathname"))
    def update_low_weight_rate(_):
        """Update low birth weight rate chart."""
        df = data_loader.load_yearly_aggregates()

        import plotly.graph_objects as go

        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=df["year"],
                y=df["low_birth_weight_pct"],
                mode="lines+markers",
                name="Taxa de Baixo Peso",
                line=dict(color=COLOR_PALETTE["warning"], width=3),
                marker=dict(size=10),
            )
        )

        max_value = df["low_birth_weight_pct"].max()
        y_axis_max = max_value * 1.25

        fig.update_layout(
            **COMMON_LAYOUT,
            xaxis_title="Ano",
            yaxis_title="Taxa de Baixo Peso ao Nascer (%)",
            yaxis=dict(range=[0, y_axis_max]),
            showlegend=False,
        )

        return fig

    @app.callback(Output("home-absolute-low-apgar-comparison", "figure"), Input("url", "pathname"))
    def update_low_apgar_absolute(_):
        """Update low APGAR5 absolute numbers chart."""
        df = data_loader.load_yearly_aggregates()

        fig = px.bar(
            df,
            x="year",
            y="low_apgar5_count",
            text="low_apgar5_count",
            template=TEMPLATE,
            color_discrete_sequence=[COLOR_PALETTE["danger"]],
        )

        fig.update_traces(texttemplate="%{text:_}".replace("_", "."), textposition="outside")

        fig.update_layout(
            **COMMON_LAYOUT,
            xaxis_title="Ano",
            yaxis_title="Número de APGAR5 <7",
            showlegend=False,
        )

        return fig

    @app.callback(Output("home-relative-low-apgar-comparison", "figure"), Input("url", "pathname"))
    def update_low_apgar_rate(_):
        """Update low APGAR5 rate chart."""
        df = data_loader.load_yearly_aggregates()

        import plotly.graph_objects as go

        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=df["year"],
                y=df["low_apgar5_pct"],
                mode="lines+markers",
                name="Taxa de APGAR5 Baixo",
                line=dict(color=COLOR_PALETTE["danger"], width=3),
                marker=dict(size=10),
            )
        )

        fig.update_layout(
            **COMMON_LAYOUT,
            xaxis_title="Ano",
            yaxis_title="Taxa de APGAR5 <7 (%)",
            yaxis=dict(rangemode="tozero"),
            showlegend=False,
        )

        return fig


# Layout for routing
layout = create_layout()
