# Geographic Pages Enhancement Plan

## Overview

This document outlines the planned enhancements to the state-level and municipal-level geographic analysis pages, focusing on:
1. Robust handling of municipalities with zero births
2. Unified indicator configuration system
3. Enhanced map visualizations with multiple metric views

## Current Status

### ✅ Completed

1. **Zero Birth Filtering** (Municipal Level)
   - Municipalities with 0 births are now filtered out automatically
   - Edge case handling for states with fewer than 5 municipalities
   - Dynamic ranking titles (Top N instead of hardcoded "Top 10")
   - Informative messages when data is insufficient

2. **Geographic Indicator Configuration** (constants.py)
   - Created `GEOGRAPHIC_INDICATORS` dictionary with `IndicatorConfig` objects
   - Includes 7 key indicators: cesarean, preterm, extreme_preterm, adolescent_pregnancy, low_birth_weight, low_apgar5, hospital_birth
   - Each indicator has absolute and relative metrics configured
   - Consistent with existing `INDICATOR_MAPPINGS` structure

### 🚧 Remaining Tasks

The following enhancements are planned but not yet implemented:

3. **Refactor State-Level Page** (state_level.py)
   - Replace hardcoded `INDICATOR_OPTIONS` with dynamically generated options from `GEOGRAPHIC_INDICATORS`
   - Use `IndicatorConfig` for consistent formatting and labeling
   - Add support for absolute value views alongside percentage views

4. **Refactor Municipal-Level Page** (municipal_level.py)
   - Replace hardcoded `INDICATOR_OPTIONS` with configuration-driven approach
   - Ensure consistent handling with state-level page
   - Support both absolute and relative metrics

5. **Enhanced State Choropleth Map** (state_level.py)
   - Add dropdown/toggle to switch between:
     - Absolute values (e.g., total cesarean count)
     - Percentage of births (e.g., cesarean rate %)
     - Per 1,000 population (requires population data integration)
   - Update map colors and legends dynamically based on metric type

6. **Municipal Choropleth Map** (municipal_level.py)
   - Create new choropleth map showing municipalities within selected state
   - Support same three metric views as state map
   - Load municipality-level GeoJSON data
   - Handle states with varying numbers of municipalities

7. **Integration Testing**
   - Verify filtering logic works correctly
   - Test edge cases (states with few municipalities)
   - Ensure maps render properly with all metric types
   - Validate consistent formatting across pages

---

## Implementation Details

### 1. Zero Birth Filtering (✅ Completed)

**Location**: `dashboard/pages/municipal_level.py`

**Changes**:
```python
# Before
df_state_mun = df_mun[df_mun["state_code"] == state_code].copy()

# After
df_state_mun = df_mun[(df_mun["state_code"] == state_code) & (df_mun["total_births"] > 0)].copy()
```

**Edge Case Handling**:
```python
total_mun_with_births = len(df_state_mun)
if total_mun_with_births < 5:
    # Show informative message instead of attempting visualization
    return html.Div(dbc.Alert(...))
```

**Dynamic Ranking**:
```python
# Adapt to available data
n_top = min(10, total_mun_with_births)
top_n_mun = df_state_mun.nlargest(n_top, indicator)
bottom_n_mun = df_state_mun.nsmallest(n_top, indicator)

# Use in card headers
html.H5(f"🏆 Top {n_top} Municípios (Maior Valor)")
```

---

### 2. Geographic Indicator Configuration (✅ Completed)

**Location**: `dashboard/config/constants.py`

**Structure**:
```python
GEOGRAPHIC_INDICATORS = {
    "cesarean": IndicatorConfig(
        absolute="cesarean_count",           # Column for absolute values
        relative="cesarean_pct",             # Column for percentage
        absolute_title="Número de Cesáreas",
        relative_title="Taxa de Cesárea (%)",
        labels="Cesáreas",
        colors="warning",
        recommended_relative_limit=15.0,     # WHO recommendation
        recommended_name="Referência OMS (15%)",
    ),
    # ... 6 more indicators
}
```

