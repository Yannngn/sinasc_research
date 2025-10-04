"""
Annual Analysis page - Detailed dashboard for a specific year.
"""

import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from components.charts import (
    create_line_chart,
    create_multi_line_chart,
    create_simple_bar_chart,
    create_stacked_bar_chart,
)
from config.constants import CHART_TITLES
from config.settings import CHART_CONFIG, CHART_HEIGHT, COLOR_PALETTE
from dash import Input, Output, dcc, html
from data.loader import data_loader


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
                            html.H1("📅 Análise Anual", className="mb-2"),
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
                                                        id="annual-maternal-ocupation-chart",
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

        maternal_age = summary.get("pregnancy", {}).get("adolescent_pregnancy_pct", 0)
        formatted_age = f"{maternal_age:.1f}".replace(".", ",")

        very_young_pregnancy_rate = summary.get("pregnancy", {}).get("very_young_pregnancy_pct", 0)
        formatted_very_young = f"{very_young_pregnancy_rate:.1f}".replace(".", ",")

        cesarean_rate = summary.get("delivery_type", {}).get("cesarean_pct", 0)
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
                            html.H4(f"{formatted_age}%", className="text-info fw-bold mb-1"),
                            html.P("Taxa de Gestações Abaixo de 20 anos", className="text-muted mb-0 small"),
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
                            html.I(className="fas fa-child fa-2x text-success mb-2"),
                            html.H4(f"{formatted_very_young}%", className="text-success fw-bold mb-1"),
                            html.P("Taxa de Gestações Abaixo de 15 anos", className="text-muted mb-0 small"),
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

        fig = create_simple_bar_chart(
            df=monthly_data,
            x_col="month_label",
            y_col="total_births",
            x_title="Mês",
            y_title="Número de Nascimentos",
            color="primary",
        )

        return fig

    @app.callback(Output("annual-absolute-cesarean-chart", "figure"), Input("annual-year-dropdown", "value"))
    def update_absolute_cesarean_chart(year: int):
        """Update monthly cesarean absolute count chart."""
        monthly_data = data_loader.load_monthly_aggregates(year)

        if "cesarean_count" not in monthly_data.columns:
            monthly_data["cesarean_count"] = monthly_data["cesarean_pct"].mul(monthly_data["total_births"]).round().astype(int)

        fig = create_simple_bar_chart(
            df=monthly_data,
            x_col="month_label",
            y_col="cesarean_count",
            x_title="Mês",
            y_title="Número de Cesáreas",
            color="warning",
        )

        return fig

    @app.callback(Output("annual-relative-cesarean-chart", "figure"), Input("annual-year-dropdown", "value"))
    def update_relative_cesarean_chart(year: int):
        """Update monthly cesarean rate chart."""
        monthly_data = data_loader.load_monthly_aggregates(year)

        fig = create_line_chart(
            df=monthly_data,
            x_col="month_label",
            y_col="cesarean_pct",
            x_title="Mês",
            y_title="Taxa de Cesárea (%)",
            color="warning",
            reference_line={"y": 15, "text": "Referência OMS", "color": "danger"},
        )
        return fig

    @app.callback(Output("annual-absolute-preterm-chart", "figure"), Input("annual-year-dropdown", "value"))
    def update_absolute_preterm_chart(year: int):
        """Update monthly preterm births absolute count chart with stacked bars."""
        monthly_data = data_loader.load_monthly_aggregates(year)

        # Calculate moderate preterm
        monthly_data["moderate_preterm_count"] = monthly_data["preterm_birth_count"] - monthly_data["extreme_preterm_birth_count"]

        return create_stacked_bar_chart(
            df=monthly_data,
            x_col="month_label",
            y_cols=["moderate_preterm_count", "extreme_preterm_birth_count"],
            labels=["Prematuros Moderados (32-36 sem)", "Prematuros Extremos (<32 sem)"],
            colors=["warning", "danger"],
            x_title="Mês",
            y_title="Número de Nascimentos Prematuros",
            text_size=9,
        )

    @app.callback(Output("annual-relative-preterm-chart", "figure"), Input("annual-year-dropdown", "value"))
    def update_relative_preterm_chart(year: int):
        """Update monthly preterm birth rate chart with multiple lines."""
        monthly_data = data_loader.load_monthly_aggregates(year)

        return create_multi_line_chart(
            df=monthly_data,
            x_col="month_label",
            y_cols=["preterm_birth_pct", "extreme_preterm_birth_pct"],
            labels=["Prematuros Total (<37 sem)", "Prematuros Extremos (<32 sem)"],
            colors=["warning", "danger"],
            x_title="Mês",
            y_title="Taxa de Prematuridade (%)",
            reference_line={"y": 10, "text": "Referência OMS", "color": "neutral"},
        )

    @app.callback(Output("annual-absolute-adolescent-chart", "figure"), Input("annual-year-dropdown", "value"))
    def update_absolute_adolescent_chart(year: int):
        """Update monthly adolescent pregnancy absolute count chart with stacked bars."""
        monthly_data = data_loader.load_monthly_aggregates(year)

        # Calculate older adolescent count
        monthly_data["older_adolescent_count"] = monthly_data["adolescent_pregnancy_count"] - monthly_data["very_young_pregnancy_count"]

        return create_stacked_bar_chart(
            df=monthly_data,
            x_col="month_label",
            y_cols=["older_adolescent_count", "very_young_pregnancy_count"],
            labels=["Adolescentes 15-19 anos", "Menores de 15 anos"],
            colors=["info", "danger"],
            x_title="Mês",
            y_title="Número de Gestações em Adolescentes",
            text_size=9,
        )

    @app.callback(Output("annual-relative-adolescent-chart", "figure"), Input("annual-year-dropdown", "value"))
    def update_relative_adolescent_chart(year: int):
        """Update monthly adolescent pregnancy rate chart with multiple lines."""
        monthly_data = data_loader.load_monthly_aggregates(year)

        return create_multi_line_chart(
            df=monthly_data,
            x_col="month_label",
            y_cols=["adolescent_pregnancy_pct", "very_young_pregnancy_pct"],
            labels=["Adolescentes Total (<20 anos)", "Menores de 15 anos"],
            colors=["info", "danger"],
            x_title="Mês",
            y_title="Taxa de Gravidez na Adolescência (%)",
        )

    @app.callback(Output("annual-absolute-low-weight-chart", "figure"), Input("annual-year-dropdown", "value"))
    def update_absolute_low_weight_chart(year: int):
        """Update monthly low birth weight absolute numbers chart."""
        monthly_data = data_loader.load_monthly_aggregates(year)

        return create_simple_bar_chart(
            df=monthly_data,
            x_col="month_label",
            y_col="low_birth_weight_count",
            x_title="Mês",
            y_title="Número de Nascimentos <2.500g",
            color="warning",
        )

    @app.callback(Output("annual-relative-low-weight-chart", "figure"), Input("annual-year-dropdown", "value"))
    def update_relative_low_weight_chart(year: int):
        """Update monthly low birth weight rate chart."""
        monthly_data = data_loader.load_monthly_aggregates(year)

        return create_line_chart(
            df=monthly_data,
            x_col="month_label",
            y_col="low_birth_weight_pct",
            x_title="Mês",
            y_title="Taxa de Baixo Peso ao Nascer (%)",
            color="warning",
        )

    @app.callback(Output("annual-absolute-low-apgar-chart", "figure"), Input("annual-year-dropdown", "value"))
    def update_absolute_low_apgar_chart(year: int):
        """Update monthly low APGAR5 absolute numbers chart."""
        monthly_data = data_loader.load_monthly_aggregates(year)

        return create_simple_bar_chart(
            df=monthly_data,
            x_col="month_label",
            y_col="low_apgar5_count",
            x_title="Mês",
            y_title="Número de APGAR5 <7",
            color="danger",
        )

    @app.callback(Output("annual-relative-low-apgar-chart", "figure"), Input("annual-year-dropdown", "value"))
    def update_relative_low_apgar_chart(year: int):
        """Update monthly low APGAR5 rate chart."""
        monthly_data = data_loader.load_monthly_aggregates(year)

        return create_line_chart(
            df=monthly_data,
            x_col="month_label",
            y_col="low_apgar5_pct",
            x_title="Mês",
            y_title="Taxa de APGAR5 Baixo (%)",
            color="danger",
        )

    @app.callback(Output("annual-delivery-type-chart", "figure"), Input("annual-year-dropdown", "value"))
    def update_delivery_type_chart(year: int):
        """Update delivery type pie chart."""
        summary = data_loader.get_year_summary(year)
        delivery_type = summary.get("delivery_type", {})

        # Create pie chart data
        values = [delivery_type.get("vaginal_pct", 0), delivery_type.get("cesarean_pct", 0)]
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

    @app.callback(Output("annual-maternal-ocupation-chart", "figure"), Input("annual-year-dropdown", "value"))
    def update_maternal_occupation_chart(year: int):
        """
        Update maternal occupation distribution chart using metadata summary.

        Args:
            year: Selected year for data filtering

        Returns:
            Plotly figure object for the pie chart
        """
        summary = data_loader.get_year_summary(year)
        maternal_occupation = summary.get("maternal_occupation", {})

        # Build a clean DataFrame: expected structure is {code: {"label": str, "count": int}}
        rows = []
        if isinstance(maternal_occupation, dict):
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
        if not occupation_counts.empty:
            occupation_counts = occupation_counts[occupation_counts["count"] > 0].sort_values("count", ascending=False)

        # Prepare colors (cycle pastel palette if necessary)
        palette = px.colors.qualitative.Pastel
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
            title="Distribuição de Ocupação Materna",
            template="plotly_white",
            showlegend=False,
            legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.02),
            margin=dict(t=40, b=10, l=10, r=80),
            height=int(CHART_HEIGHT),
        )

        return fig

    # @app.callback(Output("annual-maternal-age-chart", "figure"), Input("annual-year-dropdown", "value"))
    # def update_maternal_age_chart(year: int):
    #     """Update maternal age distribution chart."""
    #     # Load essential data with only needed column
    #     df = data_loader.load_essential_data(year, columns=["IDADEMAE"])

    #     # Remove invalid values
    #     df_clean = df[df["IDADEMAE"] > 0]

    #     fig = px.histogram(
    #         df_clean,
    #         x="IDADEMAE",
    #         nbins=40,
    #         title=CHART_TITLES["maternal_age"],
    #         labels={"IDADEMAE": "Idade (anos)", "count": "Frequência"},
    #         template="plotly_white",
    #         color_discrete_sequence=[COLOR_PALETTE["info"]],
    #     )

    #     fig.update_layout(xaxis_title="Idade Materna (anos)", yaxis_title="Número de Nascimentos", showlegend=False, bargap=0.1)

    #     # Add mean line
    #     mean_age = df_clean["IDADEMAE"].mean()
    #     fig.add_vline(
    #         x=mean_age,
    #         line_dash="dash",
    #         line_color=COLOR_PALETTE["danger"],
    #         annotation_text=f"Média: {mean_age:.1f}",
    #         annotation_position="top",
    #     )

    #     return fig


# Layout for routing
layout = create_layout()
