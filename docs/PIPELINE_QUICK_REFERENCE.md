# 📋 Database Pipeline Quick Reference

## 🚀 Common Workflows

### Add New Year (2025)
```bash
# One command - auto-optimizes!
python dashboard/data/staging.py --years 2025
python dashboard/data/promote_sql.py local
```

### Incremental Update (Add Missing Years)
```bash
# Auto-detects missing years (2015-2025)
python dashboard/data/staging.py
python dashboard/data/promote_sql.py local
```

### Re-Ingest Specific Years
```bash
python dashboard/data/staging.py --years 2023 2024 --overwrite
python dashboard/data/promote_sql.py local
```

### Full Pipeline Reset
```bash
# WARNING: Deletes and re-ingests everything
python dashboard/data/staging.py --overwrite
python dashboard/data/promote_sql.py local --pandas
```

---

## 📊 Check Database Status

### List Existing Years
```bash
python -c "
from dashboard.data.database import get_staging_db_engine
from sqlalchemy import inspect
engine = get_staging_db_engine()
inspector = inspect(engine)
years = sorted([t.split('_')[-1] for t in inspector.get_table_names() if t.startswith('raw_sinasc_')])
print(f'📅 SINASC years in database: {years}')
print(f'📊 Total: {len(years)} years')
"
```

### Count Records by Year
```bash
python -c "
from dashboard.data.database import get_staging_db_engine
from sqlalchemy import text, inspect
engine = get_staging_db_engine()
inspector = inspect(engine)
years = sorted([t.split('_')[-1] for t in inspector.get_table_names() if t.startswith('raw_sinasc_') and t.split('_')[-1].isdigit()])

print('Year | Records')
print('-----|----------')
with engine.begin() as conn:
    for year in years:
        count = conn.execute(text(f'SELECT COUNT(*) FROM raw_sinasc_{year}')).scalar()
        print(f'{year} | {count:>10,}')
"
```

---

## ⚡ Performance Modes

### Fast Mode (Recommended)
```bash
# Uses optimized SQL promotion
python dashboard/data/promote_sql.py local
```

### Safe Mode (Slower but Verified)
```bash
# Uses pandas for compatibility
python dashboard/data/promote_sql.py local --pandas
```

### Development Mode (No Optimization)
```bash
# Skip optimization for testing
python dashboard/data/staging.py --years 2024 --no-optimize
```

---

## 🔧 Troubleshooting

### "Table already exists" Error
```bash
# Use --overwrite to force re-ingest
python dashboard/data/staging.py --years 2024 --overwrite
```

### Optimization Stuck
```bash
# Run optimization manually
python dashboard/data/optimize.py --years 2024
```

### Promotion Failed
```bash
# Fall back to pandas mode
python dashboard/data/promote_sql.py local --pandas
```

### Check Database Connection
```bash
python -c "
from dashboard.data.database import get_staging_db_engine
try:
    engine = get_staging_db_engine()
    engine.connect()
    print('✅ Database connection successful')
except Exception as e:
    print(f'❌ Database connection failed: {e}')
"
```

---

## 📁 File Guide

| File | Purpose | When to Use |
|------|---------|-------------|
| `staging.py` | Ingest raw data from APIs | Adding new years, initial setup |
| `optimize.py` | Optimize data types | Manual optimization (usually auto-runs) |
| `dimensions.py` | Create lookup tables | After new data added |
| `promote_sql.py` | Copy to production (FAST) | Deploy to dashboard |
| `promote.py` | Copy to production (SLOW) | Fallback if SQL fails |
| `loader.py` | Load data for dashboard | Used by dashboard app |

---

## 🎯 Decision Tree

```
Need to add data?
│
├─ New year (2025)? → python dashboard/data/staging.py --years 2025
│
├─ Multiple years? → python dashboard/data/staging.py --years 2023 2024 2025
│
├─ All missing years? → python dashboard/data/staging.py (incremental mode)
│
└─ Re-ingest existing? → python dashboard/data/staging.py --years 2024 --overwrite

After ingestion, always promote:
→ python dashboard/data/promote_sql.py local
```

---

## ⏱️ Expected Times (3M records per year)

| Operation | Time (old) | Time (new) | Speed-up |
|-----------|-----------|-----------|----------|
| Ingest 1 year | 30 min | 30 min | 1x (same) |
| Optimize 1 year | 60 min | 60 min | 1x (TODO) |
| Promote all tables | 40 min | **4 min** | **10x** |
| **Full pipeline** | **2h 10min** | **1h 34min** | **1.4x** |

*Future: Optimize step → 6 min (10x faster) = 40 min total (4x faster)*

---

## 🔗 Related Docs

- **PIPELINE_IMPROVEMENTS_SUMMARY.md**: Full implementation details
- **DATA_PIPELINE_ANALYSIS.md**: Performance analysis
- **dashboard/data/README.md**: Data module documentation