**Benefits**:
- Single source of truth for indicator metadata
- Easy to add new indicators
- Consistent formatting across pages
- Reference lines for WHO/health authority recommendations

---

### 3. State-Level Page Refactoring (🚧 Planned)

**Current State**: `dashboard/pages/state_level.py`

Hardcoded options:
```python
INDICATOR_OPTIONS = [
    {"label": "Taxa de Cesárea (%)", "value": "cesarean_pct"},
    {"label": "Taxa de Prematuridade (%)", "value": "preterm_pct"},
    # ... 8 more hardcoded options
]
```

**Proposed Changes**:

1. **Generate options dynamically**:
```python
from config.constants import GEOGRAPHIC_INDICATORS

# Generate options from configuration
INDICATOR_OPTIONS = []
for key, config in GEOGRAPHIC_INDICATORS.items():
    # Add relative (percentage) option
    INDICATOR_OPTIONS.append({
        "label": config.relative_title,
        "value": config.get_relative_columns()[0]
    })
    # Add absolute option
    INDICATOR_OPTIONS.append({
        "label": config.absolute_title,
        "value": config.get_absolute_columns()[0]
    })
```

2. **Update formatting function**:
```python
def format_indicator_value(value: float, indicator: str, config: IndicatorConfig) -> str:
    """Use IndicatorConfig for consistent formatting"""
    # Determine if percentage or absolute
    is_percentage = indicator in config.get_relative_columns()
    
    if is_percentage:
        return f"{value:.1f}%".replace(".", ",")
    else:
        return format_brazilian_number(int(value))
```

---

### 4. Municipal-Level Page Refactoring (🚧 Planned)

**Similar approach to state-level**, but also includes:

- Filtering logic (already implemented)
- Edge case handling (already implemented)
- Configuration-based indicator selection
- Consistent formatting with state-level page

---

### 5. Enhanced State Choropleth Map (🚧 Planned)

**Location**: `dashboard/pages/state_level.py`

**New UI Component**:
```python
dcc.RadioItems(
    id="state-map-metric-type",
    options=[
        {"label": "Valores Absolutos", "value": "absolute"},
        {"label": "Percentual (%)", "value": "percentage"},
        {"label": "Por 1.000 habitantes", "value": "per_1k"},
    ],
    value="percentage",
    inline=True,
    className="mb-3"
)
```

**Updated Callback**:
```python
@callback(
    Output("geo-choropleth-map", "figure"),
    [
        Input("geo-year-dropdown", "value"),
        Input("geo-indicator-dropdown", "value"),
        Input("state-map-metric-type", "value"),  # NEW
    ],
)
def update_choropleth_map(year: int, indicator: str, metric_type: str):
    df = data_loader.load_yearly_state_aggregates(year)
    
    # Determine which column to display
    if metric_type == "absolute":
        col = indicator.replace("_pct", "_count")
    elif metric_type == "per_1k":
        # Calculate per 1k population
        pop_df = data_loader.load_population_data(level="states")
        df = df.merge(pop_df, on="state_code")
        df[f"{indicator}_per_1k"] = (df[col] / df["population"]) * 1000
        col = f"{indicator}_per_1k"
    else:  # percentage
        col = indicator
    
    # Create choropleth
    fig = px.choropleth(df, geojson=geojson, locations="state_code", color=col, ...)
    return fig
```

---

### 6. Municipal Choropleth Map (🚧 Planned)

**Location**: `dashboard/pages/municipal_level.py`

**Requirements**:
- Load municipality-level GeoJSON for selected state
- Display municipalities within state boundaries
- Support same metric types as state map
- Handle states with varying municipality counts

