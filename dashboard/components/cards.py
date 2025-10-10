import dash_bootstrap_components as dbc
from dash import html


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
    cesarean_rate = summary.get("delivery_type", {}).get("cesarean_pct", 0)
    preterm_rate = summary.get("pregnancy", {}).get("preterm_pct", 0)
    hospital_rate = summary.get("location", {}).get("hospital_birth_pct", 0)

    return dbc.Card(
        [
            dbc.CardHeader(
                html.Div(
                    [
                        html.I(className="fas fa-calendar fa-2x text-white mb-2 px-2"),
                        html.H3(f"{year}", className="mb-0 text-center text-white fw-bold"),
                    ],
                    className="d-flex align-items-center justify-content-center",
                ),
                className="bg-primary text-center  mb-3 pb-3 border-bottom",
            ),
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
                                            html.I(
                                                className="fas fa-weight-hanging text-warning me-1",
                                                style={"fontSize": "14px"},
                                            ),
                                            html.Strong("Baixo Peso: ", className="small"),
                                            html.Span("_", className="text-white"),  # Spacer
                                            html.Span(
                                                f"{low_birth_weight_rate:.1f}%".replace(".", ","),
                                                className="small text-muted",
                                            ),
                                        ],
                                        className="mb-2 d-flex align-items-center",
                                    ),
                                    # Adolescent pregnancy rate
                                    html.Div(
                                        [
                                            html.I(
                                                className="fas fa-user-friends text-info me-1",
                                                style={"fontSize": "14px"},
                                            ),
                                            html.Strong("Adolescentes: ", className="small"),
                                            html.Span("_", className="text-white"),  # Spacer
                                            html.Span(
                                                f"{adolescent_pregnancy_rate:.1f}%".replace(".", ","),
                                                className="small text-muted",
                                            ),
                                        ],
                                        className="mb-2 d-flex align-items-center",
                                    ),
                                    # Low APGAR5 rate
                                    html.Div(
                                        [
                                            html.I(
                                                className="fas fa-heartbeat text-danger me-1",
                                                style={"fontSize": "14px"},
                                            ),
                                            html.Strong("APGAR5 Baixo: ", className="small"),
                                            html.Span("_", className="text-white"),  # Spacer
                                            html.Span(
                                                f"{low_apgar5_rate:.1f}%".replace(".", ","),
                                                className="small text-muted",
                                            ),
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
                                            html.I(
                                                className="fas fa-procedures text-warning me-1",
                                                style={"fontSize": "14px"},
                                            ),
                                            html.Strong("Cesárea: ", className="small"),
                                            html.Span("_", className="text-white"),  # Spacer
                                            html.Span(
                                                f"{cesarean_rate:.1f}%".replace(".", ","),
                                                className="small text-muted",
                                            ),
                                        ],
                                        className="mb-2 d-flex align-items-center",
                                    ),
                                    # Preterm rate
                                    html.Div(
                                        [
                                            html.I(
                                                className="fas fa-exclamation-triangle text-danger me-1",
                                                style={"fontSize": "14px"},
                                            ),
                                            html.Strong("Prematuros: ", className="small"),
                                            html.Span("_", className="text-white"),  # Spacer
                                            html.Span(
                                                f"{preterm_rate:.1f}%".replace(".", ","),
                                                className="small text-muted",
                                            ),
                                        ],
                                        className="mb-2 d-flex align-items-center",
                                    ),
                                    # Hospital births
                                    html.Div(
                                        [
                                            html.I(
                                                className="fas fa-hospital text-primary me-1",
                                                style={"fontSize": "14px"},
                                            ),
                                            html.Strong("Hospitalar: ", className="small"),
                                            html.Span("_", className="text-white"),  # Spacer
                                            html.Span(
                                                f"{hospital_rate:.1f}%".replace(".", ","),
                                                className="small text-muted",
                                            ),
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
