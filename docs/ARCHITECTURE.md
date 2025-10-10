# Technical Architecture: SINASC Dashboard

## 1. System Overview

The SINASC Dashboard has evolved from a file-based system to a robust, database-driven web application. This architecture is designed for scalability, maintainability, and efficient data processing, supporting both local development and cloud deployment.

The core of the system is a three-tiered database environment coupled with a Python-based ETL (Extract, Transform, Load) pipeline.

---

## 2. Architecture Diagram

```
                                     ┌──────────────────────────────┐
                                     │    Cloud Production Env.     │
                                     │        (e.g., Render)        │
                                     └──────────────┬───────────────┘
                                                    │
                                     ┌──────────────▼──────────────┐
                                     │  Cloud Production Database  │
                                     │ (PostgreSQL + PostGIS)      │
                                     │ ┌─────────────────────────┐ │
                                     │ │   fact_births           │ │
                                     │ │   dim_* tables          │ │
                                     │ │   agg_* tables          │ │
                                     │ └─────────────────────────┘ │
                                     └──────────────▲──────────────┘
                                                    │
                                          (4) Promote │
                                                    │
┌──────────────────────────────┐     ┌──────────────┴──────────────┐     ┌──────────────────────────────┐
│      Local Development       │     │   Local Production Database │     │      Staging Environment     │
│                              │     │     (Docker - Port 5434)    │     │      (Docker - Port 5433)    │
└──────────────┬───────────────┘     └──────────────▲──────────────┘     └──────────────┬───────────────┘
               │                                    │                                   │
┌──────────────▼──────────────┐     ┌──────────────┴──────────────┐     ┌──────────────▼──────────────┐
│      Dash Application        │     │   fact_births, dim_*, agg_* │     │      raw_*, opt_* tables     │
│ (Python, Plotly, Gunicorn)   │     └─────────────────────────────┘     └──────────────▲──────────────┘
└──────────────▲───────────────┘                                                       │
               │                                                              (1, 2, 3)│ ETL Scripts
               │                                                                       │
┌──────────────┴──────────────┐     ┌─────────────────────────────┐     ┌──────────────▼──────────────┐
│       Data Loader            │     │      promote.py             │     │      staging.py              │
│ (Connects to Local/Cloud DB) │     │      (Promotes to Prod)     │     │      optimize.py             │
└──────────────────────────────┘     └─────────────────────────────┘     │      dimensions.py           │
                                                                         └─────────────────────────────┘
```

---

## 3. The Three-Tiered Database Environment

This architecture separates data processing from data serving, ensuring stability and performance.

### Tier 1: Staging Database (`sinasc_db_staging`)

-   **Purpose**: The primary environment for data ingestion and transformation. All raw, messy, and intermediate data lives here.
-   **Technology**: PostgreSQL + PostGIS, running in a local Docker container.
-   **Tables**:
    -   `raw_*`: Contain data exactly as ingested from source APIs (e.g., `raw_sinasc_2024`, `raw_ibge_population`).
    -   `opt_*`: Optimized versions of the raw tables, with corrected data types (e.g., `TEXT` to `INTEGER`, `DATE`), but still in a normalized form.
-   **Key Processes**: The `staging.py` and `optimize.py` scripts run exclusively against this database.

### Tier 2: Local Production Database (`sinasc_db_prod_local`)

-   **Purpose**: A local, clean, production-ready database for development and testing of the dashboard. It is a direct mirror of the cloud production database.
-   **Technology**: PostgreSQL + PostGIS, running in a separate local Docker container.
-   **Tables**:
    -   `fact_births`: The central fact table containing all birth records, optimized and ready for querying.
    -   `dim_*`: Dimension tables that provide descriptive labels for categorical codes (e.g., `dim_parto` maps `'1'` to `'Vaginal'`).
    -   `agg_*`: (Future) Pre-aggregated summary tables to speed up common queries.
-   **Key Processes**: The `promote.py` script populates this database from the staging DB. The local Dash application runs against this database.

### Tier 3: Cloud Production Database (`PROD_RENDER_DATABASE_URL`)

-   **Purpose**: The live database serving the deployed application on a cloud host like Render.
-   **Technology**: Managed PostgreSQL + PostGIS service.
-   **Tables**: Identical schema to the Local Production Database.
-   **Key Processes**: The `promote.py` script, when run with the `--target render` flag, populates this database. The deployed Dash application connects to this database.

