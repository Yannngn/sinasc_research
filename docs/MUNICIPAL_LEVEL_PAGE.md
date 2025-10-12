# Municipal-Level Analysis Page

## Overview

The Municipal-Level Analysis page (`municipal_level.py`) has been successfully created and integrated into the SINASC Dashboard. This page provides detailed birth statistics and health indicators at the municipal level within selected states, with comprehensive visualizations and year-over-year comparisons.

## Features Implemented

### 1. **State Selection Interface**
- Dropdown menu with all Brazilian states sorted alphabetically
- Year selection dropdown
- Indicator selection dropdown with 10 health metrics

### 2. **Summary Cards**
Display key statistics for the selected state and year:
- **Total Births**: Total number of births in the state
- **Municipalities**: Number of municipalities with birth records
- **State-level Indicator**: Weighted average of the selected indicator
- **Variation**: Standard deviation showing indicator variability across municipalities

### 3. **Municipality Rankings**
Two interactive horizontal bar charts showing:
- **Top 10 Municipalities**: Highest values for the selected indicator
- **Bottom 10 Municipalities**: Lowest values for the selected indicator
- Includes formatted indicator values and birth counts
- Color-coded based on indicator type

### 4. **Distribution Analysis**
- **Histogram**: Shows the distribution of indicator values across all municipalities
- Includes a red dashed line indicating the state-wide mean
- Helps identify outliers and patterns

### 5. **Scatter Plot Analysis**
- **Birth Volume vs. Indicator**: Visualizes the relationship between birth volume and indicator values
- Color-coded by indicator value
- Bubble size represents birth volume
- Interactive hover tooltips with municipality names

## Data Source

The page uses the `agg_municipality_yearly` aggregate table from the database, which contains:
- Municipality-level aggregates by year
- All key health indicators (cesarean rate, preterm births, etc.)
- Birth counts for each municipality

## Technical Implementation

### File Structure
```
dashboard/pages/municipal_level.py
└── Functions:
    ├── create_layout() - Main page layout
    ├── register_callbacks() - Dash callbacks
    ├── update_municipal_content() - Main callback for content
    ├── _create_municipality_ranking_chart() - Ranking visualizations
    ├── _create_distribution_chart() - Histogram chart
    └── _create_scatter_chart() - Scatter plot
```

### Integration Points

1. **Added to `pages/__init__.py`**:
   ```python
   from . import annual, home, municipal_level, state_level
   __all__ = ["home", "annual", "state_level", "municipal_level"]
   ```

2. **Integrated in `app.py`**:
   - Import: `from pages import annual, home, municipal_level, state_level`
   - Navigation: Added "Municípios" link to navbar
   - Routing: Added `/municipal-level` route
   - Callbacks: Registered with `municipal_level.register_callbacks(app)`

### Key Dependencies

```python
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from components.cards import create_metric_card
from components.charts import format_brazilian_number
from config.settings import CHART_CONFIG, CHART_HEIGHT
from dash import Input, Output, callback, dcc, html
from data.loader import data_loader
```

## Available Indicators

The page supports analysis of 10 key health indicators:

| Category | Indicators |
|----------|-----------|
| **Percentage-based** | • Taxa de Cesárea (%)<br>• Taxa de Prematuridade (%)<br>• Taxa de Prematuridade Extrema (%)<br>• Taxa de Gravidez na Adolescência (%)<br>• Taxa de Baixo Peso ao Nascer (%)<br>• Taxa de APGAR5 Baixo (%)<br>• Taxa de Nascimentos Hospitalares (%) |
| **Mean values** | • Peso Médio ao Nascer (g)<br>• Idade Materna Média (anos)<br>• APGAR5 Médio |

## User Workflow

1. **Select State**: Choose a Brazilian state from the dropdown
2. **Select Year**: Pick the year for analysis (defaults to most recent)
3. **Select Indicator**: Choose the health indicator to analyze
4. **View Results**:
   - Summary cards show state-level statistics
   - Rankings highlight top and bottom performing municipalities
   - Distribution chart shows spread across municipalities
   - Scatter plot reveals relationships between birth volume and indicators

## Error Handling

The page includes comprehensive error handling:
- **No state selected**: Shows informative message prompting user to select
- **No data available**: Displays warning when data is missing for selected year
- **Empty state data**: Shows specific message when state has no records
- **General errors**: Catches and displays any unexpected errors

## Styling & UX

- **Consistent Design**: Follows the same design patterns as other pages
- **Responsive Layout**: Works on mobile, tablet, and desktop
- **Loading States**: Uses Dash loading components for better UX
- **Interactive Charts**: All charts support zoom, pan, and hover tooltips
- **Color Coding**: Charts use appropriate color scales (RdYlGn_r for percentages, Blues for means)
- **Brazilian Formatting**: Numbers formatted with Brazilian conventions (dot for thousands, comma for decimals)

## Performance Considerations

- **Data Caching**: Uses `@lru_cache` in data loader for efficient data retrieval
- **Aggregated Data**: Works with pre-aggregated municipality data (not raw records)
- **Conditional Loading**: Only loads data when a state is selected
- **Optimized Queries**: Filters data by state code to minimize data transfer

## Future Enhancements

Potential improvements for future iterations:
1. **Month-by-month trends**: Add time series analysis within a year
2. **Municipality comparison**: Allow selection of multiple municipalities for comparison
3. **Geographic map**: Add choropleth map of municipalities within the selected state
4. **Download capability**: Add button to export data as CSV/Excel
5. **Statistical tests**: Add confidence intervals and significance testing
6. **Filters**: Add filters for municipality size, urban/rural classification

## Testing Checklist

- [x] Page loads without errors
- [x] State dropdown populates correctly
- [x] Year and indicator dropdowns work
- [x] Summary cards display correct values
- [x] Ranking charts render properly
- [x] Distribution histogram shows mean line
- [x] Scatter plot displays correctly
- [x] Error messages display appropriately
- [x] Navigation works from navbar
- [x] Page is responsive on different screen sizes

## Notes

- The page follows the project's coding standards (PEP 8, type hints, docstrings)
- All charts use the consistent `CHART_CONFIG` and `CHART_HEIGHT` from settings
- Formatting utilities from `components.charts` ensure consistency
- The page uses the same indicator list as `state_level.py` for consistency

## Related Documentation

- [ARCHITECTURE.md](ARCHITECTURE.md) - Overall system architecture
- [DESIGN_SYSTEM.md](DESIGN_SYSTEM.md) - UI design guidelines
- [CODING_STANDARDS.md](CODING_STANDARDS.md) - Code style guide
- [GEOGRAPHIC_IMPLEMENTATION.md](GEOGRAPHIC_IMPLEMENTATION.md) - Geographic features

---

**Status**: ✅ Complete and integrated
**Last Updated**: 2025-10-11
**Author**: GitHub Copilot
