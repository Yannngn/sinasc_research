# Dashboard Migration Plan: Parquet → PostgreSQL

## Executive Summary

The dashboard currently loads data from **Parquet files** (`dashboard_data/aggregates/*.parquet`), but the pipeline now produces data in **PostgreSQL tables** (`agg_*`, `fact_*`, `dim_*`). This document outlines the migration strategy to connect the dashboard directly to the database.

---

## Current State Analysis

### ✅ What's Working (Pipeline)
1. **Step 01-02**: Creates `fact_births` table with ~12.7M records
2. **Step 03**: Creates dimension tables (`dim_maternal_age_group`, `dim_birth_weight_category`, `dim_maternal_occupation`)
3. **Step 04**: Adds 26 engineered boolean features (optimized single-pass approach)
4. **Step 05**: Creates aggregate tables:
   - `agg_yearly` (5 records: 2015-2024 yearly summaries)
   - `agg_monthly` (10 records: monthly breakdowns by year)
   - `agg_state_yearly` (135 records: state-level yearly aggregates)
   - `agg_municipality_yearly` (0 records - needs investigation)

### ✅ What's Working (Promote Script)
**File**: `dashboard/data/promote.py`

- ✅ Automatically discovers all `fact_*`, `dim_*`, `agg_*` tables
- ✅ Uses pandas `read_sql_table()` + `to_sql()` for transfers
- ✅ Supports multiple destinations (local prod, Render cloud)
- ✅ Handles errors and provides progress feedback

**Status**: Ready to use, no changes needed.

### ❌ What Needs Migration (Dashboard Data Layer)

**File**: `dashboard/data/loader.py`

Currently uses **file-based loading**:
```python
def load_monthly_aggregates(self, year: int) -> pd.DataFrame:
    file_path = AGGREGATES_DIR / f"monthly_{year}.parquet"
    df = pd.read_parquet(file_path)
    return df
```

Must be changed to **database loading**:
```python
def load_monthly_aggregates(self, year: int) -> pd.DataFrame:
    engine = get_prod_db_engine()
    query = "SELECT * FROM agg_monthly WHERE year = :year"
    df = pd.read_sql(query, engine, params={"year": year})
    return df
```

---

## Schema Mapping: Database → Dashboard Expectations

### 1. Yearly Aggregates

**Database Table**: `agg_yearly`
```sql
SELECT * FROM agg_yearly LIMIT 1;
```
**Columns**:
- `year` (INTEGER)
- `total_births` (BIGINT)
- `peso_mean` (FLOAT)
- `idademae_mean` (FLOAT)
- `apgar5_mean` (FLOAT)
- `cesarean_pct` (FLOAT)
- `preterm_birth_pct` (FLOAT)
- `extreme_preterm_birth_pct` (FLOAT)
- `adolescent_pregnancy_pct` (FLOAT)
- `very_young_pregnancy_pct` (FLOAT)
- `low_birth_weight_pct` (FLOAT)
- `low_apgar5_pct` (FLOAT)
- `hospital_birth_pct` (FLOAT)

**Dashboard Expectation** (via `metadata.json`):
```json
{
  "year": 2024,
  "total_births": 2500000,
  "pregnancy": {
    "adolescent_pregnancy_pct": 15.2,
    "very_young_pregnancy_pct": 0.8,
    "preterm_birth_pct": 11.5
  },
  "delivery_type": {
    "cesarean_pct": 56.3
  },
  "health_indicators": {
    "low_birth_weight_pct": 8.9,
    "low_apgar5_pct": 1.2
  },
  "location": {
    "hospital_birth_pct": 98.5
  }
}
```

**Action Required**: Transform flat DB structure into nested JSON structure.

---

### 2. Monthly Aggregates

**Database Table**: `agg_monthly`
```sql
SELECT * FROM agg_monthly WHERE year = 2024 ORDER BY month;
```
**Columns**:
- `year` (INTEGER)
- `month` (INTEGER)
- `total_births` (BIGINT)
- `peso_mean` (FLOAT)
- `cesarean_pct` (FLOAT)
- `preterm_birth_pct` (FLOAT)

**Dashboard Expectation**:
```python
# Requires `year_month` column (datetime) or constructed from year+month
df["year_month"] = pd.to_datetime(df["year"].astype(str) + "-" + df["month"].astype(str))
df["month_label"] = df["month"].apply(lambda x: MONTH_NAMES[x - 1])
```

