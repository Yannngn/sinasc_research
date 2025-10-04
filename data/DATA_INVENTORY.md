# Data Inventory & Analysis

**Generated:** October 3, 2025  
**Purpose:** Comprehensive overview of available data for SINASC Dashboard

---

## 📊 Data Summary

### SINASC Birth Records

#### 2024 Data (Fully Processed)
| File | Size | Records | Columns | Description |
|------|------|---------|---------|-------------|
| `raw.parquet` | 68 MB | 2,260,034 | 61 | Original SINASC data from DATASUS |
| `raw.csv` | - | 2,260,034 | 61 | CSV version of raw data |
| `clean.parquet` | 59 MB | 2,260,034 | ~60 | Cleaned data with standardized missing values |
| `complete.parquet` | **57 MB** | **2,260,034** | **51** | **✅ READY FOR DASHBOARD** - Cleaned + engineered features |
| `engineered_features.parquet` | 48 MB | 2,260,034 | - | Additional calculated features |
| `selected_features.parquet` | 34 MB | 2,260,034 | ~35 | Subset of most important columns |
| `weight_percentiles.parquet` | 39 MB | 2,260,034 | - | Birth weight percentile calculations |
| `calculated_weight_percentiles.parquet` | 4.9 MB | - | - | Aggregated weight statistics |

**Memory Profile (complete.parquet):**
- In-memory size: ~880 MB (when loaded)
- On-disk size: 57 MB (compressed)
- Date range: 2024-01-01 to 2024-12-31
- Data types: Optimized (category, Int8, boolean, datetime64)

#### 2023 Data (Raw Only)
| File | Size | Records | Columns | Status |
|------|------|---------|---------|--------|
| `raw.parquet` | 77 MB | 2,537,576 | 61 | ⚠️ Needs processing |
| `raw.csv` | - | 2,537,576 | 61 | Original CSV |

**Notes:**
- 2023 data needs to be processed through cleaning pipeline
- Date format: DDMMYYYY (needs conversion)
- Memory: ~1.5 GB when loaded (not optimized)
- **Action needed:** Run `scripts/clean_file.py` and `scripts/feature_engineering.py` on 2023 data

---

## 🗺️ Geographic Reference Data

### IBGE (Brazilian Institute of Geography and Statistics)

| File | Size | Records | Description |
|------|------|---------|-------------|
| `municipalities.json` | 4.4 MB | 5,570 | Complete municipality data with hierarchy |
| `municipalities_flat.csv` | 718 KB | 5,570 | Flattened municipality lookup |

**Structure:**
```json
{
  "id": "3550308",
  "nome": "São Paulo",
  "microrregiao": {
    "mesorregiao": {
      "UF": {
        "id": "35",
        "sigla": "SP",
        "nome": "São Paulo",
        "regiao": {"id": "3", "sigla": "SE", "nome": "Sudeste"}
      }
    }
  }
}
```

**Use Cases:**
- Municipality code → name mapping
- State code → state name
- Regional aggregations (North, Northeast, Southeast, South, Center-West)
- Geographic filtering and grouping

---

## 🏥 Healthcare Facilities Data

### CNES (National Registry of Healthcare Establishments)

| File | Size | Records | Description |
|------|------|---------|-------------|
| `estabelecimentos_cnes.json` | 681 MB | ~500,000+ | Full CNES data (nested JSON) |
| `estabelecimentos_cnes.csv` | 170 MB | ~500,000+ | CSV version |
| `estabelecimentos_cnes_flat.csv` | 68 MB | ~500,000+ | Flattened with selected columns |
| `estabelecimentos_cnes_subset.json` | 120 KB | 100 | Test subset (JSON) |
| `estabelecimentos_cnes_subset.csv` | 1.2 MB | 10,000 | Test subset (CSV) |

**Selected Columns (flat version):**
- `CO_UNIDADE`: Unit code
- `CO_CNES`: CNES establishment code
- `NO_FANTASIA`: Facility name
- `TP_UNIDADE`: Establishment type
- `CO_MUNICIPIO_GESTOR`: Managing municipality code
- `NO_LOGRADOURO`: Street address
- `NO_BAIRRO`: Neighborhood
- `CO_CEP`: Postal code
- `SG_UF_GESTOR`: Managing state

**Use Cases:**
- `CODESTAB` (in SINASC) → Hospital name lookup
- Hospital location mapping
- Facility type analysis (public, private, etc.)
- Healthcare coverage analysis

**⚠️ Size Warning:** 
- Full JSON is 681 MB - too large for web dashboard
- Use `estabelecimentos_cnes_flat.csv` (68 MB) or create aggregates
- Consider pre-filtering to only establishments with SINASC records

---

## 📋 Metadata Files

### SINASC Schema & Mappings

| File | Description |
|------|-------------|
| `categorical.json` | Category value labels (e.g., 1="Hospital", 2="Vaginal") |
| `engineered_categorical.json` | Labels for engineered features |
| `dtypes.json` | Column data type specifications |
| `rename_mapping.json` | Portuguese → English column name mappings |
| `schema.csv` | Complete SINASC schema definition |

