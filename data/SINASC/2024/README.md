# SINASC 2024 Data

## Overview

Raw and processed SINASC (Sistema de Informações sobre Nascidos Vivos) data for the year 2024.

## Files

- **Raw data**: Original files from DATASUS (not included in repository)
- **Processed data**: Cleaned and enriched `.parquet` files

## Data Source

- **Source**: DATASUS (Brazilian Ministry of Health)
- **Dataset**: SINASC - Live Birth Information System
- **Year**: 2024
- **License**: Public domain (open data for research)

## Processing

Data is processed through:
1. Cleaning and standardization
2. Feature engineering
3. Optimization for dashboard use

See `scripts/` directory for processing scripts.

## Usage

For dashboard deployment, use pre-aggregated files in `dashboard_data/` instead of loading raw data.

## More Information

- [Dashboard Data README](../../../dashboard_data/README.md) - Optimized dashboard files
- [Data Inventory](../../DATA_INVENTORY.md) - Complete data catalog
