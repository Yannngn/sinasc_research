# SINASC Research Dashboard

Interactive web dashboard for analyzing Brazilian perinatal health data from SINASC (Sistema de Informações sobre Nascidos Vivos).

## 📊 Overview

This project provides data analysis and visualization of Brazilian birth records covering 5 years (2019-2024) with over 10 million records. The dashboard is built with Plotly Dash for interactive exploration of maternal and child health metrics.

## 🎯 Features

### Current Implementation
- **Multi-Year Overview**: Compare key metrics across 5 years (2019-2024)
- **Annual Analysis**: Detailed monthly breakdowns and distributions for each year
- **Pre-aggregated Data**: Optimized Parquet files for fast loading
- **Brazilian Formatting**: Numbers formatted with Brazilian conventions (dots for thousands, commas for decimals)
- **Interactive Charts**: Birth trends, cesarean rates, preterm births, adolescent pregnancies

### Key Metrics Tracked
- Total births per year/month
- Maternal age distribution
- Birth weight statistics
- APGAR scores
- Cesarean vs. vaginal delivery rates
- Preterm birth rates (including extreme preterm <32 weeks)
- Adolescent pregnancy rates (including very young mothers <15 years)
- Hospital birth percentage

## 🚀 Quick Start

### Prerequisites
- Python 3.12+ (3.13 supported for local development)
- UV package manager (recommended) or pip

### Installation

```bash
# Clone the repository
git clone https://github.com/Yannngn/sinasc_research.git
cd sinasc_research

# Install dependencies with UV
uv sync

# Or with pip
pip install -r requirements.txt
```

### Run the Dashboard

```bash
# Development mode
cd dashboard
python app.py

# Production mode
cd dashboard
gunicorn app:server --bind 0.0.0.0:8050
```

Visit: http://localhost:8050

## 📁 Project Structure

```
sinasc_research/
├── dashboard/              # Dashboard application
│   ├── app.py             # Main entry point
│   ├── pages/             # Dashboard pages
│   │   ├── home.py        # Multi-year overview
│   │   └── annual.py      # Single-year analysis
│   ├── components/        # Reusable UI components
│   ├── data/              # Data loading utilities
│   ├── config/            # Settings and constants
│   └── assets/            # CSS and static files
├── dashboard_data/        # Pre-aggregated data files
│   ├── yearly.parquet     # 5-year summary
│   ├── monthly_*.parquet  # Monthly aggregates
│   └── years/*.parquet    # Detailed annual data
├── data/                  # Raw SINASC data (not in repo)
├── scripts/               # Data processing and deployment scripts
└── docs/                  # Documentation
```

## 📚 Documentation

- **[Dashboard README](dashboard/README.md)**: Detailed dashboard architecture and features
- **[Quick Start Guide](dashboard/QUICKSTART.md)**: Getting started with the dashboard
- **[Structure Guide](dashboard/STRUCTURE.md)**: Dashboard page organization
- **[Design System](dashboard/DESIGN_SYSTEM.md)**: UI/UX design patterns
- **[Architecture](dashboard/ARCHITECTURE.md)**: Technical architecture details
- **[Deployment Guide](docs/DEPLOY_README.md)**: How to deploy to production

## 🌐 Deployment

The dashboard is optimized for free-tier hosting:

- **Data size**: ~200MB total, <13KB for aggregated files
- **Memory usage**: <200MB RAM
- **Recommended**: Render.com (free tier with 512MB RAM)

See [Deployment Guide](docs/DEPLOY_README.md) for detailed instructions.

## 📊 Data Source

- **DATASUS**: Brazilian Ministry of Health
- **Dataset**: SINASC (Sistema de Informações sobre Nascidos Vivos)
- **Coverage**: 2019-2024 (10,036,633 records)
- **Public Domain**: Open data for research and analysis

## 🛠️ Technology Stack

- **Framework**: Plotly Dash 3.2+
- **UI Components**: Dash Bootstrap Components 2.0+
- **Data Processing**: Pandas 2.3+, PyArrow 21.0+
- **Visualization**: Plotly 6.3+
- **Deployment**: Gunicorn 23.0+

## 📄 License

- **Code**: MIT License
- **Data**: Public domain (DATASUS)

## 👤 Author

Yannngn - [GitHub Profile](https://github.com/Yannngn)
