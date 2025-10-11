import dash_bootstrap_components as dbc
from dash import html


def create_year_summary_card(year: int, summary: dict) -> dbc.Card:
    """
    Create a responsive card summarizing a specific year's statistics with improved layout.

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
    cesarean_rate = summary.get("delivery_type", {}).get("cesarean_pct", 0)
    preterm_rate = summary.get("pregnancy", {}).get("preterm_pct", 0)

    return dbc.Card(
        [
            dbc.CardHeader(
                html.Div(
                    [
                        # html.I(className="fas fa-calendar fa-2x text-secondary px-2 mb-0"),
                        html.P(f"{year}", className="text-secondary mb-0"),  # fw-bold
                    ],
                    className="d-flex align-items-center",
                ),
                className="p-2 bg-light text-start border-bottom",
            ),
            dbc.CardBody(
                [
                    # Total births - primary metric on the left
                    dbc.Row(
                        [
                            dbc.Col(
                                html.Div(
                                    [
                                        html.P("Nascimentos Totais", className="text-muted mb-0"),
                                        html.H2(formatted_births, className="text-primary fw-bold mb-1"),
                                    ],
                                    className="text-start",
                                ),
                                xs=12,
                                sm=12,
                                md=7,
                                lg=7,
                                xl=7,
                            ),
                            # Cesarean and Preterm rates - secondary metrics on the right
                            dbc.Col(
                                [
                                    html.Div(
                                        [
                                            html.P("Cesáreas", className="text-muted mb-0 me-1"),
                                            html.H5(f"{cesarean_rate:.1f}%".replace(".", ","), className="text-warning fw-bold mb-0"),
                                        ],
                                        className="d-flex align-items-center justify-content-between mb-2",
                                    ),
                                    html.Div(
                                        [
                                            html.P("Prematuros", className="text-muted mb-0 me-1"),
                                            html.H5(f"{preterm_rate:.1f}%".replace(".", ","), className="text-danger fw-bold mb-0"),
                                        ],
                                        className="d-flex align-items-center justify-content-between",
                                    ),
                                ],
                                xs=12,
                                sm=12,
                                md=5,
                                lg=5,
                                xl=5,
                            ),
                        ],
                        className="mb-3",
                    ),
                    # Less important metrics at the bottom
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    html.P("Baixo Peso", className="text-muted my-1 text-center"),
                                    html.P(f"{low_birth_weight_rate:.1f}%".replace(".", ","), className="text-muted fw-bold my-1 text-center"),
                                ],
                                xs=6,
                                sm=4,
                                md=4,
                                lg=4,
                                xl=4,
                            ),
                            dbc.Col(
                                [
                                    html.P("Adolescentes", className="text-muted my-1 text-center"),
                                    html.P(
                                        f"{adolescent_pregnancy_rate:.1f}%".replace(".", ","), className="text-muted fw-bold my-1 text-center"
                                    ),
                                ],
                                xs=6,
                                sm=4,
                                md=4,
                                lg=4,
                                xl=4,
                            ),
                            dbc.Col(
                                [
                                    html.P("APGAR5 Baixo", className="text-muted my-1 text-center"),
                                    html.P(f"{low_apgar5_rate:.1f}%".replace(".", ","), className="text-muted fw-bold my-1 text-center"),
                                ],
                                xs=12,
                                sm=4,
                                md=4,
                                lg=4,
                                xl=4,
                            ),
                        ],
                        className="g-2",
                    ),
                ]
            ),
        ],
        className="shadow h-100",
    )


def create_metric_card(
    title: str,
    value: str,
    icon: str,
    color: str = "primary",
    yoy_change: float | None = None,
) -> dbc.Card:
    """
    Create a metric display card.

    Args:
        title: Card title
        value: Metric value to display
        icon: Font Awesome icon class
        color: Bootstrap color theme
        yoy_change: Year-over-year percentage change (e.g., 5.2 for +5.2% or -3.1 for -3.1%)

    Returns:
        Bootstrap Card component
    """
    # Build year-over-year change badge (top-right corner)
    yoy_badge = None
    if yoy_change is not None:
        is_positive = yoy_change > 0
        is_negative = yoy_change < 0

        # Format with Brazilian decimal separator
        change_text = f"{abs(yoy_change):.1f}%".replace(".", ",")

        # Determine color and icon with transparent background
        if is_positive:
            badge_color = "rgba(25, 135, 84, .75)"  # success with 85% opacity
            icon_class = "fas fa-arrow-up"
            prefix = "+"
        elif is_negative:
            badge_color = "rgba(220, 53, 69, .75)"  # danger with 85% opacity
            icon_class = "fas fa-arrow-down"
            prefix = "-"
        else:
            badge_color = "rgba(108, 117, 125, .75)"  # secondary with 85% opacity
            icon_class = "fas fa-minus"
            prefix = ""

        yoy_badge = html.Div(
            [
                html.I(className=f"{icon_class} me-1", style={"fontSize": "10px"}),
                html.Span(f"{prefix}{change_text}", className="fw-bold"),
            ],
            className="badge position-absolute top-0 end-0 m-2 p-2 text-white",
            style={
                "fontSize": "10px",
                "backgroundColor": badge_color,
            },
        )

    return dbc.Card(
        dbc.CardBody(
            [
                # Year-over-year change badge (if provided)
                yoy_badge if yoy_badge else html.Div(),
                html.Div(
                    [
                        html.I(
                            className=f"fas {icon} fa-2x mb-2 text-{color}",
                        ),
                        html.H4(value, className=f"text-{color} fw-bold mb-1"),
                        html.P(title, className="text-muted mb-0 small"),
                    ],
                    className="text-center",
                ),
            ]
        ),
        className="shadow-sm h-100 position-relative",
    )