---

## 4. The ETL Data Pipeline

The data pipeline is orchestrated by a series of Python scripts located in `dashboard/data/`.

### Step 1: Ingestion (`staging.py`)

-   **Responsibility**: Extracts data from various public sources and loads it into the staging database.
-   **Sources**:
    -   SINASC FTP server (birth records).
    -   IBGE SIDRA API (population data).
    -   IBGE GeoJSON files (municipality/state boundaries).
    -   CNES FTP server (health facility data).
-   **Key Features**:
    -   **Chunking**: Reads large CSV/DBF files in chunks to handle multi-gigabyte files without running out of memory.
    -   **PostGIS Integration**: Converts GeoJSON geometry into WKT (Well-Known Text) format for efficient storage and querying using `GeoAlchemy2`.
    -   **Idempotent**: Includes an `--overwrite` flag to allow re-running the ingestion process.

### Step 2: Optimization (`optimize.py`)

-   **Responsibility**: Cleans and optimizes the raw tables created by the staging script.
-   **Process**:
    1.  Reads a `raw_*` table from the staging database.
    2.  Applies a predefined schema to cast columns to efficient data types (e.g., `TEXT` -> `SMALLINT`, `VARCHAR(8)` -> `DATE`).
    3.  Saves the result as a new `opt_*` table.
    4.  Optionally (`--overwrite`), it can replace the `raw_*` table with the optimized one to save disk space.
-   **Key Features**:
    -   **Schema-Driven**: Uses a `SINASC_OPTIMIZATION_SCHEMA` dictionary to define type mappings.
    -   **Efficient Transactions**: Uses temporary tables and atomic `RENAME` operations for safe, in-place overwrites.

### Step 3: Dimension Creation (`dimensions.py`)

-   **Responsibility**: Creates and populates the dimension tables (`dim_*`) in the staging database.
-   **Process**: Reads from a `SINASC_MAPPINGS` dictionary which contains the code-to-label mappings for variables like `PARTO` (delivery type), `ESCMAE` (maternal education), etc.
-   **Output**: Tables like `dim_parto`, `dim_escmae`, `dim_racacor` that can be joined with the fact table to display human-readable names in the dashboard.

### Step 4: Promotion (`promote.py`)

-   **Responsibility**: The final step of the ETL process. It promotes the clean data from the staging environment to a production environment.
-   **Process**:
    1.  Connects to both the staging and a target production database (local or cloud).
    2.  Copies all `opt_*` tables (renaming them to `fact_*`) and all `dim_*` tables to the production database.
-   **Key Features**:
    -   **Targeted Promotion**: Can target the local production DB (`--target local`) or the cloud production DB (`--target render`).
    -   **Decoupling**: This step ensures that the production database only ever receives clean, validated data and is completely isolated from the messy ETL process.

---

## 5. Dashboard Application

### Backend (Dash/Flask)

-   **`app.py`**: The main entry point for the Dash application.
-   **`data/loader.py`**: Contains the `DataLoader` class, which is now responsible for connecting to the production database (determined by an environment variable) and fetching data. All file-based reading logic has been replaced with SQL queries via SQLAlchemy.
-   **Callbacks**: The dashboard's interactive callbacks trigger SQL queries against the production database. Joins with `dim_*` tables are used to display descriptive labels.

### Frontend

-   **Technology**: Plotly, Dash Bootstrap Components.
-   **Rendering**: The frontend is rendered server-side by Dash. User interactions trigger callbacks that re-render components with new data from the backend.

---

## 6. Local Development Environment

-   **`docker-compose.yml`**: Defines the two PostgreSQL services (`db_staging`, `db_prod_local`).
    -   Uses the official `postgis/postgis` image.
    -   Maps different host ports (5433, 5434) to the standard container port (5432).
    -   Mounts an `init-scripts` directory to automatically run a shell script that enables the `postgis` extension on database creation.
    -   Uses named volumes (`staging_data`, `prod_local_data`) to persist data between container restarts.
-   **`.env` file**: Stores the connection URLs for all three database tiers, allowing for easy switching between environments.

---

*Last Updated: October 2025*
