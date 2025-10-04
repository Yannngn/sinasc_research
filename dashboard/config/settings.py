"""
Configuration settings for SINASC Dashboard.
"""

import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent.parent  # dashboard/
DATA_DIR = BASE_DIR.parent / "dashboard_data"  # sinasc_research/dashboard_data/

# Data paths
METADATA_PATH = DATA_DIR / "metadata.json"
AGGREGATES_DIR = DATA_DIR / "aggregates"
YEARS_DIR = DATA_DIR / "years"

# App settings
DEBUG = os.getenv("DEBUG", "True") == "True"
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8050))

# Data settings
MAX_RECORDS_DISPLAY = int(os.getenv("MAX_RECORDS_DISPLAY", 10000))
CACHE_SIZE = int(os.getenv("CACHE_SIZE", 2))  # Number of years to cache

# Visualization defaults
DEFAULT_THEME = "plotly_white"
CHART_HEIGHT = 400
MAP_HEIGHT = 600

TEMPLATE = "plotly_white"

# Color palette (healthcare theme)
COLOR_PALETTE = {
    "primary": "#1f77b4",  # Blue
    "secondary": "#ff7f0e",  # Orange
    "success": "#2ca02c",  # Green
    "danger": "#d62728",  # Red
    "warning": "#ffbb00",  # Yellow
    "info": "#17becf",  # Cyan
    "neutral": "#7f7f7f",  # Gray
}

# Delivery type colors
DELIVERY_COLORS = {
    "Vaginal": COLOR_PALETTE["primary"],
    "Cesarean": COLOR_PALETTE["secondary"],
}

# Chart configuration
CHART_CONFIG = {
    "displayModeBar": False,
    "responsive": True,
}

# Number formatting (Brazilian format)
NUMBER_FORMAT = {
    "thousands_sep": ".",
    "decimal_sep": ",",
}

# Common chart layout settings
COMMON_LAYOUT = {
    "template": TEMPLATE,
    "xaxis": dict(tickmode="linear", dtick=1),
    "font": dict(family="Arial, sans-serif"),
    "hovermode": "x unified",
}

# Bar chart text settings
BAR_TEXT_CONFIG = {
    "texttemplate": "%{text:,.0f}".replace(",", "."),  # Brazilian format with dots
    "textfont": dict(size=12, color="white"),
}

# Legend settings
LEGEND_CONFIG = {
    "orientation": "h",
    "yanchor": "bottom",
    "y": 1.02,
    "xanchor": "right",
    "x": 1,
}