**Data Loading**:
```python
# In data/loader.py (may need to add)
def load_municipality_geojson(self, state_code: str) -> dict:
    """Load GeoJSON for municipalities in a specific state"""
    query = """
        SELECT municipality_code, municipality_name, geometry 
        FROM dim_municipality 
        WHERE state_code = %(state_code)s
    """
    gdf = gpd.read_postgis(query, self.engine, params={"state_code": state_code}, geom_col="geometry")
    return gdf.__geo_interface__
```

**New Section in Layout**:
```python
dbc.Row([
    dbc.Col(
        dbc.Card([
            dbc.CardHeader([
                html.H5("🗺️ Mapa Municipal", className="mb-0"),
                dcc.RadioItems(
                    id="mun-map-metric-type",
                    options=[...],  # Same as state map
                    value="percentage",
                    inline=True
                )
            ]),
            dbc.CardBody(
                dcc.Graph(id="municipal-choropleth-map", ...)
            )
        ]),
        width=12
    )
])
```

---

## Data Requirements

### Population Data Integration

For "per 1,000 population" metrics, we need:

**State Level**:
- `dim_ibge_id_states` table with population column
- Already available via `data_loader.load_population_data(level="states")`

**Municipal Level**:
- `dim_ibge_id_municipalities` table with population column
- May need to add: `data_loader.load_population_data(level="municipalities")`

**Calculation**:
```python
# For any indicator
rate_per_1k = (indicator_count / population) * 1000

# Example: Cesarean rate per 1,000 population
cesarean_per_1k = (cesarean_count / population) * 1000
```

---

## Testing Plan

### Unit Tests

1. **Filtering Logic**:
   - Test with municipalities having 0 births
   - Test with states having < 5, 5-10, and >10 municipalities
   - Verify correct birth counts after filtering

2. **Indicator Configuration**:
   - Verify all indicators load from config
   - Test absolute and relative column retrieval
   - Validate formatting for different indicator types

3. **Map Rendering**:
   - Test with all metric types (absolute, percentage, per_1k)
   - Verify color scales adjust appropriately
   - Test with missing population data

### Integration Tests

1. **Page Navigation**:
   - Navigate to municipal level → select state → verify data loads
   - Switch between indicators → verify charts update
   - Change metric type → verify map updates

2. **Edge Cases**:
   - Load state with 0 municipalities (should show message)
   - Load state with 1-4 municipalities (should show info message)
   - Load state with all metrics missing (should handle gracefully)

3. **Data Consistency**:
   - Verify sum of municipality births equals state total
   - Check that percentages are weighted correctly
   - Validate per-1k calculations

---

## Migration Path

### Phase 1 (✅ Completed)
- Filter zero-birth municipalities
- Create indicator configuration
- Handle edge cases

### Phase 2 (Next)
- Refactor state_level.py to use configuration
- Refactor municipal_level.py to use configuration
- Add absolute value support to dropdowns

### Phase 3
- Add metric type toggle to state map
- Integrate population data
- Implement per-1k calculations

### Phase 4
- Add choropleth map to municipal page
- Load municipality GeoJSON
- Support all three metric types

### Phase 5
- Testing and validation
- Documentation updates
- User acceptance testing

---

## Benefits

### For Users
- **Clearer insights**: See both absolute numbers and percentages
- **Better comparisons**: Per-population metrics normalize for state/municipality size
- **More context**: Reference lines show health authority recommendations
- **Robust experience**: Graceful handling of edge cases

### For Developers
- **Maintainability**: Single source of truth for indicators
- **Extensibility**: Easy to add new indicators
- **Consistency**: Unified formatting and labeling
- **Testability**: Configuration-driven approach easier to test

---

## Notes

- All changes maintain backward compatibility
- Existing functionality preserved while adding new features
- Progressive enhancement approach (pages work without new features)
- Mobile-responsive design maintained throughout

---

**Status**: Phase 1 complete, Phase 2-5 planned
**Last Updated**: 2025-10-11
**Author**: GitHub Copilot
