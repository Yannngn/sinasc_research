# Quick Start Guide: SINASC Dashboard

This guide provides detailed instructions for setting up and running the SINASC dashboard and its associated data pipeline on a local machine.

## 1. Architecture Overview

The project uses a three-tiered database architecture, managed locally with Docker:

1.  **Staging Database (`sinasc_db_staging`)**: A PostgreSQL database running in a Docker container. It's used for ingesting and processing raw data from public sources.
2.  **Local Production Database (`sinasc_db_prod_local`)**: A second PostgreSQL database in Docker that mirrors the structure of the cloud production database. It holds the clean, aggregated data ready to be served to the dashboard.
3.  **Cloud Production Database**: A managed PostgreSQL instance on a cloud provider (e.g., Render) for the deployed application.

This setup allows for safe data processing in a staging environment without affecting the production data that the dashboard consumes.

## 2. Prerequisites

Before you begin, ensure you have the following installed:

-   **Docker**: To run the PostgreSQL database containers.
-   **Docker Compose**: To manage the multi-container Docker application.
-   **Python**: Version 3.12 or higher.
-   **UV**: The recommended Python package manager for this project.

## 3. Local Setup and Installation

Follow these steps to get the project running locally.

### Step 1: Clone the Repository

```bash
git clone https://github.com/Yannngn/sinasc_research.git
cd sinasc_research
```

### Step 2: Configure Environment Variables

The project uses a `.env` file to manage database connection strings and other settings.

1.  **Create the `.env` file:**
    Copy the example file to create your local configuration.
    ```bash
    cp .env.example .env
    ```

2.  **Review the variables:**
    The default values in `.env` are pre-configured for the local Docker setup. You don't need to change anything to run the project locally.

    -   `STAGING_DATABASE_URL`: Connects to the staging database in Docker.
    -   `PROD_LOCAL_DATABASE_URL`: Connects to the local production database in Docker.
    -   `PROD_RENDER_DATABASE_URL`: Placeholder for your cloud database URL (used for deployment).

### Step 3: Install Python Dependencies

Use `uv` to install all required Python packages from `pyproject.toml`.

```bash
uv sync
```

### Step 4: Launch the Databases

Start the staging and local production PostgreSQL databases using Docker Compose. The `-d` flag runs the containers in detached mode.

```bash
docker-compose up -d
```

-   The first time you run this, Docker will download the `postgis/postgis` image.
-   An initialization script will automatically enable the PostGIS extension in both databases.
-   Your databases will be running on:
    -   Staging: `localhost:5433`
    -   Local Production: `localhost:5434`

## 4. Running the Data Pipeline

The data pipeline consists of three main stages: ingestion, transformation, and promotion. Each stage can be run independently or as part of a complete workflow.

### Complete Pipeline Workflow

**Step 1: Ingest raw data from APIs**
```bash
python dashboard/data/staging.py
```
This downloads raw SINASC data and ingests it into the `sinasc_db_staging` database.

**Step 2: Run SQL-based transformation pipeline**
```bash
python dashboard/data/pipeline/run_all.py
```
This executes 5 SQL-based transformation steps:
1.  **Select**: Extracts essential columns from raw tables
2.  **Create**: Builds unified `fact_births` table from all years
3.  **Bin**: Creates dimension tables (`dim_*`) for categorical data
4.  **Engineer**: Adds computed features (e.g., `is_preterm`, `is_cesarean`)
5.  **Aggregate**: Generates pre-computed summary tables (`agg_*`)

**Step 3: Promote to production**
```bash
python dashboard/data/promote.py --target local
```
This copies the transformed tables (`dim_*`, `agg_*`) from staging to the `sinasc_db_prod_local` database.

### Pipeline Details
- **Memory Efficient**: All transformations use SQL, keeping Python memory usage <200MB
- **Incremental**: Can add new years without reprocessing everything
- **Fast**: SQL operations are optimized for large datasets (10M+ rows)
- See `dashboard/data/pipeline/README.md` for detailed documentation

## 5. Running the Dashboard

Once the pipeline has successfully populated the local production database, you can launch the web application.

```bash
python dashboard/app.py
```

The dashboard will:
- Connect to your `sinasc_db_prod_local` database
- Load pre-aggregated data from `agg_*` tables
- Query dimension tables (`dim_*`) for labels and lookups

Navigate to **http://localhost:8050** in your web browser to see the application.

## 6. Development Workflow Summary

Your typical development workflow will be:

1.  **Start services**: `docker-compose up -d`
2.  **Process data** (only needs to be run once, or when adding new data):
    ```bash
    python dashboard/data/staging.py
    python dashboard/data/pipeline/run_all.py
    python dashboard/data/promote.py --target local
    ```
3.  **Run the app**: `python dashboard/app.py`
4.  **Code**: Make changes to the dashboard pages, components, or data loader. The web app will hot-reload.

### Adding New Data

To add new SINASC data (e.g., for 2025):
```bash
# Ingest new year
python dashboard/data/staging.py --years 2025

# Re-run pipeline (handles new data incrementally)
python dashboard/data/pipeline/run_all.py

# Promote to production
python dashboard/data/promote.py --target local
```

## 7. Stopping the Environment

To stop the Docker database containers, run:

```bash
docker-compose down
```

This will stop the containers but preserve the data in the Docker volumes, so you won't have to re-run the pipeline every time you restart them. To delete the data as well, use `docker-compose down -v`.
