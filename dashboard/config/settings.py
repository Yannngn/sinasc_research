"""
Configuration settings for SINASC Dashboard.
"""

import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent.parent  # dashboard/
DATA_DIR = BASE_DIR.parent / "dashboard_data"  # sinasc_research/dashboard_data/

# Data paths
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

# Modern Color Palette (Healthcare Analytics Design System)
COLOR_PALETTE = {
    "primary": "#2196f3",  # Blue - Main brand color
    "primary_dark": "#1976d2",  # Darker blue for emphasis
    "primary_light": "#64b5f6",  # Lighter blue for backgrounds
    "secondary": "#ff9800",  # Orange - Secondary actions
    "success": "#4caf50",  # Green - Positive indicators
    "success_light": "#81c784",  # Light green
    "danger": "#f44336",  # Red - Alerts and critical values
    "danger_light": "#e57373",  # Light red
    "warning": "#ff9800",  # Orange - Warnings
    "warning_dark": "#f57c00",  # Dark orange
    "info": "#00bcd4",  # Cyan - Informational
    "info_dark": "#0097a7",  # Dark cyan
    "neutral": "#9e9e9e",  # Gray - Neutral elements
    "gray_light": "#f5f5f5",  # Very light gray for backgrounds
    "gray_dark": "#616161",  # Dark gray for text
}

COLOR_CONTINUOS_PALLETTE = {
    "primary": "Viridis",
    "secondary": "YlOrRd",
    "success": "Greens",
    "danger": "Reds",
    "warning": "Oranges",
    "info": "Blues",
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

# Common chart layout settings (Modern Design System)
COMMON_LAYOUT = {
    "template": TEMPLATE,
    "xaxis": dict(
        tickmode="linear",
        dtick=1,
        showgrid=False,
        showline=True,
        linewidth=2,
        linecolor="#e0e0e0",
    ),
    "yaxis": dict(
        showgrid=True,
        gridwidth=1,
        gridcolor="#f5f5f5",
        showline=False,
    ),
    "font": dict(
        family="Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
        size=13,
        color="#424242",
    ),
    "hovermode": "x unified",
    "hoverlabel": dict(
        bgcolor="white",
        font_size=13,
        font_family="Inter, sans-serif",
        bordercolor="#e0e0e0",
    ),
    "plot_bgcolor": "white",
    "paper_bgcolor": "white",
    "margin": dict(l=60, r=40, t=60, b=60),
}

# Bar chart text settings
BAR_TEXT_CONFIG = {
    "texttemplate": "%{text:,.0f}".replace(",", "."),  # Brazilian format with dots
    "textfont": dict(size=12, color="white", family="Inter"),
}

# Legend settings (Modern positioning)
LEGEND_CONFIG = {
    "orientation": "h",
    "y": -0.25,
    "xanchor": "center",
    "x": 0.5,
    "bgcolor": "rgba(255, 255, 255, 0.8)",
    "bordercolor": "#e0e0e0",
    "borderwidth": 1,
    "font": dict(size=12),
}
