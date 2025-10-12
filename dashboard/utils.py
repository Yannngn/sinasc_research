"""
Utility functions for data formatting and display across the dashboard.

This module centralizes formatting logic to ensure consistency and reusability.
"""

import pandas as pd


def format_brazilian_number(value: float | int) -> str:
    """
    Format number using Brazilian conventions (dots as thousands separator).

    Args:
        value: Numeric value to format

    Returns:
        Formatted string with Brazilian number format
    """
    if pd.isna(value):
        return "N/A"
    return f"{int(value):,}".replace(",", ".")


def format_indicator_value(value: float, metric: str) -> str:
    """
    Format indicator value with appropriate units and Brazilian formatting.

    Args:
        value: Numeric value to format
        metric: The metric type ('absolute', 'percentage', 'per_1k') to determine formatting.

    Returns:
        Formatted string with units.
    """
    if pd.isna(value):
        return "N/A"

    if metric == "percentage":
        return f"{value:.1f}%".replace(".", ",")
    if metric == "per_1k":
        return f"{value:.2f}".replace(".", ",")  # e.g., 12,34 per 1k
    # Default to absolute number formatting
    return format_brazilian_number(value)


def format_percentage(value: float, decimals: int = 1) -> str:
    """
    Format percentage value with Brazilian decimal separator.

    Args:
        value: Percentage value (0-100)
        decimals: Number of decimal places

    Returns:
        Formatted percentage string
    """
    if pd.isna(value):
        return "N/A"
    return f"{value:.{decimals}f}%".replace(".", ",")


def format_value_with_unit(value: float, unit: str, decimals: int = 1) -> str:
    """
    Format numeric value with a unit suffix.

    Args:
        value: Numeric value to format
        unit: Unit suffix (e.g., "anos", "g", "kg")
        decimals: Number of decimal places

    Returns:
        Formatted string with unit
    """
    if pd.isna(value):
        return "N/A"
    formatted = f"{value:.{decimals}f}".replace(".", ",")
    return f"{formatted} {unit}"
