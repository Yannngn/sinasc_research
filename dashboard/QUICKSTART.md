# SINASC Dashboard - Quick Start Guide

## Overview
Interactive web dashboard for analyzing Brazilian perinatal health data (SINASC - Sistema de Informações sobre Nascidos Vivos).

## Features
- 📊 **Overview Dashboard**: Key metrics and monthly timeline
- 📈 **Temporal Analysis**: Time-based trends (in development)
- 🗺️ **Geographic Analysis**: State and municipality maps (in development)
- 🔍 **Detailed Insights**: Deep-dive visualizations (in development)

## Requirements
- Python 3.13+
- Dependencies listed in `pyproject.toml` (parent directory)

## Installation

### Using UV (Recommended)
```bash
# From project root
cd /home/yannn/projects/Yannngn/sinasc-dashboard/sinasc_research
uv sync
```

### Using pip
```bash
# From dashboard directory
cd dashboard
pip install -r requirements.txt
```

## Running the Dashboard

### Development Mode
```bash
# From dashboard directory
cd /home/yannn/projects/Yannngn/sinasc-dashboard/sinasc_research/dashboard
uv run python app.py
```

Or:
```bash
python app.py
```

The dashboard will be available at: **http://localhost:8050**

### Production Mode
```bash
gunicorn app:server -b 0.0.0.0:8050
```

## Project Structure
```
sinasc_research/
├── dashboard/                # Dashboard application
│   ├── app.py               # Main application entry point
│   ├── config/              # Configuration files
│   │   ├── __init__.py
│   │   ├── settings.py     # App settings and colors
│   │   └── constants.py    # Brazilian states, labels
│   ├── data/                # Data loading
│   │   ├── __init__.py
│   │   └── loader.py       # DataLoader with caching
│   ├── pages/               # Dashboard pages
│   │   ├── __init__.py
│   │   └── home.py         # Home page with metrics
│   └── requirements.txt     # Python dependencies
└── dashboard_data/          # Optimized data files
    ├── metadata.json
    ├── aggregates/
    │   ├── monthly_2024.parquet
    │   ├── state_2024.parquet
    │   └── municipality_2024.parquet
    └── years/
        └── 2024_essential.parquet
```

## Data Files
The dashboard uses pre-optimized data files located in `sinasc_research/dashboard_data/`:

### Aggregated Data (5 Years: 2019-2024)
- **yearly.parquet**: 12.5KB, 5 rows, 23 columns
  - Includes: total_births, preterm_birth_pct, extreme_preterm_birth_pct, adolescent_pregnancy_pct, very_young_pregnancy_pct, cesarean_pct, PESO_mean, IDADEMAE_mean, APGAR5_mean, hospital_birth_pct, etc.
- **Monthly aggregates**: monthly_{year}.parquet (10KB each, 12 months per year)
- **State aggregates**: state_{year}.parquet (11KB each, 27 states)
- **Municipality aggregates**: municipality_{year}.parquet (30KB each, top 500)

### Essential Data
- **2019_essential.parquet**: ~32MB, 2.73M records
- **2020_essential.parquet**: ~32MB, 2.68M records
- **2021_essential.parquet**: ~32MB, 2.68M records
- **2022_essential.parquet**: ~30MB, 2.56M records
- **2023_essential.parquet**: ~30MB, 2.54M records
- **2024_essential.parquet**: ~30MB, 2.26M records
- **Total**: 10,036,633 records across 5 years

### Metadata
- **metadata.json**: 2KB with dataset information

To regenerate these files:
```bash
# From project root
cd /home/yannn/projects/Yannngn/sinasc-dashboard/sinasc_research

# Generate for all years
python scripts/create_dashboard_data.py --year 2019
python scripts/create_dashboard_data.py --year 2020
python scripts/create_dashboard_data.py --year 2021
python scripts/create_dashboard_data.py --year 2022
python scripts/create_dashboard_data.py --year 2023
python scripts/create_dashboard_data.py --year 2024
```

## Environment Variables
Create a `.env` file in the dashboard directory:
```
DEBUG=True
HOST=0.0.0.0
PORT=8050
```

## Current Status
✅ **Completed**:
- Base application structure with routing
- Configuration management (settings, constants, centralized layout configs)
- Brazilian number formatting (dots for thousands, commas for decimals)
- Data loading with LRU caching (5 years: 2019-2024)
- Home page with enhanced features:
  - **Year Summary Cards** (last 3 years):
    - Total births with Brazilian formatting
    - 6 metrics in compact 2-column inline layout
    - Maternal age, birth weight, APGAR 5, cesarean rate, preterm rate, hospital rate
  - **Birth Evolution**: Bar chart with formatted text labels
  - **Cesarean Comparison**: Grouped bar chart
  - **Preterm Births Analysis**: 
    - Stacked bar chart (moderate + extreme <32 weeks)
    - Dual-line chart with WHO reference
  - **Adolescent Pregnancy Analysis**:
    - Stacked bar chart (older teens + very young <15 years)
    - Dual-line chart showing trends
  - All charts with optimized layouts (no redundant titles)
- Annual analysis page with monthly details

🔄 **In Development**:
- Temporal analysis page with date range filters
- Geographic analysis page (choropleth maps by state)
- Insights page with correlations and predictions
- Additional interactivity and cross-filtering

## Performance
- **Memory usage**: <200MB (target: <512MB for free hosting)
- **Load time**: <3 seconds for initial page
- **Chart updates**: <1 second with caching

## Technology Stack
- **Framework**: Plotly Dash 3.2+
- **UI**: Dash Bootstrap Components 2.0+
- **Data**: Pandas 2.3+, PyArrow 21.0+
- **Visualization**: Plotly 6.3+
- **Deployment**: Gunicorn 21.2+

## Deployment
Ready for deployment on:
- Render.com (free tier)
- Hugging Face Spaces
- Heroku
- Any platform supporting Python WSGI apps

## License
MIT

## Author
Yannngn
