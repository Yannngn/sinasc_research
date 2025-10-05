# Quick Reference: Regenerating Dashboard Data

## ⚡ Quick Commands

### Regenerate All Years (Recommended)
```bash
cd /home/yannn/projects/Yannngn/sinasc-dashboard/sinasc_research
python src/pipeline/05_create_dashboard_data.py --all
```

### Regenerate Single Year
```bash
python src/pipeline/05_create_dashboard_data.py --year 2024
```

### Custom Directories
```bash
python src/pipeline/05_create_dashboard_data.py --all \
  --data_dir data/SINASC \
  --output_dir dashboard_data \
  --input_name engineered_features.parquet
```

---

## 📋 What Gets Regenerated

### New Metrics Added

#### 1. **Monthly Aggregates** (`monthly_YYYY.parquet`)
- ✨ `cesarean_count`: Absolute number of cesarean births per month

#### 2. **State Aggregates** (`state_YYYY.parquet`)
- ✨ `cesarean_count`: Absolute number of cesarean births by state
- ✨ `adolescent_pregnancy_pct`: % of births to mothers < 20 years
- ✨ `adolescent_pregnancy_count`: Count of adolescent pregnancies
- ✨ `very_young_pregnancy_pct`: % of births to mothers < 15 years
- ✨ `very_young_pregnancy_count`: Count of very young pregnancies

---

## 🎯 Why Regenerate?

The Geographic Dashboard page requires:
1. **Complete state-level metrics** for regional comparisons
2. **Adolescent pregnancy data** for demographic analysis
3. **Consistent count/percentage pairs** for dual visualizations

The Annual Analysis page now uses:
1. **Cesarean counts** for absolute number charts
2. **Cesarean percentages** for rate trend charts

---

## ⏱️ Expected Runtime

| Years | Records | Time | Disk Space |
|-------|---------|------|------------|
| 1     | ~3M     | ~30s | ~50 MB     |
| 7     | ~20M    | ~4m  | ~350 MB    |

*Tested on: Intel i5 / 16GB RAM / SSD*

---

## 📦 Output Structure

```
dashboard_data/
├── aggregates/
│   ├── monthly_2018.parquet          ← Updated
│   ├── monthly_2019.parquet          ← Updated
│   ├── monthly_2020.parquet          ← Updated
│   ├── monthly_2021.parquet          ← Updated
│   ├── monthly_2022.parquet          ← Updated
│   ├── monthly_2023.parquet          ← Updated
│   ├── monthly_2024.parquet          ← Updated
│   ├── state_2018.parquet            ← Updated
│   ├── state_2019.parquet            ← Updated
│   ├── state_2020.parquet            ← Updated
│   ├── state_2021.parquet            ← Updated
│   ├── state_2022.parquet            ← Updated
│   ├── state_2023.parquet            ← Updated
│   ├── state_2024.parquet            ← Updated
│   ├── municipality_2018.parquet     ← No changes
│   ├── municipality_2019.parquet     ← No changes
│   └── ...
├── years/
│   └── ...                            ← No changes
└── metadata.json                      ← Updated (includes new years)
```

---

## ✅ Verification

After regeneration, verify the new columns exist:

```python
import pandas as pd

# Check monthly aggregates
monthly = pd.read_parquet('dashboard_data/aggregates/monthly_2024.parquet')
assert 'cesarean_count' in monthly.columns, "Missing cesarean_count in monthly"
print("✅ Monthly aggregates OK")

# Check state aggregates
state = pd.read_parquet('dashboard_data/aggregates/state_2024.parquet')
required = [
    'cesarean_count',
    'adolescent_pregnancy_pct',
    'adolescent_pregnancy_count',
    'very_young_pregnancy_pct',
    'very_young_pregnancy_count'
]
missing = [col for col in required if col not in state.columns]
assert len(missing) == 0, f"Missing columns: {missing}"
print("✅ State aggregates OK")

print("\n🎉 All new metrics present!")
```

---

## 🔄 Before Regenerating

### 1. Backup Current Data (Optional)
```bash
# Create backup
cp -r dashboard_data dashboard_data_backup_$(date +%Y%m%d)

# Or move to backup folder
mv dashboard_data dashboard_data_old
```

