"""
Chart generation helper functions - Reusable components for creating common chart types.
"""

import copy

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from config.settings import COLOR_CONTINUOS_PALETTE, COLOR_PALETTE, COMMON_LAYOUT, LEGEND_CONFIG


def format_brazilian_number(value: int | float) -> str:
    """
    Format integer with Brazilian number format (dots as thousands separator).

    Args:
        value: Number to format

    Returns:
        Formatted string (e.g., 1000 -> "1.000")
    """
    if isinstance(value, float):
        return f"{value:_}".replace(".", ",").replace("_", ".")

    return f"{int(value):_}".replace("_", ".")


def format_hovertext(value: int | float) -> str:
    """
    Format hovertext with Brazilian number format and rounding for floats.

    Args:
        value: Number to format

    Returns:
        Formatted string for hovertext
    """
    if isinstance(value, float):
        # Round to 2 decimal places and format with Brazilian style
        return f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{int(value):_}".replace("_", ".")


def generate_hovertemplate_general(value_label: str) -> str:
    """
    Generate a general hovertemplate with a title and value label.

    Args:
        title: General title for the hovertemplate.
        value_label: Label for the value being displayed.

    Returns:
        A formatted hovertemplate string.
    """
    return f"{value_label}: %{{customdata}}<extra></extra>"


def generate_hovertemplate_pie(label: str) -> str:
    """
    Generate a hovertemplate for pie charts with a label.

    Args:
        label: General label for the hovertemplate.

    Returns:
        A formatted hovertemplate string for pie charts.
    """
    return f"<b>{label}</b><br>" + "%{customdata}<br>" + "%{percent}<extra></extra>"


def create_pie_chart(
    df,
    names_col: str,
    values_col: str,
    color_keys: list | None = None,
    textinfo: str = "percent+label",
    hole: float = 0.0,
) -> go.Figure:
    """
    Create a pie (or donut) chart with Brazilian-formatted hover/labels.

    Args:
        df: DataFrame with data
        names_col: Column name for category labels
        values_col: Column name for numeric values
        title: Chart title
        color_keys: Optional list of keys from COLOR_PALETTE to use for slices (order must match categories)
        textinfo: What to display on slices (Plotly textinfo string, e.g. 'percent+label', 'value+label')
        hole: Fraction of radius to cut out of the middle (0.0 for pie, >0 for donut)

    Returns:
        Plotly Figure object

    Raises:
        ValueError: If specified color_keys length doesn't match number of categories
    """
    # Prepare formatted values for hover/customdata (Brazilian style)
    formatted_values = [format_hovertext(val) for val in df[values_col]]

    # Determine colors for slices
    colors_list = None
    if color_keys is not None:
        if len(color_keys) != len(df[names_col]):
            # allow color_keys to be fewer (reused) but if strictly mismatched warn by raising
            raise ValueError("color_keys length must match number of categories")
        colors_list = [COLOR_PALETTE.get(k, k) for k in color_keys]

    fig = go.Figure(
        go.Pie(
            labels=df[names_col],
            values=df[values_col],
            hole=hole,
            textinfo=textinfo,
            texttemplate="%{label}<br>%{percent}",
            customdata=formatted_values,
            hovertemplate=generate_hovertemplate_pie("%{label}"),
            marker=dict(colors=colors_list) if colors_list is not None else None,
            sort=False,
        )
    )

    # Local layout + legend copy
    layout = copy.deepcopy(COMMON_LAYOUT)

    # Adjust margins for donut labels if necessary
    if hole and hole >= 0.4:
        layout["margin"] = {**layout.get("margin", {}), "t": 60, "b": 40, "l": 40, "r": 40}

    fig.update_layout(
        **layout,
        showlegend=False,
    )

    return fig


def create_bar_chart(
    df,
    x_col: str,
    y_col: str,
    label: str,
    color: str,
    x_title: str,
    y_title: str,
) -> go.Figure:
    """
    Create a simple bar chart with formatted text labels and Brazilian-style hover.

    Args:
        df: DataFrame with data
        x_col: Column name for x-axis
        y_col: Column name for y-axis
        x_title: X-axis title
        y_title: Y-axis title
        color: Color key from COLOR_PALETTE

    Returns:
        Plotly Figure object
    """
    fig = go.Figure()

    # Formatted values for bar text and hover (Brazilian style: dots thousands, comma decimals)
    formatted_values = [format_hovertext(val) for val in df[y_col]]

    fig.add_trace(
        go.Bar(
            x=df[x_col],
            y=df[y_col],
            name=label,
            marker_color=COLOR_PALETTE[color],
            customdata=formatted_values,
            text=formatted_values,
            textposition="inside",
            textfont=dict(size=11, color="white"),
            hovertemplate=generate_hovertemplate_general(y_title),
        )
    )

    # Determine y-axis range
    max_value = df[y_col].max()
    y_axis_max = max_value * 1.25  # 25% padding above for outside text
    y_axis_config = {"range": [0, y_axis_max]}

    # Use a deep copy of the shared layout so we don't mutate the global
    layout = copy.deepcopy(COMMON_LAYOUT)
    # Merge/replace yaxis settings on the local layout copy
    layout["yaxis"] = {**layout.get("yaxis", {}), **y_axis_config}

    fig.update_layout(
        **layout,
        xaxis_title=x_title,
        yaxis_title=y_title,
        showlegend=False,
    )

    return fig


