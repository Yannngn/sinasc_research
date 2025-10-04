"""
Annual Analysis page - Detailed dashboard for a specific year.
"""

import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
from config.constants import CHART_TITLES
from config.settings import CHART_CONFIG, CHART_HEIGHT, COLOR_PALETTE
from dash import Input, Output, dcc, html
from data.loader import data_loader

MONTH_NAMES = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]


def create_metric_card(title: str, value: str, icon: str, color: str = "primary") -> dbc.Card:
    """
    Create a metric display card.

    Args:
        title: Card title
        value: Metric value to display
        icon: Font Awesome icon class
        color: Bootstrap color theme

    Returns:
        Bootstrap Card component
    """
    return dbc.Card(
        dbc.CardBody(
            [
                html.Div(
                    [
                        html.I(className=f"fas {icon} fa-2x mb-2", style={"color": COLOR_PALETTE.get(color, "#1f77b4")}),
                        html.H4(value, className="mb-0 fw-bold"),
                        html.P(title, className="text-muted mb-0 small"),
                    ],
                    className="text-center",
                )
            ]
        ),
        className="shadow-sm h-100",
    )


def create_layout() -> html.Div:
    """
    Create annual analysis page layout.

    Returns:
        Dash HTML Div with page layout
    """
    # Get metadata
    metadata = data_loader.get_metadata()
    available_years = sorted(data_loader.get_available_years(), reverse=True)
    latest_year = max(available_years) if available_years else 2024

    return html.Div(
        [
            # Header
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.H1("� Análise Anual", className="mb-2"),
                            html.P("Detalhamento de Nascimentos por Ano", className="lead text-muted mb-4"),
                        ]
                    )
                ]
            ),
            # Year selector
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Label("Selecione o Ano:", className="fw-bold"),
                            dcc.Dropdown(
                                id="annual-year-dropdown",
                                options=[{"label": str(year), "value": year} for year in available_years],
                                value=latest_year,
                                clearable=False,
                                className="mb-4",
                            ),
                        ],
                        width=12,
                        md=3,
                    )
                ]
            ),
            # Key metrics cards (updated dynamically)
            dbc.Row(
                [
                    dbc.Col(
                        [html.Div(id="annual-births-card")],
                        width=12,
                        md=3,
                        className="mb-3",
                    ),
                    dbc.Col(
                        [html.Div(id="annual-age-card")],
                        width=12,
                        md=3,
                        className="mb-3",
                    ),
                    dbc.Col(
                        [html.Div(id="annual-weight-card")],
                        width=12,
                        md=3,
                        className="mb-3",
                    ),
                    dbc.Col(
                        [html.Div(id="annual-cesarean-card")],
                        width=12,
                        md=3,
                        className="mb-3",
                    ),
                ],
                className="mb-3",
            ),
            # Additional metrics cards (second row) - Health quality indicators
            dbc.Row(
                [
                    dbc.Col(
                        [html.Div(id="annual-low-weight-card")],
                        width=12,
                        md=3,
                        className="mb-3",
                    ),
                    dbc.Col(
                        [html.Div(id="annual-preterm-card")],
                        width=12,
                        md=3,
                        className="mb-3",
                    ),
                    dbc.Col(
                        [html.Div(id="annual-hospital-card")],
                        width=12,
                        md=3,
                        className="mb-3",
                    ),
                    dbc.Col(
                        [html.Div(id="annual-low-apgar-card")],
                        width=12,
                        md=3,
                        className="mb-3",
                    ),
                ],
                className="mb-4",
            ),
            # Loading state for charts
            dcc.Loading(
                id="annual-loading",
                type="default",
                children=[
                    # Section header
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    html.H4("📈 Evolução Mensal", className="mb-3 fw-bold text-secondary"),
                                ]
                            )
                        ]
                    ),
                    # Primary visualization - Timeline
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    dbc.Card(
                                        [
                                            dbc.CardHeader(html.H5("Nascimentos por Mês", className="mb-0"), className="bg-light"),
                                            dbc.CardBody(
                                                [
                                                    dcc.Graph(
                                                        id="annual-timeline-chart",
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
                                            dbc.CardHeader(html.H5("Número Mensal de Cesáreas", className="mb-0"), className="bg-light"),
                                            dbc.CardBody(
                                                [
                                                    dcc.Graph(
                                                        id="annual-absolute-cesarean-chart",
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
                                            dbc.CardHeader(html.H5("Taxa Mensal de Cesárea", className="mb-0"), className="bg-light"),
                                            dbc.CardBody(
                                                [
                                                    dcc.Graph(
                                                        id="annual-relative-cesarean-chart",
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
                                            dbc.CardHeader(html.H5("Nascimentos Prematuros Mensais", className="mb-0"), className="bg-light"),
                                            dbc.CardBody(
                                                [
                                                    dcc.Graph(
                                                        id="annual-absolute-preterm-chart",
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
                                            dbc.CardHeader(html.H5("Taxa Mensal de Prematuridade", className="mb-0"), className="bg-light"),
                                            dbc.CardBody(
                                                [
                                                    dcc.Graph(
                                                        id="annual-relative-preterm-chart",
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
                                            dbc.CardHeader(
                                                html.H5("Gestações em Adolescentes Mensais", className="mb-0"), className="bg-light"
                                            ),
                                            dbc.CardBody(
                                                [
                                                    dcc.Graph(
                                                        id="annual-absolute-adolescent-chart",
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
                                            dbc.CardHeader(
                                                html.H5("Taxa Mensal de Gravidez na Adolescência", className="mb-0"), className="bg-light"
                                            ),
                                            dbc.CardBody(
                                                [
                                                    dcc.Graph(
                                                        id="annual-relative-adolescent-chart",
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
                                            dbc.CardHeader(
                                                html.H5("Baixo Peso ao Nascer Mensal (<2.500g)", className="mb-0"), className="bg-light"
                                            ),
                                            dbc.CardBody(
                                                [
                                                    dcc.Graph(
                                                        id="annual-absolute-low-weight-chart",
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
                                            dbc.CardHeader(
                                                html.H5("Taxa Mensal de Baixo Peso ao Nascer", className="mb-0"), className="bg-light"
                                            ),
                                            dbc.CardBody(
                                                [
                                                    dcc.Graph(
                                                        id="annual-relative-low-weight-chart",
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
                                            dbc.CardHeader(html.H5("APGAR5 Baixo Mensal (<7)", className="mb-0"), className="bg-light"),
                                            dbc.CardBody(
                                                [
                                                    dcc.Graph(
                                                        id="annual-absolute-low-apgar-chart",
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
                                            dbc.CardHeader(html.H5("Taxa Mensal de APGAR5 Baixo", className="mb-0"), className="bg-light"),
                                            dbc.CardBody(
                                                [
                                                    dcc.Graph(
                                                        id="annual-relative-low-apgar-chart",
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
                    # Distribution charts section
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    html.H4("📊 Distribuições", className="mb-3 fw-bold text-secondary"),
                                ]
                            )
                        ]
                    ),
                    # Secondary visualizations
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    dbc.Card(
                                        [
                                            dbc.CardHeader(html.H5("Tipo de Parto", className="mb-0"), className="bg-light"),
                                            dbc.CardBody(
                                                [
                                                    dcc.Graph(
                                                        id="annual-delivery-type-chart",
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
                                            dbc.CardHeader(html.H5("Distribuição de Idade Materna", className="mb-0"), className="bg-light"),
                                            dbc.CardBody(
                                                [
                                                    dcc.Graph(
                                                        id="annual-maternal-age-chart",
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
                        ]
                    ),
                ],
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
                                    f"Período: {metadata.get('date_range', {}).get('min', '')} a {metadata.get('date_range', {}).get('max', '')}",
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


# Function to register callbacks (called from app.py)
def register_callbacks(app):
    """Register callbacks for home page."""

    @app.callback(
        [
            Output("annual-births-card", "children"),
            Output("annual-age-card", "children"),
            Output("annual-weight-card", "children"),
            Output("annual-cesarean-card", "children"),
            Output("annual-low-weight-card", "children"),
            Output("annual-preterm-card", "children"),
            Output("annual-hospital-card", "children"),
            Output("annual-low-apgar-card", "children"),
        ],
        Input("annual-year-dropdown", "value"),
    )
    def update_metric_cards(year: int):
        """Update metric cards based on selected year with Brazilian formatting - prioritizing rates over means."""
        summary = data_loader.get_year_summary(year)

        # Format with Brazilian number format
        total_births = summary.get("total_births", 0)
        formatted_births = f"{total_births:_}".replace("_", ".")

        maternal_age = summary.get("maternal_age", {}).get("mean", 0)
        formatted_age = f"{maternal_age:.1f}".replace(".", ",")

        birth_weight = summary.get("birth_weight", {}).get("mean", 0)
        formatted_weight = f"{birth_weight:.0f}"

        cesarean_rate = summary.get("delivery_type", {}).get("cesarean_rate_pct", 0)
        formatted_cesarean = f"{cesarean_rate:.1f}".replace(".", ",")

        low_weight_rate = summary.get("health_indicators", {}).get("low_birth_weight_pct", 0)
        formatted_low_weight = f"{low_weight_rate:.1f}".replace(".", ",")

        preterm_rate = summary.get("pregnancy", {}).get("preterm_birth_pct", 0)
        formatted_preterm = f"{preterm_rate:.1f}".replace(".", ",")

        hospital_rate = summary.get("location", {}).get("hospital_birth_pct", 0)
        formatted_hospital = f"{hospital_rate:.1f}".replace(".", ",")

        low_apgar5_rate = summary.get("health_indicators", {}).get("low_apgar5_pct", 0)
        formatted_low_apgar = f"{low_apgar5_rate:.1f}".replace(".", ",")

        # Create detailed cards similar to home page
        births_card = dbc.Card(
            dbc.CardBody(
                [
                    html.Div(
                        [
                            html.I(className="fas fa-baby fa-2x text-primary mb-2"),
                            html.H4(formatted_births, className="text-primary fw-bold mb-1"),
                            html.P("Nascimentos Totais", className="text-muted mb-0 small"),
                        ],
                        className="text-center",
                    )
                ]
            ),
            className="shadow-sm h-100",
        )

        age_card = dbc.Card(
            dbc.CardBody(
                [
                    html.Div(
                        [
                            html.I(className="fas fa-female fa-2x text-info mb-2"),
                            html.H4(f"{formatted_age} anos", className="text-info fw-bold mb-1"),
                            html.P("Idade Materna Média", className="text-muted mb-0 small"),
                        ],
                        className="text-center",
                    )
                ]
            ),
            className="shadow-sm h-100",
        )

        weight_card = dbc.Card(
            dbc.CardBody(
                [
                    html.Div(
                        [
                            html.I(className="fas fa-weight fa-2x text-success mb-2"),
                            html.H4(f"{formatted_weight}g", className="text-success fw-bold mb-1"),
                            html.P("Peso Médio ao Nascer", className="text-muted mb-0 small"),
                        ],
                        className="text-center",
                    )
                ]
            ),
            className="shadow-sm h-100",
        )

        cesarean_card = dbc.Card(
            dbc.CardBody(
                [
                    html.Div(
                        [
                            html.I(className="fas fa-procedures fa-2x text-warning mb-2"),
                            html.H4(f"{formatted_cesarean}%", className="text-warning fw-bold mb-1"),
                            html.P("Taxa de Cesárea", className="text-muted mb-0 small"),
                        ],
                        className="text-center",
                    )
                ]
            ),
            className="shadow-sm h-100",
        )

        low_weight_card = dbc.Card(
            dbc.CardBody(
                [
                    html.Div(
                        [
                            html.I(className="fas fa-weight-hanging fa-2x text-warning mb-2"),
                            html.H4(f"{formatted_low_weight}%", className="text-warning fw-bold mb-1"),
                            html.P("Taxa de Baixo Peso (<2.500g)", className="text-muted mb-0 small"),
                        ],
                        className="text-center",
                    )
                ]
            ),
            className="shadow-sm h-100",
        )

        preterm_card = dbc.Card(
            dbc.CardBody(
                [
                    html.Div(
                        [
                            html.I(className="fas fa-exclamation-triangle fa-2x text-danger mb-2"),
                            html.H4(f"{formatted_preterm}%", className="text-danger fw-bold mb-1"),
                            html.P("Taxa de Prematuros", className="text-muted mb-0 small"),
                        ],
                        className="text-center",
                    )
                ]
            ),
            className="shadow-sm h-100",
        )

        hospital_card = dbc.Card(
            dbc.CardBody(
                [
                    html.Div(
                        [
                            html.I(className="fas fa-hospital fa-2x text-primary mb-2"),
                            html.H4(f"{formatted_hospital}%", className="text-primary fw-bold mb-1"),
                            html.P("Nascimentos Hospitalares", className="text-muted mb-0 small"),
                        ],
                        className="text-center",
                    )
                ]
            ),
            className="shadow-sm h-100",
        )

        low_apgar_card = dbc.Card(
            dbc.CardBody(
                [
                    html.Div(
                        [
                            html.I(className="fas fa-heartbeat fa-2x text-danger mb-2"),
                            html.H4(f"{formatted_low_apgar}%", className="text-danger fw-bold mb-1"),
                            html.P("Taxa de APGAR5 Baixo (<7)", className="text-muted mb-0 small"),
                        ],
                        className="text-center",
                    )
                ]
            ),
            className="shadow-sm h-100",
        )

        return births_card, age_card, weight_card, cesarean_card, low_weight_card, preterm_card, hospital_card, low_apgar_card

    @app.callback(Output("annual-timeline-chart", "figure"), Input("annual-year-dropdown", "value"))
    def update_timeline_chart(year: int):
        """Update timeline chart based on selected year with vertical month labels."""
        monthly_data = data_loader.load_monthly_aggregates(year)

        monthly_data["month_label"] = monthly_data["month"].apply(lambda x: MONTH_NAMES[x - 1])

        fig = go.Figure()

        fig.add_trace(
            go.Bar(
                x=monthly_data["month_label"],
                y=monthly_data["total_births"],
                text=[f"{int(val):_}".replace("_", ".") for val in monthly_data["total_births"]],
                textposition="inside",
                marker_color=COLOR_PALETTE["primary"],
                name="Nascimentos",
                textfont=dict(size=11, color="white"),
            )
        )

        fig.update_layout(
            xaxis_title="Mês",
            yaxis_title="Número de Nascimentos",
            showlegend=False,
            yaxis=dict(rangemode="tozero"),
            template="plotly_white",
            hovermode="x unified",
            xaxis=dict(
                tickangle=0,  # Keep horizontal since we use short labels
            ),
        )

        return fig

    @app.callback(Output("annual-absolute-cesarean-chart", "figure"), Input("annual-year-dropdown", "value"))
    def update_absolute_cesarean_chart(year: int):
        """Update monthly cesarean absolute count chart."""
        monthly_data = data_loader.load_monthly_aggregates(year)

        # Create month labels

        monthly_data["month_label"] = monthly_data["month"].apply(lambda x: MONTH_NAMES[x - 1])

        # Calculate cesarean count if not present
        if "cesarean_count" not in monthly_data.columns:
            monthly_data["cesarean_count"] = (monthly_data["total_births"] * monthly_data["cesarean_rate_pct"] / 100).round().astype(int)

        fig = go.Figure()

        fig.add_trace(
            go.Bar(
                x=monthly_data["month_label"],
                y=monthly_data["cesarean_count"],
                text=[f"{int(val):_}".replace("_", ".") for val in monthly_data["cesarean_count"]],
                textposition="inside",
                marker_color=COLOR_PALETTE["warning"],
                textfont=dict(size=10, color="white"),
            )
        )

        fig.update_layout(
            xaxis_title="Mês",
            yaxis_title="Número de Cesáreas",
            showlegend=False,
            yaxis=dict(rangemode="tozero"),
            template="plotly_white",
        )

        return fig

    @app.callback(Output("annual-relative-cesarean-chart", "figure"), Input("annual-year-dropdown", "value"))
    def update_relative_cesarean_chart(year: int):
        """Update monthly cesarean rate chart."""
        monthly_data = data_loader.load_monthly_aggregates(year)

        # Create month labels

        monthly_data["month_label"] = monthly_data["month"].apply(lambda x: MONTH_NAMES[x - 1])

        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=monthly_data["month_label"],
                y=monthly_data["cesarean_rate_pct"],
                mode="lines+markers",
                line=dict(color=COLOR_PALETTE["warning"], width=3),
                marker=dict(size=10),
                name="Taxa de Cesárea",
            )
        )

        fig.update_layout(
            xaxis_title="Mês",
            yaxis_title="Taxa de Cesárea (%)",
            showlegend=False,
            yaxis=dict(rangemode="tozero"),
            template="plotly_white",
            margin=dict(r=125),
        )

        # Add WHO reference line
        fig.add_hline(
            y=15,
            line_dash="dash",
            line_color=COLOR_PALETTE["danger"],
            annotation_text="Recomendação OMS",
            annotation_position="right",
        )

        return fig

    @app.callback(Output("annual-absolute-preterm-chart", "figure"), Input("annual-year-dropdown", "value"))
    def update_absolute_preterm_chart(year: int):
        """Update monthly preterm births absolute count chart with stacked bars."""
        monthly_data = data_loader.load_monthly_aggregates(year)

        # Create month labels

        monthly_data["month_label"] = monthly_data["month"].apply(lambda x: MONTH_NAMES[x - 1])

        # Use existing count columns
        monthly_data["moderate_preterm_count"] = monthly_data["preterm_birth_count"] - monthly_data["extreme_preterm_birth_count"]

        fig = go.Figure()

        # Add moderate preterm
        fig.add_trace(
            go.Bar(
                x=monthly_data["month_label"],
                y=monthly_data["moderate_preterm_count"],
                name="Prematuros Moderados (32-36 sem)",
                marker_color=COLOR_PALETTE["warning"],
                text=[f"{int(val):_}".replace("_", ".") for val in monthly_data["moderate_preterm_count"]],
                textposition="inside",
                textfont=dict(size=9, color="white"),
            )
        )

        # Add extreme preterm
        fig.add_trace(
            go.Bar(
                x=monthly_data["month_label"],
                y=monthly_data["extreme_preterm_birth_count"],
                name="Prematuros Extremos (<32 sem)",
                marker_color=COLOR_PALETTE["danger"],
                text=[f"{int(val):_}".replace("_", ".") for val in monthly_data["extreme_preterm_birth_count"]],
                textposition="outside",
                textfont=dict(size=9),
            )
        )

        max_value = monthly_data["preterm_birth_count"].max()
        y_axis_max = max_value * 1.25

        fig.update_layout(
            xaxis_title="Mês",
            yaxis_title="Número de Nascimentos Prematuros",
            barmode="stack",
            yaxis=dict(range=[0, y_axis_max]),
            template="plotly_white",
            legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5),
        )

        return fig

    @app.callback(Output("annual-relative-preterm-chart", "figure"), Input("annual-year-dropdown", "value"))
    def update_relative_preterm_chart(year: int):
        """Update monthly preterm birth rate chart with multiple lines."""
        monthly_data = data_loader.load_monthly_aggregates(year)

        # Create month labels

        monthly_data["month_label"] = monthly_data["month"].apply(lambda x: MONTH_NAMES[x - 1])

        fig = go.Figure()

        # Add total preterm line
        fig.add_trace(
            go.Scatter(
                x=monthly_data["month_label"],
                y=monthly_data["preterm_birth_pct"],
                mode="lines+markers",
                name="Prematuros Total (<37 sem)",
                line=dict(color=COLOR_PALETTE["warning"], width=3),
                marker=dict(size=10),
            )
        )

        # Add extreme preterm line
        fig.add_trace(
            go.Scatter(
                x=monthly_data["month_label"],
                y=monthly_data["extreme_preterm_birth_pct"],
                mode="lines+markers",
                name="Prematuros Extremos (<32 sem)",
                line=dict(color=COLOR_PALETTE["danger"], width=3),
                marker=dict(size=10),
            )
        )

        fig.update_layout(
            xaxis_title="Mês",
            yaxis_title="Taxa de Prematuridade (%)",
            yaxis=dict(rangemode="tozero"),
            template="plotly_white",
            legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5),
            margin=dict(r=125),
        )

        # Add WHO reference line
        fig.add_hline(
            y=10,
            line_dash="dash",
            line_color=COLOR_PALETTE["neutral"],
            annotation_text="Referência OMS",
            annotation_position="right",
        )

        return fig

    @app.callback(Output("annual-absolute-adolescent-chart", "figure"), Input("annual-year-dropdown", "value"))
    def update_absolute_adolescent_chart(year: int):
        """Update monthly adolescent pregnancy absolute count chart with stacked bars."""
        monthly_data = data_loader.load_monthly_aggregates(year)

        # Create month labels

        monthly_data["month_label"] = monthly_data["month"].apply(lambda x: MONTH_NAMES[x - 1])

        monthly_data["older_adolescent_count"] = monthly_data["adolescent_pregnancy_count"] - monthly_data["very_young_pregnancy_count"]

        fig = go.Figure()

        fig.add_trace(
            go.Bar(
                x=monthly_data["month_label"],
                y=monthly_data["older_adolescent_count"],
                name="Adolescentes 15-19 anos",
                marker_color=COLOR_PALETTE["info"],
                text=[f"{int(val):_}".replace("_", ".") for val in monthly_data["older_adolescent_count"]],
                textposition="inside",
                textfont=dict(size=9, color="white"),
            )
        )

        fig.add_trace(
            go.Bar(
                x=monthly_data["month_label"],
                y=monthly_data["very_young_pregnancy_count"],
                name="Menores de 15 anos",
                marker_color=COLOR_PALETTE["danger"],
                text=[f"{int(val):_}".replace("_", ".") for val in monthly_data["very_young_pregnancy_count"]],
                textposition="outside",
                textfont=dict(size=9),
            )
        )

        max_value = monthly_data["adolescent_pregnancy_count"].max()
        y_axis_max = max_value * 1.25

        fig.update_layout(
            xaxis_title="Mês",
            yaxis_title="Número de Gestações em Adolescentes",
            barmode="stack",
            yaxis=dict(range=[0, y_axis_max]),
            template="plotly_white",
            legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5),
        )

        return fig

    @app.callback(Output("annual-relative-adolescent-chart", "figure"), Input("annual-year-dropdown", "value"))
    def update_relative_adolescent_chart(year: int):
        """Update monthly adolescent pregnancy rate chart with multiple lines."""
        monthly_data = data_loader.load_monthly_aggregates(year)

        # Create month labels

        monthly_data["month_label"] = monthly_data["month"].apply(lambda x: MONTH_NAMES[x - 1])

        fig = go.Figure()

        # Add total adolescent line
        fig.add_trace(
            go.Scatter(
                x=monthly_data["month_label"],
                y=monthly_data["adolescent_pregnancy_pct"],
                mode="lines+markers",
                name="Adolescentes Total (<20 anos)",
                line=dict(color=COLOR_PALETTE["info"], width=3),
                marker=dict(size=10),
            )
        )

        # Add very young line
        fig.add_trace(
            go.Scatter(
                x=monthly_data["month_label"],
                y=monthly_data["very_young_pregnancy_pct"],
                mode="lines+markers",
                name="Menores de 15 anos",
                line=dict(color=COLOR_PALETTE["danger"], width=3),
                marker=dict(size=10),
            )
        )

        fig.update_layout(
            xaxis_title="Mês",
            yaxis_title="Taxa de Gravidez na Adolescência (%)",
            yaxis=dict(rangemode="tozero"),
            template="plotly_white",
            legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5),
        )

        return fig

    @app.callback(Output("annual-delivery-type-chart", "figure"), Input("annual-year-dropdown", "value"))
    def update_delivery_type_chart(year: int):
        """Update delivery type pie chart."""
        summary = data_loader.get_year_summary(year)
        delivery_type = summary.get("delivery_type", {})

        # Create pie chart data
        values = [delivery_type.get("vaginal_rate_pct", 0), delivery_type.get("cesarean_rate_pct", 0)]
        labels = ["Vaginal", "Cesárea"]
        colors = [COLOR_PALETTE["primary"], COLOR_PALETTE["secondary"]]

        fig = go.Figure(
            data=[go.Pie(labels=labels, values=values, marker=dict(colors=colors), hole=0.4, textinfo="label+percent", textposition="auto")]
        )

        fig.update_layout(
            title=CHART_TITLES["delivery_type"],
            template="plotly_white",
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
        )

        return fig

    @app.callback(Output("annual-maternal-age-chart", "figure"), Input("annual-year-dropdown", "value"))
    def update_maternal_age_chart(year: int):
        """Update maternal age distribution chart."""
        # Load essential data with only needed column
        df = data_loader.load_essential_data(year, columns=["IDADEMAE"])

        # Remove invalid values
        df_clean = df[df["IDADEMAE"] > 0]

        fig = px.histogram(
            df_clean,
            x="IDADEMAE",
            nbins=40,
            title=CHART_TITLES["maternal_age"],
            labels={"IDADEMAE": "Idade (anos)", "count": "Frequência"},
            template="plotly_white",
            color_discrete_sequence=[COLOR_PALETTE["info"]],
        )

        fig.update_layout(xaxis_title="Idade Materna (anos)", yaxis_title="Número de Nascimentos", showlegend=False, bargap=0.1)

        # Add mean line
        mean_age = df_clean["IDADEMAE"].mean()
        fig.add_vline(
            x=mean_age,
            line_dash="dash",
            line_color=COLOR_PALETTE["danger"],
            annotation_text=f"Média: {mean_age:.1f}",
            annotation_position="top",
        )

        return fig

    @app.callback(Output("annual-absolute-low-weight-chart", "figure"), Input("annual-year-dropdown", "value"))
    def update_absolute_low_weight_chart(year: int):
        """Update monthly low birth weight absolute numbers chart."""
        monthly_data = data_loader.load_monthly_aggregates(year)

        # Create month labels
        monthly_data["month_label"] = monthly_data["month"].apply(lambda x: MONTH_NAMES[x - 1])

        fig = px.bar(
            monthly_data,
            x="month_label",
            y="low_birth_weight_count",
            text="low_birth_weight_count",
            template="plotly_white",
            color_discrete_sequence=[COLOR_PALETTE["warning"]],
        )

        fig.update_traces(texttemplate="%{text:_}".replace("_", "."), textposition="outside")

        fig.update_layout(
            xaxis_title="Mês",
            yaxis_title="Número de Nascimentos <2.500g",
            showlegend=False,
        )

        return fig

    @app.callback(Output("annual-relative-low-weight-chart", "figure"), Input("annual-year-dropdown", "value"))
    def update_relative_low_weight_chart(year: int):
        """Update monthly low birth weight rate chart."""
        monthly_data = data_loader.load_monthly_aggregates(year)

        # Create month labels
        monthly_data["month_label"] = monthly_data["month"].apply(lambda x: MONTH_NAMES[x - 1])

        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=monthly_data["month_label"],
                y=monthly_data["low_birth_weight_pct"],
                mode="lines+markers",
                name="Taxa de Baixo Peso",
                line=dict(color=COLOR_PALETTE["warning"], width=3),
                marker=dict(size=10),
            )
        )

        fig.update_layout(
            xaxis_title="Mês",
            yaxis_title="Taxa de Baixo Peso ao Nascer (%)",
            yaxis=dict(rangemode="tozero"),
            template="plotly_white",
            showlegend=False,
        )

        return fig

    @app.callback(Output("annual-absolute-low-apgar-chart", "figure"), Input("annual-year-dropdown", "value"))
    def update_absolute_low_apgar_chart(year: int):
        """Update monthly low APGAR5 absolute numbers chart."""
        monthly_data = data_loader.load_monthly_aggregates(year)

        # Create month labels
        monthly_data["month_label"] = monthly_data["month"].apply(lambda x: MONTH_NAMES[x - 1])

        fig = px.bar(
            monthly_data,
            x="month_label",
            y="low_apgar5_count",
            text="low_apgar5_count",
            template="plotly_white",
            color_discrete_sequence=[COLOR_PALETTE["danger"]],
        )

        fig.update_traces(texttemplate="%{text:_}".replace("_", "."), textposition="outside")

        fig.update_layout(
            xaxis_title="Mês",
            yaxis_title="Número de APGAR5 <7",
            showlegend=False,
        )

        return fig

    @app.callback(Output("annual-relative-low-apgar-chart", "figure"), Input("annual-year-dropdown", "value"))
    def update_relative_low_apgar_chart(year: int):
        """Update monthly low APGAR5 rate chart."""
        monthly_data = data_loader.load_monthly_aggregates(year)

        # Create month labels
        monthly_data["month_label"] = monthly_data["month"].apply(lambda x: MONTH_NAMES[x - 1])

        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=monthly_data["month_label"],
                y=monthly_data["low_apgar5_pct"],
                mode="lines+markers",
                name="Taxa de APGAR5 Baixo",
                line=dict(color=COLOR_PALETTE["danger"], width=3),
                marker=dict(size=10),
            )
        )

        fig.update_layout(
            xaxis_title="Mês",
            yaxis_title="Taxa de APGAR5 <7 (%)",
            yaxis=dict(rangemode="tozero"),
            template="plotly_white",
            showlegend=False,
        )

        return fig


# Layout for routing
layout = create_layout()