**Example from categorical.json:**
```json
{
  "LOCNASC": {
    "1": "Hospital",
    "2": "Outros estabelecimentos de saúde",
    "3": "Domicílio",
    "9": "Ignorado"
  },
  "PARTO": {
    "1": "Vaginal",
    "2": "Cesário",
    "9": "Ignorado"
  }
}
```

---

## 🎯 Dashboard Data Strategy

### Recommended Approach

#### For Initial Development (Single Year)
```python
# Use 2024 complete.parquet
df = pd.read_parquet('data/SINASC/2024/complete.parquet')
# Size: 57 MB on disk, ~880 MB in memory
# Ready to use with all features
```

#### For Multi-Year Dashboard (After Processing 2023)

**Option 1: Load on Demand**
```python
def load_year_data(year: int, columns: list = None) -> pd.DataFrame:
    """Load specific year with optional column selection."""
    return pd.read_parquet(
        f'data/SINASC/{year}/complete.parquet',
        columns=columns
    )
```

**Option 2: Pre-Aggregate for Web**
Create monthly/yearly aggregates to reduce memory:
```python
# Generate aggregates
monthly_births = df.groupby(df['DTNASC'].dt.to_period('M')).agg({
    'PESO': 'mean',
    'IDADEMAE': 'mean',
    'APGAR5': 'mean',
    'PARTO': lambda x: (x == 2).mean(),  # Cesarean rate
})
# Save as lightweight aggregate file
monthly_births.to_parquet('data/aggregates/monthly_summary_2024.parquet')
```

---

## 📈 Data Processing Pipeline

### Current State
```
RAW DATA (2023, 2024)
    ↓ scripts/read_file.py
LOADED + SCHEMA APPLIED
    ↓ scripts/clean_file.py
CLEANED (standardized missing values)
    ↓ scripts/feature_engineering.py
ENGINEERED FEATURES (bins, categories)
    ↓ scripts/feature_selection.py
SELECTED FEATURES (dashboard subset)
    ↓ scripts/calculate_weight_z.py
WEIGHT STATISTICS
    ↓
COMPLETE.PARQUET ✅ (2024 only)
```

### Missing Steps for 2023
```bash
# Process 2023 data to match 2024
cd /home/yannn/projects/Yannngn/sinasc-dashboard/sinasc_research

# 1. Clean 2023 data
.venv/bin/python scripts/clean_file.py \
  --data_dir data/SINASC \
  --year 2023 \
  --dataset raw

# 2. Engineer features
.venv/bin/python scripts/feature_engineering.py \
  --data_dir data/SINASC \
  --year 2023 \
  --dataset clean

# 3. Calculate weight percentiles
.venv/bin/python scripts/calculate_weight_z.py \
  --data_dir data/SINASC \
  --year 2023

# Result: data/SINASC/2023/complete.parquet
```

---

## 🎨 Column Categories (complete.parquet)

### Demographics (10 columns)
- `IDADEMAE`, `IDADEPAI` - Parental ages
- `IDADEMAEBIN`, `IDADEPAIBIN` - Age bins
- `ESTCIVMAE` - Maternal marital status
- `ESCMAE` - Maternal education
- `OCUPMAE` - Maternal occupation
- `RACACOR`, `RACACORMAE` - Newborn/maternal race
- `SEXO` - Newborn sex

### Geographic (2 columns)
- `CODMUNNASC` - Birth municipality code
- `CODMUNRES` - Residence municipality code
- `DESLOCNASCBOOL` - Migration indicator (birth ≠ residence)

### Prenatal Care (7 columns)
- `CONSULTAS` - Number of prenatal consultations
- `CONSPRENAT` - Prenatal consultation indicator
- `MESPRENAT` - Month prenatal care started
- `MESPRENATBIN` - Binned start month
- `KOTELCHUCK` - Prenatal care adequacy index

### Pregnancy History (9 columns)
- `QTDGESTANT` - Number of previous pregnancies
- `QTDPARTNOR` - Previous normal deliveries
- `QTDPARTCES` - Previous cesarean sections
- `GRAVIDEZ` - Pregnancy type (single, twins)
- `PRIMEGEST` - First pregnancy indicator
- `PARTNORPREV`, `PARTCESPREV` - Previous delivery indicators
- Binned versions: `QTDGESTANTBIN`, `QTDPARTNORBIN`, `QTDPARTCESBIN`

### Delivery Characteristics (8 columns)
- `LOCNASC` - Place of birth
- `CODESTAB` - Healthcare establishment code
- `PARTO` - Delivery type (vaginal/cesarean)
- `GESTACAO` - Gestational weeks category
- `SEMAGESTAC` - Gestational weeks (numeric)
- `TPAPRESENT` - Fetal presentation
- `TPROBSON` - Robson classification
- `STTRABPART`, `STCESPARTO` - Labor/cesarean indicators
- `PARIDADE` - Parity

### Newborn Health (10 columns)
- `PESO` - Birth weight (grams)
- `PESOBIN` - Weight category
- `PESOPERC` - Weight percentile
- `PESOPERCBIN` - Percentile category
- `APGAR1`, `APGAR5` - APGAR scores (1 min, 5 min)
- `APGAR1BIN`, `APGAR5BIN` - APGAR categories

