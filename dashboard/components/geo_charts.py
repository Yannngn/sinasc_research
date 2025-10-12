from typing import Any

import pandas as pd
import plotly.express as px
from config.geographic import get_region_from_id_code, get_state_from_id_code

_original_px_choropleth = px.choropleth


def _format_brazil_number(value: Any, is_percent: bool) -> str:
    """
    Format a numeric value using Brazilian locale rules:
    - Thousands separator: '.'
    - Decimal separator: ','
    - Percent values get a trailing '%' and are scaled if in [ -1, 1 ].

    Args:
        value: Numeric value to format.
        is_percent: Whether to format as percent.

    Returns:
        Formatted string.
    """
    try:
        v = float(value)
    except Exception:
        return "-" if pd.isna(value) else str(value)

    if pd.isna(v):
        return "-"

    if is_percent:
        # If given as fraction (0-1), convert to percent
        if abs(v) <= 1:
            v *= 100.0
        s = f"{v:,.1f}"  # English style: 12,345.6
        # Swap to Brazilian style: 12.345,6
        s = s.replace(",", "X").replace(".", ",").replace("X", ".")
        return f"{s}%"

    # Absolute numbers: integers show no decimals, floats show one decimal
    if abs(v - round(v)) < 1e-6:
        s = f"{int(round(v)):,}"
        s = s.replace(",", "X").replace(".", ",").replace("X", ".")
        return s
    else:
        s = f"{v:,.1f}"
        s = s.replace(",", "X").replace(".", ",").replace("X", ".")
        return s


def _wrapped_choropleth(*args, **kwargs):
    """
    Wrapper around plotly.express.choropleth to:
    - Add a formatted customdata column for Brazilian number formatting (hover).
    - Set a hovertemplate showing state name and the formatted value.
    - Provide colorbar tickvals/ticktext using Brazilian formatting and percent title when applicable.
    - Round (ceil) legend ranges to "nice" numbers (e.g., 467809 -> 500k; 24.7% -> 25%).
    """
    label = kwargs.pop("title", kwargs.get("color"))

    fig = _original_px_choropleth(*args, **kwargs)

    # Try to retrieve the dataframe and color column name
    df = None
    if args:
        df = args[0]
    elif "data_frame" in kwargs:
        df = kwargs["data_frame"]

    color_col = kwargs.get("color")

    is_percent = False
    if isinstance(color_col, str) and (("_pct" in color_col) or ("rate" in color_col.lower())):
        is_percent = True

    # Only proceed if we have a DataFrame and the color column exists
    if isinstance(df, pd.DataFrame) and isinstance(color_col, str) and color_col in df.columns:
        # Prepare formatted strings for hover
        formatted_values = df[color_col].apply(lambda v: _format_brazil_number(v, is_percent)).tolist()

        # Attach formatted values as customdata to each trace and set hovertemplate
        pretty_label = label.replace("_", " ").capitalize()
        for trace in fig.data:
            # customdata expects an array of arrays for multiple columns; we provide single column
            trace.customdata = [[fv] for fv in formatted_values]  # type:ignore
            # Use hovertext (from hover_name) and customdata[0] for the formatted value
            trace.hovertemplate = "<b>%{hovertext}</b><br>" + f"{pretty_label}: " + "%{customdata[0]}<extra></extra>"  # type:ignore

    return fig


# Patch plotly.express.choropleth so calls in this module pick up Brazilian formatting
px.choropleth = _wrapped_choropleth


def create_choropleth_chart(
    df: pd.DataFrame, geojson: dict, indicator: str, color: str, title: str | None = None, color_scale: str = "Viridis"
):
    """
    Create a generic choropleth chart.

    Args:
        df: DataFrame containing the data.
        geojson: GeoJSON object for geographic boundaries.
        locations: Column in df that matches GeoJSON feature IDs.
        color: Column in df to use for coloring the map.
        title: Title of the chart.
        color_scale: Color scale for the chart.

    Returns:
        Plotly Figure object.
    """

    is_percent = ("_pct" in indicator) or ("rate" in indicator.lower())
    df = df.copy()
    if "state_code" in df.columns:
        df["state_code"] = df["state_code"].astype(str).str.zfill(2)

    # Ensure state_name for nicer hover
    if "state_name" not in df.columns:
        df["state_name"] = df["state_code"].apply(get_state_from_id_code)

    fig = px.choropleth(
        df,
        geojson=geojson,
        locations="state_code",
        featureidkey="properties.id",
        color=color,
        color_continuous_scale=color_scale,
        title=title,
        hover_name="state_name" if "state_name" in df.columns else None,
    )

    fig.update_geos(
        fitbounds="locations",
        visible=False,
        projection_type="mercator",
        center=dict(lat=-14.2350, lon=-51.9253),
    )
    fig.update_layout(
        template="plotly_white",
        margin=dict(l=10, r=10, t=20, b=10),
        coloraxis_colorbar=dict(
            title="%" if is_percent else "",
            ticksuffix="%" if is_percent else "",
        ),
    )

    return fig


def create_state_scatter_plot(df: pd.DataFrame, indicator: str, indicator_label: str) -> Any:
    """
    Create a scatter plot of total births vs indicator by state.

    Args:
        df: DataFrame with state data including state_abbr, region_name, total_births
        indicator: Column name for y-axis
        indicator_label: Human-readable label for y-axis

    Returns:
        Plotly Figure object
    """
    from config.constants import BRAZILIAN_STATES
    from config.geographic import get_state_from_id_code

    df = df.copy()
    df["state_name"] = df["state_code"].apply(get_state_from_id_code)
    df["region_name"] = df["state_code"].apply(get_region_from_id_code)
    df["state_abbr"] = df["state_code"].apply(lambda x: BRAZILIAN_STATES.get(x, {}).get("abbr", ""))

    x_col = "total_births" if "_count" in indicator else "births_per_1k"
    y_col = indicator
    fig = px.scatter(
        df,
        x=x_col,
        y=y_col,
        size="total_births",
        color="region_name",
        text="state_abbr",
        hover_name="state_name",
        custom_data=["total_births", y_col],
        size_max=50,
        color_discrete_sequence=px.colors.qualitative.Set2,
    )

    # Keep hover showing only x (per 1k), y (indicator) and size (total births) with clearer labels
    hovertemplate = (
        "<b>%{hovertext}</b><br>"
        "Nascimentos por 1.000 habitantes: %{x:.1f}<br>"
        f"{indicator_label}:"
        "%{customdata[1]:.2f}<br>"
        "Total nascimentos: %{customdata[0]:,}<extra></extra>"
    )
    fig.update_traces(hovertemplate=hovertemplate)
    fig.update_traces(textposition="top center", textfont=dict(size=10))
    fig.update_layout(
        template="plotly_white",
        xaxis_title="Nascimentos por 1.000 habitantes",
        yaxis_title=indicator_label,
        showlegend=True,
        legend=dict(title="Região", orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=60, r=40, t=50, b=40),
        font=dict(family="Inter, sans-serif"),
    )
    return fig
