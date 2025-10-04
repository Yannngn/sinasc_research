# Dashboard Structure Update

## Overview
The dashboard has been restructured to separate multi-year comparison from detailed annual analysis.

## Pages

### 🏠 Home (`/`)
**Purpose**: Multi-year comparison and overview statistics (2019-2024)

**Features**:
- **Year Summary Cards** (last 3 years shown):
  - Total births with Brazilian formatting (2.677.101)
  - 6 metrics per year in compact 2-column layout:
    - 👩 Maternal Age (with comma decimal: 28,5 anos)
    - ⚖️ Birth Weight (3.200g)
    - ❤️ APGAR 5 (8,9)
    - 🏥 Cesarean Rate (55,2%)
    - ⚠️ Preterm Rate (11,3%)
    - 🏥 Hospital Births (98,5%)
  - Inline title:value format with icons
  
- **Birth Evolution Chart**: 
  - Bar chart with text labels inside bars
  - Brazilian formatted numbers
  - No redundant title (card header sufficient)
  
- **Cesarean Comparison**: 
  - Grouped bar chart (vaginal vs cesarean)
  - Brazilian formatting
  
- **Preterm Births Analysis**:
  - Stacked bar chart: moderate + extreme (<32 weeks)
  - Text inside/outside bars with 1.25x y-axis padding
  - Dual-line chart: total vs extreme rates
  - WHO 10% reference line
  
- **Adolescent Pregnancy Analysis**:
  - Stacked bar chart: older teens (13-19) + very young (<15)
  - Dual-line chart: total vs very young rates
  - Brazilian formatting throughout

**Data Used**:
- `yearly.parquet` - 12.5KB, 5 years, 23 columns with new metrics
- Year summaries from loader with caching

### 📊 Análise Anual (`/annual`)
**Purpose**: Detailed analysis for a specific year

**Features**:
- Year selector dropdown
- Dynamic metric cards (births, age, weight, cesarean rate)
- Monthly births timeline (bar chart)
- Delivery type distribution (donut pie chart)
- Maternal age distribution (histogram with mean line)

**Data Used**:
- `monthly_{year}.parquet` - Monthly aggregates
- `{year}_essential.parquet` - Full dataset for histograms
- Year summaries from `metadata.json`

### 📈 Temporal (Coming soon)
Temporal trends and time-series analysis

### 🗺️ Geográfico (Coming soon)
Geographic analysis with choropleth maps

### 🔍 Insights (Coming soon)
Deep-dive insights and correlations

## Files Changed

### New Files
- `pages/home.py` - Multi-year comparison page
- `pages/annual.py` - Renamed from old `home.py`, detailed annual analysis

### Modified Files
- `app.py` - Updated routing and navigation bar
- `pages/__init__.py` - Export both `home` and `annual` modules

## Navigation Flow
```
Home (Overview) → Annual Analysis (Select Year) → Detailed Charts
     ↓                    ↓
Multi-year trends    Single year deep-dive
```

## Usage

### To view all years comparison:
Navigate to **Home** (default page)

### To analyze a specific year:
1. Click **"📊 Análise Anual"** in navigation
2. Select year from dropdown
3. All charts and metrics update automatically

## Benefits
- ✅ Clear separation of concerns
- ✅ Better user experience (overview → detail)
- ✅ Easier to add new years without cluttering
- ✅ Scalable structure for future features