### Temporal (3 columns)
- `DTNASC` - Birth date (datetime64)
- `HORANASC` - Birth hour
- `HORANASCBIN` - Hour category

### Administrative (2 columns)
- `PAIREGIST` - Father registration indicator
- `CODOCUPMAE` - Maternal occupation code

---

## 🚀 Dashboard Optimization Recommendations

### Memory Budget: <512 MB (Free Tier Hosting)

#### Strategy 1: Column Selection
Only load columns needed for specific visualizations:
```python
ESSENTIAL_COLS = [
    'DTNASC', 'CODMUNNASC', 'CODMUNRES', 
    'IDADEMAE', 'PARTO', 'PESO', 'APGAR5', 'GESTACAO'
]
df = pd.read_parquet('complete.parquet', columns=ESSENTIAL_COLS)
# Reduces memory by ~70%
```

#### Strategy 2: Pre-Aggregation
Create dashboard-specific aggregate files:
```python
# Monthly aggregates (~1-2 MB per year)
# State aggregates (~100 KB per year)
# Municipality aggregates (~5-10 MB per year)
```

#### Strategy 3: Lazy Loading
Load year data only when requested:
```python
@lru_cache(maxsize=2)  # Cache last 2 years
def get_year_data(year: int) -> pd.DataFrame:
    return pd.read_parquet(f'data/SINASC/{year}/complete.parquet')
```

#### Strategy 4: Downsampling for Visualizations
For scatter plots and large histograms:
```python
df_sample = df.sample(n=10000) if len(df) > 10000 else df
```

---

## 📦 Recommended Dashboard Data Package

### Create Optimized Dashboard Files
```bash
# Structure for deployment
dashboard_data/
├── metadata.json              # Years, record counts, date ranges
├── geo/
│   ├── states.json           # 27 states (5 KB)
│   ├── municipalities.json   # 5,570 municipalities (4.4 MB)
│   └── hospital_subset.json  # Only hospitals in SINASC (500 KB)
├── aggregates/
│   ├── monthly_2023.parquet  # (500 KB)
│   ├── monthly_2024.parquet  # (500 KB)
│   ├── state_2023.parquet    # (50 KB)
│   ├── state_2024.parquet    # (50 KB)
│   └── combined_yearly.parquet # (100 KB)
└── years/
    ├── 2023_essential.parquet # (15-20 MB)
    └── 2024_essential.parquet # (15-20 MB)

Total: ~50 MB (fits easily in free hosting)
```

---

## ✅ Data Quality Assessment

### 2024 Complete Data
- **Completeness**: ✅ Excellent
- **Data Types**: ✅ Optimized
- **Missing Values**: ✅ Standardized (coded as -1 or 9)
- **Date Range**: ✅ Complete year (2024-01-01 to 2024-12-31)
- **Features**: ✅ Engineered features included
- **Memory Efficiency**: ✅ 57 MB (down from 68 MB raw)

### 2023 Data
- **Completeness**: ⚠️ Raw only
- **Processing**: ❌ Needs cleaning + feature engineering
- **Date Format**: ⚠️ Integer format (needs conversion)
- **Memory**: ❌ Not optimized (1.5 GB)

---

## 🎯 Next Steps for Dashboard

### Immediate (Use Existing Data)
1. ✅ Use `2024/complete.parquet` for initial development
2. ✅ Load `IBGE/municipalities_flat.csv` for geographic features
3. ✅ Load `categorical.json` for value labels
4. ⚠️ Create hospital subset from `CNES/estabelecimentos_cnes_flat.csv`

### Short-Term (Process 2023)
1. Run cleaning pipeline on 2023 data
2. Generate 2023 complete.parquet
3. Test multi-year functionality

### Medium-Term (Optimization)
1. Create pre-aggregated files for common queries
2. Build monthly partition files
3. Generate dashboard-specific data package (<50 MB)

### Long-Term (Expansion)
1. Process additional years (2022, 2021, etc.)
2. Create time-series specific aggregates
3. Build API for on-demand data access

---

## 📞 Data Access Patterns for Dashboard

### Home Page (Overview)
```python
# Load: Pre-aggregated yearly totals (~100 KB)
# Columns: None (use aggregates)
# Memory: <10 MB
```

### Timeline Page (Temporal Analysis)
```python
# Load: Monthly aggregates + selected columns
# Columns: ['DTNASC', 'PESO', 'IDADEMAE', 'PARTO', 'APGAR5']
# Memory: ~200 MB per year
```

### Geographic Page (Maps)
```python
# Load: Municipality aggregates + geo reference
# Columns: ['CODMUNNASC', 'PESO', 'PARTO', 'APGAR5']
# Memory: ~150 MB per year
```

### Insights Page (Deep Dive)
```python
# Load: Full data with filtering
# Columns: User-selected subset
# Memory: <400 MB (with proper filtering)
```

---

*This inventory will be updated as new data is processed or requirements change.*
