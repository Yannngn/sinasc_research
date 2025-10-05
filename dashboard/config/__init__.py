"""
Configuration module for SINASC Dashboard.
"""

from .constants import BRAZILIAN_STATES, CATEGORY_LABELS, CHART_TITLES, METRIC_NAMES, MONTH_NAMES
from .settings import (
    BASE_DIR,
    CHART_CONFIG,
    CHART_HEIGHT,
    COLOR_PALETTE,
    DATA_DIR,
    DEBUG,
    HOST,
    PORT,
)

__all__ = [
    # Settings
    "BASE_DIR",
    "DATA_DIR",
    "DEBUG",
    "HOST",
    "PORT",
    "COLOR_PALETTE",
    "CHART_CONFIG",
    "CHART_HEIGHT",
    # Constants
    "BRAZILIAN_STATES",
    "CATEGORY_LABELS",
    "CHART_TITLES",
    "METRIC_NAMES",
    "MONTH_NAMES",
]