def create_line_chart(
    df,
    x_col: str,
    y_col: str,
    label: str,
    color: str,
    x_title: str,
    y_title: str,
    reference_line: dict | None = None,
) -> go.Figure:
    """
    Create a line chart with markers.

    Args:
        df: DataFrame with data
        x_col: Column name for x-axis
        y_col: Column name for y-axis
        x_title: X-axis title
        y_title: Y-axis title
        color: Color key from COLOR_PALETTE
        reference_line: Optional dict with keys 'y', 'text', 'color' for horizontal reference line

    Returns:
        Plotly Figure object
    """
    fig = go.Figure()

    formatted_values = [format_hovertext(val) for val in df[y_col]]

    fig.add_trace(
        go.Scatter(
            x=df[x_col],
            y=df[y_col],
            mode="lines+markers",
            name=label,
            line=dict(color=COLOR_PALETTE[color], width=3),
            marker=dict(size=10),
            text=label,
            customdata=formatted_values,
            hovertemplate=generate_hovertemplate_general(label),
        )
    )

    # Add reference line if provided
    if reference_line:
        fig.add_hline(
            y=reference_line.get("y"),
            line_dash="dash",
            line_color=COLOR_PALETTE.get(reference_line.get("color", "neutral")),
            annotation_text=reference_line.get("text", ""),
        )

    max_value = df[y_col].max()
    y_axis_max = max_value * 1.25  # 25% padding above for outside text
    y_axis_config = {"range": [0, y_axis_max]}

    # Local layout copy
    layout = copy.deepcopy(COMMON_LAYOUT)
    layout["yaxis"] = {**layout.get("yaxis", {}), **y_axis_config}
    if reference_line:
        # update margin only on the local copy
        layout["margin"] = {**layout.get("margin", {}), "r": 125}
    legend = copy.deepcopy(LEGEND_CONFIG)

    fig.update_layout(
        **layout,
        xaxis_title=x_title,
        yaxis_title=y_title,
        legend=legend,
    )

    return fig


def create_stacked_bar_chart(
    df: pd.DataFrame,
    x_col: str,
    y_cols: list,
    labels: list,
    colors: list,
    x_title: str,
    y_title: str,
    subtract: bool = True,
) -> go.Figure:
    """
    Create a stacked bar chart with two categories.

    Args:
        df: DataFrame with data
        x_col: Column name for x-axis
        y_cols: List of two column names for y-axis values [bottom_stack, top_stack]
        labels: List of two labels for legend [bottom_label, top_label]
        colors: List of two color keys from COLOR_PALETTE [bottom_color, top_color]
        x_title: X-axis title
        y_title: Y-axis title
        subtract: If True, the top stack is a subset of the bottom stack and will be subtracted for correct stacking.

    Returns:
        Plotly Figure object
    """

    if subtract:
        df = df.copy()

        df[y_cols[0]] = df[y_cols[0]] - df[y_cols[1]]
        df[y_cols[1]] = df[y_cols[1]]

    fig = go.Figure()

    for y_col, label, color, text_position in zip(y_cols, labels, colors, ["inside", "outside"]):
        formatted_values = [format_hovertext(val) for val in df[y_col]]
        fig.add_trace(
            go.Bar(
                x=df[x_col],
                y=df[y_col],
                name=label,
                marker_color=COLOR_PALETTE[color],
                customdata=formatted_values,
                text=formatted_values,
                textposition=text_position,
                textfont=dict(size=11, color="white"),
                hovertemplate=generate_hovertemplate_general(label),
            )
        )

    # Calculate max value for y-axis with padding for outside text
    total_col = df[y_cols[0]] + df[y_cols[1]]
    max_value = total_col.max()
    y_axis_max = max_value * 1.25  # 25% padding above for outside text
    y_axis_config = {"range": [0, y_axis_max]}

    # Local layout + legend copy
    layout = copy.deepcopy(COMMON_LAYOUT)
    layout["yaxis"] = {**layout.get("yaxis", {}), **y_axis_config}
    legend = copy.deepcopy(LEGEND_CONFIG)

    fig.update_layout(
        **layout,
        xaxis_title=x_title,
        yaxis_title=y_title,
        barmode="stack",
        legend=legend,
    )

    return fig


