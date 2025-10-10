# SINASC Research Dashboard

Interactive web dashboard for analyzing Brazilian perinatal health data from SINASC (Sistema de Informações sobre Nascidos Vivos), powered by a robust PostgreSQL backend and a full ETL pipeline.

## 📊 Overview

This project provides a comprehensive platform for analyzing Brazilian birth records. It features a complete ETL (Extract, Transform, Load) pipeline that processes raw data from public sources, stores it in a PostgreSQL database, and serves it to a Plotly Dash dashboard for interactive exploration.

The architecture supports both local development with Docker and cloud deployment on platforms like Render.

## 🎯 Features

### Current Implementation
- **ETL Pipeline**: Automated scripts for data ingestion, type optimization, and dimension table creation.
- **PostgreSQL Backend**: Scalable and robust data storage using PostgreSQL with PostGIS for geospatial analysis.
- **Staging & Production Environments**: Dual database setup (staging for processing, production for serving) manageable via Docker.
- **Multi-Year Analysis**: Compare key metrics across multiple years.
- **Geographic Analysis**: Interactive maps and regional data exploration.
- **Interactive Charts**: Explore trends in cesarean rates, preterm births, maternal age, and more.

### Key Metrics Tracked
- Total births by year, month, state, and municipality.
- Maternal age distribution.
- Birth weight statistics and low-weight births.
- APGAR scores.
- Cesarean vs. vaginal delivery rates.
- Preterm birth rates.
- Adolescent pregnancy rates.
- Geographic distribution of births.

## 🚀 Quick Start

### Prerequisites
- **Docker** and **Docker Compose**
- Python 3.12+
- UV package manager (recommended) or pip

### Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Yannngn/sinasc_research.git
    cd sinasc_research
    ```

2.  **Set up environment variables:**
    Create a `.env` file by copying the example file:
    ```bash
    cp .env.example .env
    ```
    *No changes are needed in `.env` for the default local setup.*

3.  **Install Python dependencies:**
    ```bash
    uv sync
    ```

4.  **Launch the databases:**
    This command starts the staging and local production PostgreSQL databases in Docker.
    ```bash
    docker-compose up -d
    ```

### Run the Full Pipeline & Dashboard

1.  **Run the ETL pipeline:**
    This script will ingest, optimize, and promote the data to your local databases.
    ```bash
    python -m dashboard.data.run_all
    ```

2.  **Run the Dashboard:**
    ```bash
    python -m dashboard.app
    ```

Visit: http://localhost:8050

## 📁 Project Structure

```
sinasc_research/
├── dashboard/              # Dashboard application
│   ├── app.py             # Main entry point
│   ├── data/              # Data pipeline scripts (ETL)
│   │   ├── staging.py     # Ingests raw data
│   │   ├── optimize.py    # Optimizes data types
│   │   ├── dimensions.py  # Creates dimension tables
│   │   ├── promote.py     # Promotes data to production
│   │   └── run_all.py     # Orchestrates the pipeline
│   ├── pages/             # Dashboard pages
│   └── components/        # Reusable UI components
├── deployment/             # Deployment configurations (Dockerfile, render.yaml)
├── docs/                   # Project documentation
├── data/                   # Raw data source (not in repo)
└── docker-compose.yml      # Defines local database services
```

## 📚 Documentation

- **[Quick Start Guide](docs/QUICKSTART.md)**: Detailed setup and development guide.
- **[Architecture](docs/ARCHITECTURE.md)**: In-depth explanation of the three-tiered database architecture.
- **[Deployment Guide](docs/DEPLOYMENT_GUIDE.md)**: How to deploy the application and database to Render.
- **[Data Pipeline](docs/PIPELINE.md)**: Details on the ETL process.

## 🌐 Deployment

The application is designed for cloud deployment on services like Render. The architecture includes separate staging and production databases, which can be mapped to local Docker containers or cloud-hosted PostgreSQL instances.

See the **[Deployment Guide](docs/DEPLOYMENT_GUIDE.md)** for detailed instructions.

## 📊 Data Source

- **DATASUS**: Brazilian Ministry of Health (SINASC, CNES)
- **IBGE**: Brazilian Institute of Geography and Statistics (Population, Geospatial Data)
- **Public Domain**: All data is open for research and analysis.

## 🛠️ Technology Stack

- **Backend**: Python, PostgreSQL, PostGIS
- **Framework**: Plotly Dash
- **Data Processing**: Pandas, SQLAlchemy, GeoAlchemy2
- **Environment**: Docker, Docker Compose
- **UI**: Dash Bootstrap Components
- **Deployment**: Gunicorn

## 📄 License

- **Code**: MIT License
- **Data**: Public domain (DATASUS, IBGE)

## 👤 Author

Yannngn - [GitHub Profile](https://github.com/Yannngn)
