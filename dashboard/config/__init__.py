"""
Configuration module for SINASC Dashboard.
"""

from .constants import *
from .settings import *

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
    "METRIC_NAMES",
    "CHART_TITLES",
]
