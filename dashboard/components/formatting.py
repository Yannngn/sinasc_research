"""
Shared formatting utilities for dashboard pages.
"""

import pandas as pd

from .charts import format_brazilian_number


def format_indicator_value(value: float, indicator: str) -> str:
    """
    Format indicator value with appropriate units and Brazilian formatting.

    Args:
        value: Numeric value to format
        indicator: Indicator name to determine formatting

    Returns:
        Formatted string with units
    """
    # Handle None/NaN values
    if value is None or pd.isna(value):
        return "N/A"

    # Convert to float if it's a string or other type
    try:
        value = float(value)
    except (ValueError, TypeError):
        return "N/A"

    # Handle metric_value with generic formatting
    if indicator == "metric_value":
        if value >= 1000:
            return format_brazilian_number(int(value))
        elif value >= 1:
            return f"{value:.1f}".replace(".", ",")
        else:
            return f"{value:.2f}".replace(".", ",")

    # Percentage indicators
    if "_pct" in indicator or "rate" in indicator.lower():
        return f"{value:.1f}%".replace(".", ",")

    # Count indicators
    if "_count" in indicator or "count" in indicator.lower():
        return format_brazilian_number(int(value))

    # Weight indicators
    if "peso" in indicator.lower() or "weight" in indicator.lower():
        return f"{value:.0f}g"

    # Age indicators
    if "idade" in indicator.lower() or "age" in indicator.lower():
        return f"{value:.1f} anos".replace(".", ",")

    # APGAR indicators
    if "apgar" in indicator.lower():
        return f"{value:.1f}".replace(".", ",")

    # Default: format as number
    return format_brazilian_number(value)


def format_metric_by_type(value: float, metric_type: str, indicator: str = "") -> str:
    """
    Format metric value based on the selected metric type.

    Args:
        value: Numeric value to format
        metric_type: Type of metric ("absolute", "percentage", "per_1k")
        indicator: Original indicator name for fallback formatting

    Returns:
        Formatted string with appropriate units
    """
    # Handle None/NaN values
    if value is None or pd.isna(value):
        return "N/A"

    # Convert to float if it's a string or other type
    try:
        value = float(value)
    except (ValueError, TypeError):
        return "N/A"

    if metric_type == "per_1k":
        return f"{value:.2f}/1k hab.".replace(".", ",")
    elif metric_type == "absolute":
        return format_brazilian_number(int(value))
    elif metric_type == "percentage":
        return f"{value:.1f}%".replace(".", ",")
    else:
        # Fallback to indicator-based formatting
        return format_indicator_value(value, indicator)


def get_metric_suffix(metric_type: str) -> str:
    """
    Get suffix label for metric type.

    Args:
        metric_type: Type of metric ("absolute", "percentage", "per_1k")

    Returns:
        Suffix string with appropriate units
    """
    if metric_type == "per_1k":
        return " (por 1.000 hab.)"
    elif metric_type == "absolute":
        return " (contagem)"
    elif metric_type == "percentage":
        return " (%)"
    return ""


def calculate_metric_column(df: pd.DataFrame, indicator: str, metric_type: str) -> tuple[str, str]:
    """
    Calculate metric column based on type selection and add it to the DataFrame.

    This centralizes the logic for converting indicators between absolute counts,
    percentages, and per-1000 population rates.

    Args:
        df: DataFrame with municipality/state data (must have 'total_births' and 'population' columns)
        indicator: Original indicator column name (e.g., 'cesarean_pct', 'cesarean_count')
        metric_type: Type of metric to calculate ("absolute", "percentage", "per_1k")

    Returns:
        Tuple of (metric_column_name, metric_suffix_label)

    Side Effects:
        May add a 'metric_value' column to the DataFrame
    """
    metric_column = indicator  # Default to the original indicator
    metric_suffix = get_metric_suffix(metric_type)

    if metric_type == "per_1k":
        # Calculate per 1,000 inhabitants
        if indicator.endswith("_pct"):
            count_col = indicator.replace("_pct", "_count")
            if count_col in df.columns:
                df["metric_value"] = (df[count_col] / df["population"] * 1000).fillna(0)
            else:
                # Fallback: calculate from percentage
                df["metric_value"] = ((df[indicator] / 100 * df["total_births"]) / df["population"] * 1000).fillna(0)
        elif indicator.endswith("_count"):
            df["metric_value"] = (df[indicator] / df["population"] * 1000).fillna(0)
        else:
            # For mean indicators, calculate birth rate
            df["metric_value"] = (df["total_births"] / df["population"] * 1000).fillna(0)
        metric_column = "metric_value"

    elif metric_type == "absolute":
        # Use absolute counts
        if indicator.endswith("_pct"):
            count_col = indicator.replace("_pct", "_count")
            if count_col in df.columns:
                df["metric_value"] = df[count_col]
            else:
                # Calculate count from percentage
                df["metric_value"] = (df[indicator] / 100 * df["total_births"]).fillna(0)
            metric_column = "metric_value"
        elif indicator.endswith("_count"):
            metric_column = indicator
        else:
            # For other indicators, show total births
            df["metric_value"] = df["total_births"]
            metric_column = "metric_value"

    elif metric_type == "percentage":
        # Use or calculate percentages
        if not indicator.endswith("_pct"):
            if indicator.endswith("_count"):
                df["metric_value"] = (df[indicator] / df["total_births"] * 100).fillna(0)
                metric_column = "metric_value"
        # else: use indicator as-is

    return metric_column, metric_suffix