### 2. Check Available Source Data
```bash
# List available years in SINASC data directory
ls -d data/SINASC/*/

# Expected output:
# data/SINASC/2018/
# data/SINASC/2019/
# data/SINASC/2020/
# data/SINASC/2021/
# data/SINASC/2022/
# data/SINASC/2023/
# data/SINASC/2024/
```

### 3. Verify Source Files Exist
```bash
# Check that engineered_features.parquet exists for each year
for year in {2018..2024}; do
  file="data/SINASC/$year/engineered_features.parquet"
  if [ -f "$file" ]; then
    size=$(du -h "$file" | cut -f1)
    echo "✅ $year: $size"
  else
    echo "❌ $year: MISSING"
  fi
done
```

---

## 🚨 Troubleshooting

### Error: "File not found"
```
⚠️  File not found: data/SINASC/2024/engineered_features.parquet
```

**Solution**: Run the feature engineering pipeline first:
```bash
python src/pipeline/03_create_engineered_features.py --year 2024
```

### Error: "Memory error"
**Solution**: Process years individually instead of `--all`:
```bash
for year in {2018..2024}; do
  python src/pipeline/05_create_dashboard_data.py --year $year
done
```

### Error: "Column not found"
**Solution**: Ensure you're using the latest pipeline code:
```bash
git pull origin dev
```

---

## 📊 Expected Log Output

```
============================================================
Processing Year: 2024
============================================================

📥 Loading data from data/SINASC/2024/engineered_features.parquet...
  ✅ Loaded 2,834,567 records with 51 columns

📅 Creating monthly aggregates for 2024...
  ✅ Saved 12 months of aggregates (0.02 MB)

🗺️  Creating state aggregates for 2024...
  ✅ Saved 27 states with aggregates (0.01 MB)

🏙️  Creating municipality aggregates for 2024 (top 500)...
  ✅ Saved 500 municipalities with aggregates (0.03 MB)

📈 Creating yearly summary for 2024...
  ✅ Created yearly summary

✅ Year 2024 processing complete!

============================================================
Creating Combined Files
============================================================

📊 Creating yearly aggregates...
  ✅ Saved yearly aggregates (0.01 MB)

📈 Creating combined yearly data...
  ✅ Combined data from 7 years (0.05 MB)

📝 Creating metadata...
  ✅ Saved metadata (0.01 MB)

============================================================
Dashboard Data Creation Complete!
============================================================

📦 Output directory: dashboard_data
📊 Total size: 350.2 MB
📅 Years processed: 7
📝 Total records: 19,841,489

✨ Ready for dashboard deployment!
```

---

## 🎯 Next Steps After Regeneration

1. **Restart Dashboard** (if running):
   ```bash
   # Stop current instance
   pkill -f "python dashboard/app.py"
   
   # Start fresh
   python dashboard/app.py
   ```

2. **Test Geographic Page**:
   - Navigate to http://localhost:8050/geographic
   - Select different years in dropdown
   - Verify all indicators load correctly
   - Check regional comparison chart
   - Verify state ranking table

3. **Test Annual Page**:
   - Navigate to http://localhost:8050/annual
   - Check "Número Mensal de Cesáreas" chart loads
   - Verify YoY badges appear on metric cards
   - Confirm all charts render without errors

4. **Verify Data Quality**:
   ```bash
   python -c "
   import pandas as pd
   df = pd.read_parquet('dashboard_data/aggregates/state_2024.parquet')
   print('State columns:', len(df.columns))
   print('Has cesarean_count:', 'cesarean_count' in df.columns)
   print('Has adolescent metrics:', 'adolescent_pregnancy_pct' in df.columns)
   "
   ```

---

## 📚 Related Documentation

- **Pipeline Enhancement Details**: `docs/PIPELINE_GEOGRAPHIC_ENHANCEMENT.md`
- **Geographic Page Implementation**: `docs/GEOGRAPHIC_IMPLEMENTATION.md`
- **YoY Change Feature**: `docs/YOY_CHANGE_FEATURE.md`
- **IBGE Data Guide**: `data/IBGE/README.md`

---

*Quick reference guide - Keep this handy for future regenerations!*
