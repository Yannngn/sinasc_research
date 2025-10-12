"""
Dashboard components package - Reusable UI and chart components.
"""

from .cards import create_metric_card, create_year_summary_card
from .charts import (
    create_bar_chart,
    create_distribution_histogram,
    create_line_chart,
    create_multi_line_chart,
    create_ranking_bar_chart,
    create_scatter_plot,
    create_stacked_bar_chart,
    format_brazilian_number,
)
from .formatting import (
    calculate_metric_column,
    format_indicator_value,
    format_metric_by_type,
    get_metric_suffix,
)
from .maps import create_choropleth_map

__all__ = [
    "calculate_metric_column",
    "create_bar_chart",
    "create_choropleth_map",
    "create_distribution_histogram",
    "create_line_chart",
    "create_metric_card",
    "create_multi_line_chart",
    "create_ranking_bar_chart",
    "create_scatter_plot",
    "create_stacked_bar_chart",
    "create_year_summary_card",
    "format_brazilian_number",
    "format_indicator_value",
    "format_metric_by_type",
    "get_metric_suffix",
]