**Action Required**: Add datetime construction in `DataLoader.load_monthly_aggregates()`.

---

### 3. State Aggregates

**Database Table**: `agg_state_yearly`
```sql
SELECT * FROM agg_state_yearly WHERE year = 2024 LIMIT 3;
```
**Columns**:
- `state_code` (TEXT) — e.g., "SP", "RJ"
- `state_name` (TEXT) — e.g., "São Paulo"
- `region_name` (TEXT) — e.g., "Sudeste"
- `year` (INTEGER)
- `total_births` (BIGINT)
- `peso_mean` (FLOAT)
- `idademae_mean` (FLOAT)
- `apgar5_mean` (FLOAT)
- `cesarean_pct` (FLOAT)
- `preterm_birth_pct` (FLOAT)
- `extreme_preterm_birth_pct` (FLOAT)
- `adolescent_pregnancy_pct` (FLOAT)
- `low_birth_weight_pct` (FLOAT)

**Dashboard Expectation**: Uses `state_code` for GeoJSON matching and choropleth maps.

**Action Required**: Verify `state_code` matches GeoJSON feature IDs (should be 2-letter state abbreviations).

---

### 4. Municipality Aggregates

**Database Table**: `agg_municipality_yearly`
```sql
SELECT * FROM agg_municipality_yearly WHERE year = 2024 LIMIT 3;
```
**Columns**:
- `municipality_code` (TEXT) — 7-digit IBGE code
- `municipality_name` (TEXT)
- `state_abbr` (TEXT)
- `year` (INTEGER)
- `total_births` (BIGINT)
- `peso_mean` (FLOAT)
- `idademae_mean` (FLOAT)
- `cesarean_pct` (FLOAT)
- `preterm_birth_pct` (FLOAT)

**Current Issue**: Table has 0 records (likely because of `HAVING COUNT(fb.id) >= 10` filter).

**Action Required**:
1. Review filter logic in `step_05_aggregate.py`
2. Verify JOIN condition between `fact_births` and `raw_ibge_municipalities_id`
3. Potentially lower threshold or investigate data quality issues

---

## Migration Strategy

### Phase 1: Dual-Mode Support (Recommended)
Allow the dashboard to run with **either** files or database, using an environment variable:

```python
# dashboard/data/loader.py
import os
from data.database import get_prod_db_engine

USE_DATABASE = os.getenv("USE_DATABASE", "False") == "True"

class DataLoader:
    def load_yearly_aggregates(self) -> pd.DataFrame:
        if USE_DATABASE:
            engine = get_prod_db_engine()
            return pd.read_sql_table("agg_yearly", engine)
        else:
            # Fallback to file-based loading
            file_path = AGGREGATES_DIR / "yearly.parquet"
            return pd.read_parquet(file_path)
```

**Benefits**:
- ✅ Zero-downtime migration
- ✅ Easy rollback if issues arise
- ✅ Can test database mode locally before deploying

---

### Phase 2: Pure Database Mode
Once validated, remove file-based code and default to database:

```python
class DataLoader:
    def __init__(self, use_staging: bool = False):
        """
        Initialize data loader.
        
        Args:
            use_staging: If True, connect to staging DB; otherwise production DB
        """
        from data.database import get_staging_db_engine, get_prod_db_engine
        self.engine = get_staging_db_engine() if use_staging else get_prod_db_engine()
        self.metadata = self._load_metadata_from_db()
```

---

## Required Code Changes

### 1. Update `dashboard/data/loader.py`

#### Method: `_load_metadata()` → `_load_metadata_from_db()`
**Current**: Reads `dashboard_data/metadata.json`  
**New**: Generates metadata from `agg_yearly` table

```python
def _load_metadata_from_db(self) -> Dict:
    """Generate metadata from database tables."""
    df_yearly = pd.read_sql_table("agg_yearly", self.engine)
    
    yearly_summaries = []
    for _, row in df_yearly.iterrows():
        yearly_summaries.append({
            "year": int(row["year"]),
            "total_births": int(row["total_births"]),
            "pregnancy": {
                "adolescent_pregnancy_pct": float(row["adolescent_pregnancy_pct"]),
                "very_young_pregnancy_pct": float(row["very_young_pregnancy_pct"]),
                "preterm_birth_pct": float(row["preterm_birth_pct"]),
            },
            "delivery_type": {
                "cesarean_pct": float(row["cesarean_pct"]),
            },
            "health_indicators": {
                "low_birth_weight_pct": float(row["low_birth_weight_pct"]),
                "low_apgar5_pct": float(row["low_apgar5_pct"]),
            },
            "location": {
                "hospital_birth_pct": float(row["hospital_birth_pct"]),
            },
        })
    
    return {
        "years": sorted([s["year"] for s in yearly_summaries]),
        "yearly_summaries": yearly_summaries,
        "generated_at": pd.Timestamp.now().isoformat(),
    }
```

