# Scripts & Data Pipeline Guide

This directory contains all scripts for data processing and deployment preparation.

## 🚀 Data Processing Pipeline

The entire data pipeline can be executed with a single command. This script runs all the necessary steps in the correct order.

### How to Run

Process a single year:
```bash
python scripts/run_pipeline.py --year 2024
```

Process a specific list of years:
```bash
python scripts/run_pipeline.py --years 2022 2023 2024
```

Process all available years (2019-2024) and overwrite existing downloads:
```bash
python scripts/run_pipeline.py --all --overwrite
```

### Pipeline Structure

The `run_pipeline.py` orchestrator calls the following scripts located in `scripts/pipeline/` in sequence. The numerical prefixes indicate the execution order.

-   **`01_read_raw_data.py`**: Downloads raw data from the DATASUS source.
-   **`02_clean_data.py`**: Cleans data, handles missing values, and optimizes types.
-   **`03_select_features.py`**: Selects a subset of columns needed for the dashboard.
-   **`04_engineer_features.py`**: Creates new features like age groups and risk categories.
-   **`05_create_dashboard_data.py`**: Generates the final, aggregated data files for the web application.

---

## 📦 Deployment

To prepare the project for deployment (e.g., to Render.com), run the deployment script.

### How to Run

```bash
python scripts/deployment/prepare_deployment.py
```
This script generates all necessary configuration files (`Dockerfile`, `render.yaml`, etc.) in the `deployment/` directory at the project root.

---

## 🔧 Utilities

The `scripts/utils/` directory contains shared Python modules used by other scripts.

-   **`sinasc_definitions.py`**: Contains constants, column mappings, and data dictionaries for the SINASC dataset.