def create_multi_line_chart(
    df,
    x_col: str,
    y_cols: list,
    labels: list,
    colors: list,
    x_title: str,
    y_title: str,
    reference_line: dict | None = None,
) -> go.Figure:
    """
    Create a chart with multiple line traces.

    Args:
        df: DataFrame with data
        x_col: Column name for x-axis
        y_cols: List of column names for y-axis values
        labels: List of labels for legend (same length as y_cols)
        colors: List of color keys from COLOR_PALETTE (same length as y_cols)
        x_title: X-axis title
        y_title: Y-axis title
        reference_line: Optional dict with keys 'y', 'text', 'color' for horizontal reference line

    Returns:
        Plotly Figure object
    """
    fig = go.Figure()

    # Add each line trace
    for y_col, label, color in zip(y_cols, labels, colors):
        formatted_values = [format_hovertext(val) for val in df[y_col]]

        fig.add_trace(
            go.Scatter(
                x=df[x_col],
                y=df[y_col],
                mode="lines+markers",
                name=label,
                line=dict(color=COLOR_PALETTE[color], width=3),
                marker=dict(size=10),
                text=label,
                customdata=formatted_values,
                hovertemplate=generate_hovertemplate_general(label),
            )
        )

    # Add reference line if provided
    if reference_line:
        fig.add_hline(
            y=reference_line.get("y"),
            line_dash="dash",
            line_color=COLOR_PALETTE.get(reference_line.get("color", "neutral")),
            annotation_text=reference_line.get("text", ""),
            annotation_position="right",
        )

    # Determine y-axis range
    max_value = df[y_cols].max().max()
    y_axis_max = max_value * 1.25  # 25% padding above for outside text
    y_axis_config = {"range": [0, y_axis_max]}

    # Local layout + legend copies
    layout = copy.deepcopy(COMMON_LAYOUT)
    layout["yaxis"] = {**layout.get("yaxis", {}), **y_axis_config}
    if reference_line:
        layout["margin"] = {**layout.get("margin", {}), "r": 125}
    legend = copy.deepcopy(LEGEND_CONFIG)

    fig.update_layout(
        **layout,
        xaxis_title=x_title,
        yaxis_title=y_title,
        legend=legend,
    )

    return fig


def create_colored_bar_chart(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    color_col: str,
    label: str,
    color: str,
    x_title: str,
    y_title: str,
) -> go.Figure:
    """
    Create a bar chart with bars colored by a column using a continuous palette.

    Args:
        df: DataFrame with data
        x_col: Column name for x-axis
        y_col: Column name for y-axis
        color_col: Column name to determine bar colors (each unique value gets a color from palette)
        label: Trace label for legend/hover
        color: Key to lookup continuous palette name in COLOR_CONTINUOS_PALETTE, or fallback to COLOR_PALETTE
        x_title: X-axis title
        y_title: Y-axis title

    Returns:
        Plotly Figure object
    """
    fig = go.Figure()
    formatted_values = [format_hovertext(val) for val in df[y_col]]

    # Determine colors for bars
    if color_col and color_col in df.columns:
        # Get palette name from COLOR_CONTINUOS_PALETTE or use fallback
        palette_name = COLOR_CONTINUOS_PALETTE.get(color, "Viridis")

        # Get the palette from plotly.express.colors.sequential
        palette = getattr(px.colors.sequential, palette_name, px.colors.sequential.Viridis)

        # Get unique values and assign colors cyclically from palette
        unique_values = df[color_col].unique()
        color_map = {val: palette[i % len(palette)] for i, val in enumerate(unique_values)}
        colors_list = [color_map[val] for val in df[color_col]]
    else:
        # No color column: use single color from COLOR_PALETTE
        colors_list = COLOR_PALETTE.get(color, color)  # type: ignore

    fig.add_trace(
        go.Bar(
            x=df[x_col],
            y=df[y_col],
            name=label,
            marker=dict(color=colors_list),
            customdata=formatted_values,
            text=formatted_values,
            textposition="inside",
            textfont=dict(size=11, color="white"),
            hovertemplate=generate_hovertemplate_general(y_title),
        )
    )

    # Use a local copy of the common layout for consistency with other charts
    layout = copy.deepcopy(COMMON_LAYOUT)
    fig.update_layout(
        **layout,
        showlegend=False,
        xaxis_title=x_title,
        yaxis_title=y_title,
    )

    return fig


