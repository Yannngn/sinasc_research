# Dashboard Data - Optimized SINASC Files

**Generated:** October 3, 2025  
**Purpose:** Lightweight, pre-aggregated data files for SINASC Dashboard deployment

---

## 📦 Package Overview

This directory contains optimized data files for the SINASC web dashboard, designed to:
- Minimize memory usage (<512MB RAM requirement)
- Enable fast loading (<3 seconds initial load)
- Support multi-year analysis
- Fit within free hosting tier limits

**Total Size:** ~30 MB (per year)  
**Memory Usage:** <200 MB when loaded  
**Load Time:** <2 seconds on free tier hosting

---

## 📂 Directory Structure

```
dashboard_data/
├── metadata.json                    # Dataset metadata and summaries
├── aggregates/                      # Pre-computed aggregates
│   ├── monthly_2024.parquet        # Monthly statistics (8.6 KB)
│   ├── state_2024.parquet          # State-level statistics (11 KB)
│   ├── municipality_2024.parquet   # Top 500 municipalities (30 KB)
│   └── combined_yearly.parquet     # Multi-year comparison (12 KB)
└── years/                           # Year-specific data
    └── 2024_essential.parquet      # Essential columns (30 MB)
```

---

## 📊 Data Files

### 1. Essential Columns (`years/{year}_essential.parquet`)

**Size:** ~30 MB per year  
**Records:** 2,260,034 (2024)  
**Columns:** 29 (reduced from 51)

**Included Columns:**
- **Temporal:** `DTNASC`, `HORANASC`
- **Geographic:** `CODMUNNASC`, `CODMUNRES`
- **Demographics:** `IDADEMAE`, `IDADEPAI`, `ESTCIVMAE`, `ESCMAE`, `RACACOR`, `RACACORMAE`, `SEXO`
- **Prenatal Care:** `CONSULTAS`, `CONSPRENAT`, `MESPRENAT`, `KOTELCHUCK`
- **Pregnancy:** `GRAVIDEZ`, `QTDGESTANT`, `GESTACAO`, `SEMAGESTAC`
- **Delivery:** `LOCNASC`, `CODESTAB`, `PARTO`, `TPROBSON`
- **Newborn Health:** `PESO`, `APGAR1`, `APGAR5`
- **Engineered:** `IDADEMAEBIN`, `PESOBIN`, `DESLOCNASCBOOL`

**Use Case:** Detailed visualizations and filtering

**Load Example:**
```python
import pandas as pd

# Load essential data for a specific year
df = pd.read_parquet('dashboard_data/years/2024_essential.parquet')

# Or with column selection for even lower memory
df = pd.read_parquet(
    'dashboard_data/years/2024_essential.parquet',
    columns=['DTNASC', 'IDADEMAE', 'PESO', 'PARTO']
)
```

---

### 2. Monthly Aggregates (`aggregates/monthly_{year}.parquet`)

**Size:** ~10 KB per year  
**Records:** 12 (one per month)  
**Metrics:**
- `total_births`: Birth count
- `PESO_mean`, `PESO_median`, `PESO_std`: Birth weight statistics
- `IDADEMAE_mean`, `IDADEMAE_median`: Maternal age
- `APGAR1_mean`, `APGAR5_mean`: APGAR scores
- `cesarean_rate_pct`: Cesarean delivery rate
- `multiple_pregnancy_pct`: Multiple pregnancy rate
- `hospital_birth_pct`: Hospital birth rate

**Use Case:** Timeline visualizations, trend analysis

**Load Example:**
```python
# Load monthly aggregates
monthly = pd.read_parquet('dashboard_data/aggregates/monthly_2024.parquet')

# Create time series chart
import plotly.express as px
fig = px.line(monthly, x='year_month', y='total_births', 
              title='Births per Month - 2024')
```

---

### 3. State Aggregates (`aggregates/state_{year}.parquet`)

**Size:** ~11 KB per year  
**Records:** 27 (Brazilian states)  
**Metrics:**
- `total_births`: Birth count per state
- `PESO_mean`, `PESO_median`, `PESO_std`: Birth weight by state
- `IDADEMAE_mean`, `IDADEMAE_median`: Maternal age by state
- `APGAR1_mean`, `APGAR5_mean`: APGAR scores by state
- `cesarean_rate_pct`: Cesarean rate by state
- `multiple_pregnancy_pct`: Multiple pregnancy rate
- `hospital_birth_pct`: Hospital birth rate
- `preterm_rate_pct`: Preterm birth rate

