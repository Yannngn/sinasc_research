"""
Dashboard components package - Reusable UI and chart components.
"""

from .charts import (
    create_line_chart,
    create_multi_line_chart,
    create_simple_bar_chart,
    create_stacked_bar_chart,
    format_brazilian_number,
)

__all__ = [
    "create_simple_bar_chart",
    "create_line_chart",
    "create_stacked_bar_chart",
    "create_multi_line_chart",
    "format_brazilian_number",
]