#### Method: `load_monthly_aggregates(year)`
```python
@lru_cache(maxsize=10)
def load_monthly_aggregates(self, year: int) -> pd.DataFrame:
    """Load monthly aggregated data for a specific year."""
    query = "SELECT * FROM agg_monthly WHERE year = :year ORDER BY month"
    df = pd.read_sql(query, self.engine, params={"year": year})
    
    # Add computed columns expected by dashboard
    df["year_month"] = pd.to_datetime(
        df["year"].astype(str) + "-" + df["month"].astype(str).str.zfill(2)
    )
    df["month_label"] = df["month"].apply(lambda x: MONTH_NAMES[x - 1])
    
    return df
```

#### Method: `load_state_aggregates(year)`
```python
@lru_cache(maxsize=10)
def load_state_aggregates(self, year: int) -> pd.DataFrame:
    """Load state aggregates for a specific year."""
    query = "SELECT * FROM agg_state_yearly WHERE year = :year ORDER BY state_code"
    df = pd.read_sql(query, self.engine, params={"year": year})
    return df
```

#### Method: `load_municipality_aggregates(year)`
```python
@lru_cache(maxsize=10)
def load_municipality_aggregates(self, year: int) -> pd.DataFrame:
    """Load municipality aggregates for a specific year."""
    query = "SELECT * FROM agg_municipality_yearly WHERE year = :year ORDER BY total_births DESC"
    df = pd.read_sql(query, self.engine, params={"year": year})
    return df
```

#### Method: `load_yearly_aggregates()`
```python
@lru_cache(maxsize=1)
def load_yearly_aggregates(self) -> pd.DataFrame:
    """Load yearly aggregates with key indicators per year."""
    return pd.read_sql_table("agg_yearly", self.engine)
```

#### Method: `load_combined_yearly()` (Deprecated?)
**Current**: Reads `combined_yearly.parquet`  
**Question**: Is this different from `agg_yearly`? If not, remove this method and update callers to use `load_yearly_aggregates()`.

---

### 2. Remove File Dependencies

**Files to check/update**:
- `dashboard/config/settings.py` — Remove `AGGREGATES_DIR`, `YEARS_DIR` if unused
- `dashboard/data/loader.py` — Remove all Parquet file loading
- Update any scripts that generate `dashboard_data/metadata.json`

---

### 3. Update Environment Variables

**Add to `.env`**:
```bash
# Production database (dashboard queries this)
PRODUCTION_DATABASE_URL=postgresql://user:pass@localhost:5432/sinasc_prod_db

# Use database instead of files (set to True after migration)
USE_DATABASE=True
```

---

## Testing Checklist

### Unit Tests (Run Locally)
```bash
# 1. Test database connection
uv run python -c "from dashboard.data.database import get_prod_db_engine; print(get_prod_db_engine())"

# 2. Test data loader
uv run python -c "from dashboard.data.loader import data_loader; print(data_loader.get_available_years())"

# 3. Test aggregate loading
uv run python -c "from dashboard.data.loader import data_loader; print(data_loader.load_yearly_aggregates())"
```

### Integration Tests (Run Dashboard)
```bash
# 1. Promote staging → local production
uv run python dashboard/data/promote.py local

# 2. Start dashboard with database mode
USE_DATABASE=True uv run python dashboard/app.py

# 3. Verify pages render:
#    - Home page (year cards, comparison charts)
#    - Annual page (year selector, monthly trends)
#    - Geographic page (state maps, regional analysis)
```

### Smoke Tests (Visual Verification)
- [ ] Home page loads without errors
- [ ] Year summary cards display correct metrics
- [ ] Monthly trend charts render with proper labels
- [ ] State choropleth map displays correctly
- [ ] Clicking year tabs switches data
- [ ] Filters and dropdowns work

---

## Rollback Plan

If database migration causes issues:

