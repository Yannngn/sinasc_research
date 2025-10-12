"""
Map visualization components for geographic analysis.
"""

import dash_bootstrap_components as dbc
import plotly.express as px
from config.settings import CHART_CONFIG
from dash import dcc, html


def create_choropleth_map(
    df,
    geojson_data,
    locations_col: str,
    color_col: str,
    color_label: str,
    hover_name_col: str,
    hover_data: dict | None = None,
    color_scale: str = "Blues",
    height: int = 500,
) -> dcc.Graph | html.Div:
    """
    Create a choropleth map for geographic regions.

    Args:
        df: DataFrame with geographic data
        geojson_data: GeoJSON dictionary for boundaries
        locations_col: Column containing location codes
        color_col: Column to color by
        color_label: Label for color axis
        hover_name_col: Column for hover name
        hover_data: Dict of columns to show in hover
        color_scale: Plotly color scale
        height: Map height in pixels

    Returns:
        Dash Graph component or Div with error message
    """
    try:
        if not geojson_data or not geojson_data.get("features"):
            return html.Div(
                dbc.Alert(
                    [
                        html.I(className="fas fa-info-circle me-2"),
                        "Dados geográficos não disponíveis.",
                    ],
                    color="info",
                ),
                className="d-flex align-items-center justify-content-center",
                style={"minHeight": f"{height}px"},
            )

        # Default hover data
        if hover_data is None:
            hover_data = {
                locations_col: False,
                color_col: ":.1f",
            }

        fig = px.choropleth(
            df,
            geojson=geojson_data,
            locations=locations_col,
            featureidkey="properties.id",
            color=color_col,
            hover_name=hover_name_col,
            hover_data=hover_data,
            color_continuous_scale=color_scale,
            labels={color_col: color_label},
        )

        fig.update_geos(
            fitbounds="geojson",
            visible=False,
        )

        fig.update_layout(
            template="plotly_white",
            margin=dict(l=0, r=0, t=0, b=0),
            font=dict(family="Inter, sans-serif"),
            height=height,
            coloraxis_colorbar=dict(
                title=color_label,
                thickness=15,
                len=0.7,
            ),
        )

        return dcc.Graph(figure=fig, config=CHART_CONFIG)  # type: ignore

    except Exception as e:
        return html.Div(
            dbc.Alert(
                [
                    html.I(className="fas fa-exclamation-circle me-2"),
                    f"Erro ao carregar mapa: {str(e)}",
                ],
                color="warning",
            ),
            className="d-flex align-items-center justify-content-center",
            style={"minHeight": f"{height}px"},
        )