**Use Case:** Choropleth maps, regional comparisons

**Load Example:**
```python
# Load state aggregates
states = pd.read_parquet('dashboard_data/aggregates/state_2024.parquet')

# Create choropleth map
import plotly.express as px
fig = px.choropleth(
    states,
    geojson=brazil_geojson,
    locations='state_code',
    color='cesarean_rate_pct',
    title='Cesarean Rate by State'
)
```

---

### 4. Municipality Aggregates (`aggregates/municipality_{year}.parquet`)

**Size:** ~30 KB per year  
**Records:** 500 (top municipalities by birth count)  
**Metrics:**
- `total_births`: Birth count per municipality
- `PESO_mean`, `PESO_median`: Birth weight by municipality
- `IDADEMAE_mean`: Maternal age by municipality
- `APGAR5_mean`: APGAR score by municipality
- `cesarean_rate_pct`: Cesarean rate by municipality

**Use Case:** Detailed geographic analysis, city comparisons

**Load Example:**
```python
# Load municipality aggregates
municipalities = pd.read_parquet('dashboard_data/aggregates/municipality_2024.parquet')

# Top 10 municipalities by birth count
top10 = municipalities.nlargest(10, 'total_births')
```

---

### 5. Combined Yearly (`aggregates/combined_yearly.parquet`)

**Size:** ~12 KB (scales with number of years)  
**Records:** 27 states × number of years  
**Purpose:** Multi-year state-level comparison

**Use Case:** Year-over-year trends, regional comparisons across time

**Load Example:**
```python
# Load combined yearly data
combined = pd.read_parquet('dashboard_data/aggregates/combined_yearly.parquet')

# Compare cesarean rates across years
import plotly.express as px
fig = px.line(
    combined, 
    x='year', 
    y='cesarean_rate_pct',
    color='state_code',
    title='Cesarean Rate Trends by State'
)
```

---

### 6. Metadata (`metadata.json`)

**Size:** ~2 KB  
**Content:** Dataset information, date ranges, summary statistics

**Structure:**
```json
{
  "generated_at": "2025-10-03T16:05:34",
  "total_years": 1,
  "years": [2024],
  "total_records": 2260034,
  "date_range": {
    "min": "2024-01-01",
    "max": "2024-12-31"
  },
  "yearly_summaries": [{...}],
  "schema": {
    "essential_columns": [...],
    "aggregate_metrics": [...]
  }
}
```

**Use Case:** Dashboard initialization, data validation, UI configuration

**Load Example:**
```python
import json

with open('dashboard_data/metadata.json') as f:
    metadata = json.load(f)

# Get available years for dropdown
available_years = metadata['years']

# Display key metrics
print(f"Total births: {metadata['total_records']:,}")
print(f"Date range: {metadata['date_range']['min']} to {metadata['date_range']['max']}")
```

---

## 📈 Key Statistics (2024)

| Metric | Value |
|--------|-------|
| **Total Births** | 2,260,034 |
| **Avg Maternal Age** | 27.8 years |
| **Avg Birth Weight** | 3,150 grams |
| **Cesarean Rate** | 60.6% |
| **Hospital Births** | 98.5% |
| **Multiple Pregnancies** | 2.4% |
| **Preterm Births** | 12.3% |
| **Avg APGAR (5min)** | 9.3 |

---

## 🚀 Usage Guidelines

### Loading Strategy

#### Option 1: Aggregates Only (Fastest - <10 MB)
```python
# Load only pre-aggregated data
monthly = pd.read_parquet('dashboard_data/aggregates/monthly_2024.parquet')
states = pd.read_parquet('dashboard_data/aggregates/state_2024.parquet')

# Memory: <5 MB
# Load time: <0.5 seconds
```

#### Option 2: Essential + Aggregates (Balanced - ~30 MB)
```python
# Load essential columns for detailed views
df = pd.read_parquet('dashboard_data/years/2024_essential.parquet')
monthly = pd.read_parquet('dashboard_data/aggregates/monthly_2024.parquet')

# Memory: ~150 MB
# Load time: <2 seconds
```

