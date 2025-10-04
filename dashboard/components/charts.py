"""
Chart generation helper functions - Reusable components for creating common chart types.
"""

import copy

import plotly.graph_objects as go
from config.settings import COLOR_PALETTE, COMMON_LAYOUT, LEGEND_CONFIG


def format_brazilian_number(value: int) -> str:
    """
    Format integer with Brazilian number format (dots as thousands separator).

    Args:
        value: Number to format

    Returns:
        Formatted string (e.g., 1000 -> "1.000")
    """
    return f"{int(value):_}".replace("_", ".")


def create_simple_bar_chart(
    df,
    x_col: str,
    y_col: str,
    x_title: str,
    y_title: str,
    color: str = "primary",
) -> go.Figure:
    """
    Create a simple bar chart with formatted text labels.

    Args:
        df: DataFrame with data
        x_col: Column name for x-axis
        y_col: Column name for y-axis
        x_title: X-axis title
        y_title: Y-axis title
        color: Color key from COLOR_PALETTE
        show_text: Whether to show value labels on bars
        text_inside: Whether to position text inside bars

    Returns:
        Plotly Figure object
    """
    fig = go.Figure()

    text_values = [format_brazilian_number(val) for val in df[y_col]]

    fig.add_trace(
        go.Bar(
            x=df[x_col],
            y=df[y_col],
            text=text_values,
            textposition="inside",
            marker_color=COLOR_PALETTE[color],
            textfont=dict(size=12, color="white"),
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
    x_title: str,
    y_title: str,
    color: str = "primary",
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

    fig.add_trace(
        go.Scatter(
            x=df[x_col],
            y=df[y_col],
            mode="lines+markers",
            line=dict(color=COLOR_PALETTE[color], width=3),
            marker=dict(size=10),
        )
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

    fig.update_layout(
        **layout,
        xaxis_title=x_title,
        yaxis_title=y_title,
        showlegend=False,
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

    return fig


def create_stacked_bar_chart(
    df,
    x_col: str,
    y_cols: list,
    labels: list,
    colors: list,
    x_title: str,
    y_title: str,
    text_size: int = 11,
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
        text_size: Font size for text labels

    Returns:
        Plotly Figure object
    """
    fig = go.Figure()

    # Add bottom stack (larger category)
    fig.add_trace(
        go.Bar(
            x=df[x_col],
            y=df[y_cols[0]],
            name=labels[0],
            marker_color=COLOR_PALETTE[colors[0]],
            text=[format_brazilian_number(val) for val in df[y_cols[0]]],
            textposition="inside",
            textfont=dict(size=text_size, color="white"),
        )
    )

    # Add top stack (smaller category, text outside)
    fig.add_trace(
        go.Bar(
            x=df[x_col],
            y=df[y_cols[1]],
            name=labels[1],
            marker_color=COLOR_PALETTE[colors[1]],
            text=[format_brazilian_number(val) for val in df[y_cols[1]]],
            textposition="outside",
            textfont=dict(size=text_size),
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
        fig.add_trace(
            go.Scatter(
                x=df[x_col],
                y=df[y_col],
                mode="lines+markers",
                name=label,
                line=dict(color=COLOR_PALETTE[color], width=3),
                marker=dict(size=10),
            )
        )

    # Determine y-axis range
    max_value = df[y_cols].max().max()
    y_axis_max = max_value * 1.25  # 25% padding above for outside text

    # Local layout + legend copies
    layout = copy.deepcopy(COMMON_LAYOUT)
    layout["yaxis"] = {**layout.get("yaxis", {}), "range": [0, y_axis_max]}
    if reference_line:
        layout["margin"] = {**layout.get("margin", {}), "r": 125}
    legend = copy.deepcopy(LEGEND_CONFIG)

    fig.update_layout(
        **layout,
        xaxis_title=x_title,
        yaxis_title=y_title,
        legend=legend,
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

    return fig