def create_ranking_bar_chart(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    x_title: str,
    y_title: str,
    text_formatter,
    orientation: str = "h",
    color: str = "primary",
    height: int | None = None,
) -> go.Figure:
    """
    Create a horizontal or vertical bar chart for rankings.

    Args:
        df: DataFrame with data (should be pre-sorted)
        x_col: Column name for x-axis (categories for horizontal, values for vertical)
        y_col: Column name for y-axis (values for horizontal, categories for vertical)
        x_title: X-axis title
        y_title: Y-axis title
        text_formatter: Function to format bar text values
        orientation: 'h' for horizontal, 'v' for vertical
        color: Color key from COLOR_PALETTE
        height: Optional height in pixels

    Returns:
        Plotly Figure object
    """
    fig = go.Figure()
    value_col = x_col if orientation == "h" else y_col

    # Format text for bars (use the numeric column)
    text_values = [text_formatter(val) for val in df[value_col]]
    hover_values = [format_hovertext(val) for val in df[value_col]]

    fig.add_trace(
        go.Bar(
            x=df[x_col],
            y=df[y_col],
            orientation=orientation,
            marker_color=COLOR_PALETTE[color],
            text=text_values,
            textposition="inside",
            textfont=dict(size=11, color="white"),
            customdata=hover_values,
            hovertemplate=generate_hovertemplate_general(y_title if orientation == "h" else x_title),
        )
    )

    # Determine axis range and create ticks for horizontal orientation
    max_value = df[value_col].max()
    layout = copy.deepcopy(COMMON_LAYOUT)
    axis_max = max_value * 1.25 if max_value and max_value > 0 else max_value or 0.0  # 25% padding for outside text
    axis_config = {"range": [0, axis_max]}

    if orientation == "h":
        # Generate nice tick values for x-axis (include 0 and axis_max)
        tick_count = 5  # number of ticks to show
        if axis_max <= 0:
            tick_vals = [0.0]
            tick_text = [format_hovertext(0)]
        else:
            step = axis_max / (tick_count - 1)
            tick_vals = [round(step * i, 2) for i in range(tick_count)]
            tick_text = [format_hovertext(v) for v in tick_vals]

        layout["xaxis"] = {
            **layout.get("xaxis", {}),
            **axis_config,
            "tickmode": "array",
            "tickvals": tick_vals,
            "ticktext": tick_text,
        }
    else:
        layout["yaxis"] = {**layout.get("yaxis", {}), **axis_config}

    # Use a deep copy of the shared layout so we don't mutate the global
    fig.update_layout(
        **layout,
        xaxis_title=x_title,
        yaxis_title=y_title,
        showlegend=False,
        height=height,
    )

    return fig


def create_distribution_histogram(
    df: pd.DataFrame,
    value_col: str,
    x_title: str,
    y_title: str,
    weights_col: str | None = None,
    nbins: int = 20,
    color: str = "primary",
) -> go.Figure:
    """
    Create a histogram for distribution analysis.

    Args:
        df: DataFrame with data
        value_col: Column with values to bin
        x_title: X-axis title
        y_title: Y-axis title
        weights_col: Optional column for weighted histogram
        nbins: Number of bins
        color: Color key from COLOR_PALETTE

    Returns:
        Plotly Figure object
    """
    histfunc = "sum" if weights_col else "count"

    fig = px.histogram(
        df,
        x=value_col,
        y=weights_col,
        nbins=nbins,
        histfunc=histfunc,
        color_discrete_sequence=[COLOR_PALETTE[color]],
    )

    layout = copy.deepcopy(COMMON_LAYOUT)

    fig.update_layout(
        **layout,
        xaxis_title=x_title,
        yaxis_title=y_title,
        showlegend=False,
    )

    fig.update_traces(
        hovertemplate=f"{x_title}: %{{x}}<br>{y_title}: %{{y}}<extra></extra>",
    )

    return fig


def create_scatter_plot(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    x_title: str,
    y_title: str,
    hover_name_col: str | None = None,
    size_col: str | None = None,
    color: str = "primary",
) -> go.Figure:
    """
    Create a scatter plot for correlation analysis.

    Args:
        df: DataFrame with data
        x_col: Column for x-axis
        y_col: Column for y-axis
        x_title: X-axis title
        y_title: Y-axis title
        hover_name_col: Optional column for hover labels
        size_col: Optional column to size markers
        color: Color key from COLOR_PALETTE

    Returns:
        Plotly Figure object
    """
    fig = px.scatter(
        df,
        x=x_col,
        y=y_col,
        hover_name=hover_name_col,
        size=size_col,
        color_discrete_sequence=[COLOR_PALETTE[color]],
    )

    layout = copy.deepcopy(COMMON_LAYOUT)

    fig.update_layout(
        **layout,
        xaxis_title=x_title,
        yaxis_title=y_title,
        showlegend=False,
    )

    # Customize hover template
    hover_template = f"{x_title}: %{{x:.1f}}<br>{y_title}: %{{y:.1f}}"
    if hover_name_col:
        hover_template = f"<b>%{{hovertext}}</b><br>{hover_template}"
    hover_template += "<extra></extra>"

    fig.update_traces(hovertemplate=hover_template)

    return fig