#### Option 3: Lazy Loading (Memory-Efficient)
```python
from functools import lru_cache

@lru_cache(maxsize=2)
def load_year_data(year):
    return pd.read_parquet(f'dashboard_data/years/{year}_essential.parquet')

# Load only when needed, cache last 2 years
df_2024 = load_year_data(2024)
```

---

## 🔄 Regenerating Data

To regenerate or add new years:

```bash
# Process a specific year
python scripts/create_dashboard_data.py --year 2024

# Process all available years
python scripts/create_dashboard_data.py --all

# Custom output directory
python scripts/create_dashboard_data.py --year 2024 --output_dir custom_dir
```

**Prerequisites:**
- Year data must have `complete.parquet` file in `data/SINASC/{year}/`
- Run data cleaning and feature engineering first if needed:
  ```bash
  python scripts/clean_file.py --year 2023
  python scripts/feature_engineering.py --year 2023
  ```

---

## 📊 Memory Profile

### File Sizes (on disk)
| File Type | Size per Year | Total (2024 only) |
|-----------|---------------|-------------------|
| Essential columns | ~30 MB | 30 MB |
| Monthly aggregates | ~10 KB | 10 KB |
| State aggregates | ~11 KB | 11 KB |
| Municipality aggregates | ~30 KB | 30 KB |
| Combined yearly | ~12 KB | 12 KB |
| Metadata | ~2 KB | 2 KB |
| **Total** | **~30 MB** | **~30 MB** |

### Memory Usage (when loaded)
| Component | Memory |
|-----------|--------|
| Essential columns only | ~150 MB |
| All aggregates | <5 MB |
| Essential + aggregates | ~155 MB |
| With Dash overhead | ~200 MB |
| **Safe for free tier** | ✅ <512 MB |

---

## 🎯 Dashboard Integration

### Recommended Architecture

```python
# app.py - Main Dash app
import dash
from dash import dcc, html, callback, Input, Output
import pandas as pd
import json

# Load metadata on startup
with open('dashboard_data/metadata.json') as f:
    METADATA = json.load(f)

# Load lightweight aggregates on startup
MONTHLY_DATA = {
    year: pd.read_parquet(f'dashboard_data/aggregates/monthly_{year}.parquet')
    for year in METADATA['years']
}

STATE_DATA = {
    year: pd.read_parquet(f'dashboard_data/aggregates/state_{year}.parquet')
    for year in METADATA['years']
}

# Lazy load detailed data
from functools import lru_cache

@lru_cache(maxsize=2)
def load_detailed_data(year, columns=None):
    """Load detailed year data with caching."""
    return pd.read_parquet(
        f'dashboard_data/years/{year}_essential.parquet',
        columns=columns
    )

# Use in callbacks
@callback(
    Output('timeline-chart', 'figure'),
    Input('year-dropdown', 'value')
)
def update_timeline(year):
    monthly = MONTHLY_DATA[year]
    # Create visualization
    return fig
```

---

## ✅ Data Quality

- **Completeness**: ✅ All 2024 records included
- **Date Range**: ✅ Full year (Jan 1 - Dec 31, 2024)
- **Missing Values**: ✅ Handled (converted to NaN, excluded from calculations)
- **Data Types**: ✅ Optimized (category, Int8, datetime64)
- **Aggregates**: ✅ Pre-computed, validated against raw data
- **Schema**: ✅ Consistent across files

---

## 🔮 Future Enhancements

- [ ] Add 2023 data (pending processing)
- [ ] Weekly aggregates for finer temporal analysis
- [ ] Hospital-level aggregates (using CNES data)
- [ ] Regional aggregates (North, Northeast, Southeast, South, Center-West)
- [ ] Demographic breakdowns (age groups, education levels)
- [ ] Specialized aggregates for ML models

---

## 📞 Support

For questions or issues with the dashboard data:
1. Check the parent `DATA_INVENTORY.md` for source data information
2. Verify data processing with `scripts/create_dashboard_data.py --help`
3. Review the dashboard architecture in `dashboard/ARCHITECTURE.md`

---

*Last Updated: October 3, 2025*  
*Data Source: DATASUS SINASC 2024*