1. Set `USE_DATABASE=False` in `.env`
2. Restart dashboard (will fall back to Parquet files)
3. Debug database queries in isolation
4. Fix issues and retry

---

## Performance Considerations

### Database Query Optimization
1. **Add indexes** on frequently queried columns:
   ```sql
   CREATE INDEX idx_agg_yearly_year ON agg_yearly(year);
   CREATE INDEX idx_agg_monthly_year ON agg_monthly(year);
   CREATE INDEX idx_agg_state_year ON agg_state_yearly(year, state_code);
   ```

2. **Connection pooling**: SQLAlchemy engines already use pooling (default 5 connections).

3. **Caching**: The `@lru_cache` decorators remain effective for database queries.

### Expected Performance
- **Parquet files**: ~50-200ms per file load (disk I/O)
- **PostgreSQL queries**: ~10-50ms per query (network + query execution)
- **Result**: Database should be **faster** for small aggregates, similar for large datasets.

---

## Known Issues & Future Work

### Issue 1: Municipality Aggregates Empty
**Root Cause**: `agg_municipality_yearly` has 0 records.

**Investigation Steps**:
1. Check if JOIN condition is correct:
   ```sql
   SELECT COUNT(DISTINCT fb."CODMUNNASC") 
   FROM fact_births fb 
   JOIN raw_ibge_municipalities_id dm ON fb."CODMUNNASC" = dm.id;
   ```
2. Check municipality ID format (7-digit vs 6-digit codes)
3. Review HAVING filter (`COUNT(fb.id) >= 10`)

**Temporary Fix**: Lower threshold or remove HAVING clause.

---

### Issue 2: Missing `has_father_registered` Feature
**Root Cause**: `IDADEPAI` column doesn't exist in `selected_sinasc_*` tables.

**Options**:
1. Add `IDADEPAI` to `ESSENTIAL_COLUMNS` in `step_01_select.py`
2. Accept missing feature (26/27 features is still good coverage)

---

### Issue 3: `load_essential_data()` Method
**Current**: Loads individual birth records from `{year}_essential.parquet` files.

**Question**: Is this method used by any dashboard pages? If not, can be removed.

**If used**: Will need to query `fact_births` directly:
```python
def load_essential_data(self, year: int, columns: Optional[List[str]] = None) -> pd.DataFrame:
    if columns:
        cols_str = ", ".join([f'"{c}"' for c in columns])
        query = f'SELECT {cols_str} FROM fact_births WHERE CAST(SUBSTR(CAST("DTNASC" AS TEXT), 1, 4) AS INTEGER) = :year'
    else:
        query = 'SELECT * FROM fact_births WHERE CAST(SUBSTR(CAST("DTNASC" AS TEXT), 1, 4) AS INTEGER) = :year'
    
    return pd.read_sql(query, self.engine, params={"year": year})
```

⚠️ **Warning**: Loading 2M+ individual records will be **slow**. Consider pagination or pre-filtering.

---

## Timeline Estimate

| Phase | Task | Time | Dependencies |
|-------|------|------|--------------|
| 1 | Update `DataLoader` class | 2-3 hours | Database schema finalized |
| 2 | Test locally with staging DB | 1 hour | Phase 1 complete |
| 3 | Promote to local prod + test | 30 min | Phase 2 complete |
| 4 | Update environment configs | 15 min | Phase 3 complete |
| 5 | Deploy to Render/Hugging Face | 1 hour | Phase 4 complete |
| 6 | Monitor and fix issues | 1-2 hours | Phase 5 complete |

**Total**: ~6-8 hours of focused development work.

---

## Next Steps

1. **Review this document** and confirm migration strategy
2. **Fix municipality aggregates** issue (investigate JOIN/filtering)
3. **Implement Phase 1** (dual-mode support) in `data/loader.py`
4. **Test locally** with staging database
5. **Promote to production** and verify dashboard functionality
6. **Deploy to cloud** (Render or Hugging Face Spaces)

---

## Questions for Discussion

1. Should we keep `load_essential_data()` method, or is it unused?
2. Do we need `combined_yearly.parquet` functionality, or is `agg_yearly` sufficient?
3. What's the preferred deployment target (Render, Hugging Face, both)?
4. Should we add more aggregate tables (e.g., `agg_quarterly`, `agg_region_yearly`)?
5. Do we want real-time data updates, or is batch promotion sufficient?

---

**Status**: Ready for implementation. Promote script works, pipeline produces correct tables, migration path is clear.
