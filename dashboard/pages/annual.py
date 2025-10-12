"""
Annual Analysis page - Detailed dashboard for a specific year.
"""

import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go
from components.cards import create_metric_card
from components.charts import (
    create_bar_chart,
    create_line_chart,
    create_multi_line_chart,
    create_pie_chart,
    create_stacked_bar_chart,
)
from components.geo_charts import create_choropleth_chart
from config.constants import (
    CHART_TITLES,
    INDICATOR_MAPPINGS,
    MONTH_NAMES,
    YEAR_SUMMARY_METRICS,
)
from config.settings import (
    CHART_CONFIG,
    CHART_HEIGHT,
    COLOR_CONTINUOS_PALETTE,
    COLOR_PALETTE,
)
from dash import Input, Output, dcc, html
from data.loader import data_loader


def get_previous_year_summary(year: int) -> dict | None:
    """
    Get the summary for the previous year if available.

    Args:
        year: Current year

    Returns:
        Previous year summary or None
    """
    available_years = data_loader.get_available_years()
    prev_year = year - 1
    if prev_year in available_years:
        return data_loader.get_year_summary(prev_year)
    return None


def create_year_summary(year: int):
    """
    Create year summary cards using configuration-driven approach.

    Args:
        year: Year to generate summary for

    Returns:
        List of metric cards
    """
    summary = data_loader.get_year_summary(year)
    prev_summary = get_previous_year_summary(year)

    cards = []
    for metric_key, config in YEAR_SUMMARY_METRICS.items():
        # Extract current value
        current_value = config.extract_value(summary)

        # Format the value
        formatted_value = config.format_value(current_value)

        # Calculate YOY change
        yoy_change = None
        if prev_summary:
            prev_value = config.extract_value(prev_summary)
            yoy_change = config.calculate_yoy_change(current_value, prev_value)

        # Create card
        card = create_metric_card(
            title=config.card_title, value=formatted_value, icon=config.card_icon, color=config.card_color, yoy_change=yoy_change
        )
        cards.append(card)

    return cards


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

    def return_header() -> dbc.Row:
        return dbc.Row(
            [
                dbc.Col(
                    [
                        html.H4("Análise Anual"),
                        html.P(
                            "Detalhamento de Nascimentos por Ano",
                            className="text-muted mb-4",
                        ),
                    ],
                    className="mb-3 mx-0",
                )
            ]
        )

    def return_summary_cards() -> dbc.Row:
        return dbc.Row(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            [html.Div(id="annual-births-card")],
                            width=12,
                            md=3,
                            className="mx-0",
                        ),
                        dbc.Col(
                            [html.Div(id="annual-age-card")],
                            width=12,
                            md=3,
                            className="mx-0",
                        ),
                        dbc.Col(
                            [html.Div(id="annual-weight-card")],
                            width=12,
                            md=3,
                            className="mx-0",
                        ),
                        dbc.Col(
                            [html.Div(id="annual-cesarean-card")],
                            width=12,
                            md=3,
                            className="mx-0",
                        ),
                    ],
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            [html.Div(id="annual-low-weight-card")],
                            width=12,
                            md=3,
                            className="mx-0",
                        ),
                        dbc.Col(
                            [html.Div(id="annual-preterm-card")],
                            width=12,
                            md=3,
                            className="mx-0",
                        ),
                        dbc.Col(
                            [html.Div(id="annual-hospital-card")],
                            width=12,
                            md=3,
                            className="mx-0",
                        ),
                        dbc.Col(
                            [html.Div(id="annual-low-apgar-card")],
                            width=12,
                            md=3,
                            className="mx-0",
                        ),
                    ],
                ),
                dbc.Row(
                    [
                        html.P(
                            "Use o controle deslizante abaixo para navegar pelos dados de diferentes anos:",
                            className="text-muted my-3",
                        ),
                        dcc.Slider(
                            id="annual-year-slider",
                            min=min(available_years),
                            max=max(available_years),
                            value=latest_year,
                            marks={year: str(year) for year in available_years},
                            step=1,
                            className="color-primary mb-2",
                            tooltip={"placement": "bottom", "always_visible": True},
                        ),
                        html.Div(
                            [
                                html.Small(
                                    f"Período disponível: {min(available_years)} - {max(available_years)}",
                                    className="text-muted",
                                )
                            ],
                            className="text-center mt-2",
                        ),
                    ]
                ),
            ],
            className="shadow-sm gap-2 mb-5",
        )

    def return_indicator_analysis() -> dcc.Loading:
        return dbc.Row(
            children=[
                dcc.Loading(
                    id="annual-loading",
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
                                                    "Evolução dos indicadores ao longo dos meses",
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
                                            id="annual-indicator-month-dropdown",
                                            options=[
                                                {"label": month, "value": i}
                                                for i, month in enumerate(
                                                    [
                                                        "Janeiro",
                                                        "Fevereiro",
                                                        "Março",
                                                        "Abril",
                                                        "Maio",
                                                        "Junho",
                                                        "Julho",
                                                        "Agosto",
                                                        "Setembro",
                                                        "Outubro",
                                                        "Novembro",
                                                        "Dezembro",
                                                    ],
                                                    start=1,
                                                )
                                            ],
                                            value=1,  # Default to January
                                            clearable=False,
                                            className="mb-3",
                                            style={"width": "100%"},
                                        ),
                                        dcc.Dropdown(
                                            id="annual-indicator-type-dropdown",
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
                                                        id="annual-absolute-indicator-chart-title",
                                                        className="mb-0",
                                                    ),
                                                    className="bg-light",
                                                ),
                                                dbc.CardBody(
                                                    [
                                                        dcc.Graph(
                                                            id="annual-absolute-indicator-chart",
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
                                                        id="annual-relative-indicator-chart-title",
                                                        className="mb-0",
                                                    ),
                                                    className="bg-light",
                                                ),
                                                dbc.CardBody(
                                                    [
                                                        dcc.Graph(
                                                            id="annual-relative-indicator-chart",
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
                                                        id="annual-indicator-pie-title",
                                                        className="mb-0",
                                                    ),
                                                    className="bg-light",
                                                ),
                                                dbc.CardBody(
                                                    [
                                                        dcc.Graph(
                                                            id="annual-indicator-pie-chart",
                                                            config=CHART_CONFIG,  # type:ignore
                                                            style={"height": f"{CHART_HEIGHT}px"},
                                                        )
                                                    ],
                                                    className="p-0",
                                                ),
                                            ],
                                            className="shadow-sm mb-4",
                                        )
                                    ],
                                    width=12,
                                    lg=2,
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
                                                        "Mapa Geográfico do Indicador",
                                                        id="annual-indicator-absolute-map-title",
                                                        className="mb-0",
                                                    ),
                                                    className="bg-light",
                                                ),
                                                dbc.CardBody(
                                                    [
                                                        dcc.Graph(
                                                            id="annual-indicator-absolute-map-chart",
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
                                                        id="annual-indicator-relative-map-title",
                                                        className="mb-0",
                                                    ),
                                                    className="bg-light",
                                                ),
                                                dbc.CardBody(
                                                    [
                                                        dcc.Graph(
                                                            id="annual-indicator-relative-map-chart",
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
                            ]
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
            # Header
            return_header(),
            # Key metrics cards (updated dynamically)
            return_summary_cards(),
            # Year selector - moved below cards for better UX
            return_indicator_analysis(),
            # dbc.Row(
            #     dbc.Col(
            #         [
            #             dbc.Card(
            #                 [
            #                     dbc.CardHeader(
            #                         html.H5(
            #                             "Distribuição de Ocupação Materna",
            #                             id="annual-maternal-occupation-pie-title",
            #                             className="mb-0",
            #                         ),
            #                         className="bg-light",
            #                     ),
            #                     dbc.CardBody(
            #                         [
            #                             dcc.Graph(
            #                                 id="annual-maternal-occupation-pie-chart",
            #                                 config=CHART_CONFIG,  # type:ignore
            #                                 style={"height": f"{CHART_HEIGHT}px"},
            #                             )
            #                         ],
            #                         className="p-0",
            #                     ),
            #                 ],
            #                 className="shadow-sm",
            #             )
            #         ],
            #         width=12,
            #         lg=3,
            #         className="mb-4",
            #     )
            # ),
            # Data source footer
            return_footer(),
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
        Input("annual-year-slider", "value"),
    )
    def update_metric_cards(year: int):
        """Update metric cards based on selected year with Brazilian formatting - prioritizing rates over means."""
        return create_year_summary(year)

    @app.callback(
        [
            # Figures
            Output("annual-timeline-chart", "figure"),
            # Titles
            Output("annual-timeline-title", "children"),
        ],
        Input("annual-year-slider", "value"),
    )
    def update_monthly_charts(year: int):
        """Update all monthly evolution charts and their dynamic titles."""
        monthly_data = data_loader.load_monthly_aggregates(year)

        # Timeline chart
        timeline_fig = create_bar_chart(
            df=monthly_data,
            x_col="month_label",
            y_col="total_births",
            label="Nascimentos",
            x_title="Mês",
            y_title="Número de Nascimentos",
            color="primary",
        )
        timeline_title = f"Nascimentos por Mês - {year}"

        return (
            # Figures
            timeline_fig,
            # Titles
            timeline_title,
        )

    @app.callback(
        [
            Output("annual-delivery-type-chart", "figure"),
            Output("annual-delivery-type-title", "children"),
        ],
        Input("annual-year-slider", "value"),
    )
    def update_delivery_type_chart(year: int):
        """Update delivery type pie chart."""
        summary = data_loader.get_year_summary(year)
        delivery_type = summary.get("delivery_type", {})

        # Create pie chart data
        cesarean = delivery_type.get("cesarean_pct", 0)
        values = [
            delivery_type.get("vaginal_pct", 100 - cesarean),
            cesarean,
        ]
        labels = ["Vaginal", "Cesárea"]
        colors = [COLOR_PALETTE["primary"], COLOR_PALETTE["secondary"]]

        fig = go.Figure(
            data=[
                go.Pie(
                    labels=labels,
                    values=values,
                    marker=dict(colors=colors),
                    hole=0.4,
                    textinfo="label+percent",
                    textposition="auto",
                )
            ]
        )

        fig.update_layout(
            title=CHART_TITLES["delivery_type"],
            template="plotly_white",
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
        )

        title = f"Tipo de Parto - {year}"

        return fig, title

    @app.callback(
        Output("annual-state-level-map", "figure"),
        [
            Input("annual-year-slider", "value"),
            Input("annual-birth-month-dropdown", "value"),
            Input("annual-birth-type-dropdown", "value"),
        ],
    )
    def update_state_level_map(year, month, birth_type):
        """Update the state level map based on selected filters."""
        df = data_loader.load_monthly_state_aggregates(year)
        df = df[df["month"] == month]

        if birth_type == "per_1k":
            color_col = "births_per_1k_population"
            color_label = "Nascimentos por 1.000 Hab."
            color_scale = "Viridis"
        else:
            color_col = "total_births"
            color_label = "Nascimentos"
            color_scale = "Blues"

        fig = create_choropleth_chart(
            df=df,
            geojson=data_loader.load_geojson_states(),
            indicator="state_code",
            color=color_col,
            color_scale=color_scale,
            title=f"{color_label} por Estado - {MONTH_NAMES[month - 1]} {year}",
        )
        return fig

    @app.callback(
        [
            Output("annual-absolute-indicator-chart", "figure"),
            Output("annual-relative-indicator-chart", "figure"),
            Output("annual-absolute-indicator-chart-title", "children"),
            Output("annual-relative-indicator-chart-title", "children"),
        ],
        Input("annual-indicator-type-dropdown", "value"),
        Input("annual-year-slider", "value"),
    )
    def update_indicator_charts(selected_indicator, selected_year):
        """Update the absolute and relative indicator charts based on the selected indicator."""
        df = data_loader.load_monthly_aggregates(selected_year)

        # Get the selected indicator's data
        indicator_data = INDICATOR_MAPPINGS[selected_indicator]

        # Create absolute chart
        absolute_columns = indicator_data.get_absolute_columns()
        if len(absolute_columns) == 1:
            # Single column - use bar chart
            absolute_chart = create_bar_chart(
                df=df,
                x_col="month_label",
                y_col=absolute_columns[0],
                label=indicator_data.get_labels()[0],
                color=indicator_data.get_colors()[0],
                x_title="Mês",
                y_title=indicator_data.absolute_title,
            )
        else:
            # Multiple columns - use stacked bar chart
            absolute_chart = create_stacked_bar_chart(
                df=df,
                x_col="month_label",
                y_cols=absolute_columns,
                labels=indicator_data.get_labels(),
                colors=indicator_data.get_colors(),
                x_title="Mês",
                y_title=indicator_data.absolute_title,
            )

        # Create relative chart with reference line if available
        reference_line = indicator_data.get_reference_line()

        relative_columns = indicator_data.get_relative_columns()
        if len(relative_columns) == 1:
            # Single column - use line chart
            relative_chart = create_line_chart(
                df=df,
                x_col="month_label",
                y_col=relative_columns[0],
                label=indicator_data.get_labels()[0],
                color=indicator_data.get_colors()[0],
                x_title="Mês",
                y_title=indicator_data.relative_title,
                reference_line=reference_line,
            )
        else:
            # Multiple columns - use multi-line chart
            relative_chart = create_multi_line_chart(
                df=df,
                x_col="month_label",
                y_cols=relative_columns,
                labels=indicator_data.get_labels(),
                colors=indicator_data.get_colors(),
                x_title="Mês",
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
            Output("annual-indicator-pie-chart", "figure"),
            Output("annual-indicator-pie-title", "children"),
        ],
        Input("annual-indicator-type-dropdown", "value"),
        Input("annual-indicator-month-dropdown", "value"),
        Input("annual-year-slider", "value"),
    )
    def update_indicator_pie_chart(selected_indicator, selected_month, selected_year):
        """Update the pie chart based on the selected indicator."""
        df = data_loader.load_monthly_aggregates(selected_year)

        # Get the selected indicator's data
        indicator_data = INDICATOR_MAPPINGS[selected_indicator]

        # For pie chart, we use the first absolute column
        absolute_col = indicator_data.get_absolute_columns()[0]

        total: int = int(df.loc[df["month"] == selected_month + 1, absolute_col].sum())  # type: ignore
        other: int = df.loc[df["month"] == selected_month + 1, "total_births"].sum() - total  # type: ignore

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
            Output("annual-indicator-absolute-map-chart", "figure"),
            Output("annual-indicator-relative-map-chart", "figure"),
            Output("annual-indicator-absolute-map-title", "children"),
            Output("annual-indicator-relative-map-title", "children"),
        ],
        Input("annual-indicator-type-dropdown", "value"),
        Input("annual-year-slider", "value"),
        Input("annual-indicator-month-dropdown", "value"),
    )
    def update_indicator_maps(selected_indicator, selected_year, selected_month):
        """Update both absolute and relative choropleth maps for the selected indicator and year."""
        df = data_loader.load_monthly_state_aggregates(selected_year)
        df = df[df["month"] == selected_month]

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

        title_text = f"Mapa de {label} ({MONTH_NAMES[selected_month - 1]}/{selected_year})"
        rel_title_text = f"Mapa de Taxa de {label} ({MONTH_NAMES[selected_month - 1]}/{selected_year})"

        return abs_map, rel_map, title_text, rel_title_text

    # @app.callback(
    #     [
    #         Output("annual-maternal-occupation-pie-chart", "figure"),
    #         Output("annual-maternal-occupation-pie-title", "children"),
    #     ],
    #     Input("annual-year-slider", "value"),
    #     Input("annual-indicator-month-dropdown", "value"),
    # )
    # def update_maternal_occupation_chart(year: int, month: int):
    #     """
    #     Update maternal occupation distribution chart using metadata summary.

    #     Args:
    #         year: Selected year for data filtering

    #     Returns:
    #         Tuple of (Plotly figure object, dynamic title string)
    #     """
    #     summary = data_loader.get_year_summary(year)
    #     maternal_occupation = summary.get("maternal_occupation", {})

    #     # Build a clean DataFrame: expected structure is {code: {"label": str, "count": int}}
    #     rows = []
    #     if isinstance(maternal_occupation, dict) and maternal_occupation:
    #         for code, info in maternal_occupation.items():
    #             if isinstance(info, dict):
    #                 label = info.get("label", str(code))
    #                 count = int(info.get("count", 0) or 0)
    #             else:
    #                 # backward compatibility: if value is just a count
    #                 label = str(code)
    #                 try:
    #                     count = int(info)
    #                 except Exception:
    #                     count = 0

    #             rows.append({"code": str(code), "label": label, "count": count})

    #     occupation_counts = pd.DataFrame(rows)

    #     # Remove zero counts (they clutter the pie) and sort by count desc
    #     occupation_counts = occupation_counts[occupation_counts["count"] > 0].sort_values("count", ascending=False)

    #     palette = px.colors.qualitative.Prism
    #     colors = [palette[i % len(palette)] for i in range(len(occupation_counts))]

    #     # Create pie chart with smaller text and tighter margins so the pie fills the card
    #     fig = go.Figure(
    #         data=[
    #             go.Pie(
    #                 labels=occupation_counts["label"],
    #                 values=occupation_counts["count"],
    #                 hole=0.4,
    #                 textinfo="label+percent",
    #                 textposition="inside",
    #                 marker=dict(colors=colors, line=dict(color="white", width=0.5)),
    #             )
    #         ]
    #     )

    #     fig.update_traces(textfont_size=12, insidetextorientation="radial")

    #     fig.update_layout(
    #         template="plotly_white",
    #         showlegend=False,
    #         legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.02),
    #         margin=dict(t=40, b=10, l=10, r=80),
    #         height=int(CHART_HEIGHT),
    #     )

    #     title = f"Distribuição de Ocupação Materna - {year}"

    #     return fig, title


# Layout for routing
layout = create_layout()
