# Next Steps: Map Enhancements (Tasks 5-7)

## Status: Ready for Implementation

The foundation work is complete. This document provides implementation guidance for the remaining map enhancement tasks.

---

## Task 5: Enhanced State Choropleth Map

### Goal
Add metric type toggle to existing state map to show:
1. Absolute values (e.g., 5,234 cesarean births)
2. Percentage of total births (e.g., 45.2% cesarean rate) ← **Currently implemented**
3. Per 1,000 population (e.g., 12.5 cesareans per 1k people)

### Implementation Steps

#### Step 1: Add UI Toggle Control

**Location**: `dashboard/pages/state_level.py` in `create_layout()`

```python
# Add after the indicator dropdown
dbc.Row([
    dbc.Col([
        html.Label("Tipo de Métrica:", className="fw-bold mb-2"),
        dcc.RadioItems(
            id="state-map-metric-type",
            options=[
                {"label": "📊 Valores Absolutos", "value": "absolute"},
                {"label": "📈 Percentual (%)", "value": "percentage"},
                {"label": "👥 Por 1.000 habitantes", "value": "per_1k"},
            ],
            value="percentage",
            inline=True,
            labelClassName="me-4",
            className="mb-3"
        ),
    ], width=12)
], className="mb-4")
```

#### Step 2: Update Map Callback

**Location**: `dashboard/pages/state_level.py` in `update_choropleth_map()`

```python
@callback(
    Output("geo-choropleth-map", "figure"),
    [
        Input("geo-year-dropdown", "value"),
        Input("geo-indicator-dropdown", "value"),
        Input("state-map-metric-type", "value"),  # NEW INPUT
    ],
)
def update_choropleth_map(year: int, indicator: str, metric_type: str):
    df = data_loader.load_yearly_state_aggregates(year)
    geojson = data_loader._load_brazil_states_geojson()
    
    if df.empty or not geojson:
        return error_figure()
    
    df["state_code"] = df["state_code"].astype(str).str.zfill(2)
    
    # Determine which column to display based on metric type
    if metric_type == "absolute":
        # Convert from percentage to count column
        if "_pct" in indicator:
            display_col = indicator.replace("_pct", "_count")
        else:
            display_col = indicator  # Already absolute
        title_suffix = "(Valores Absolutos)"
        is_percent = False
        
    elif metric_type == "per_1k":
        # Calculate per 1k population
        pop_df = data_loader.load_population_data(level="states")
        df = df.merge(pop_df[["state_code", "population"]], on="state_code", how="left")
        
        # Get the absolute count column
        if "_pct" in indicator:
            count_col = indicator.replace("_pct", "_count")
        else:
            count_col = indicator
        
        # Calculate per 1k
        display_col = f"{indicator}_per_1k"
        df[display_col] = (df[count_col] / df["population"]) * 1000
        title_suffix = "(Por 1.000 habitantes)"
        is_percent = False
        
    else:  # percentage (default)
        display_col = indicator
        title_suffix = ""
        is_percent = "_pct" in indicator
    
    # Get indicator info from configuration
    config = _get_indicator_config(indicator)
    indicator_title = config.relative_title if is_percent else config.absolute_title
    
    # Create choropleth
    fig = px.choropleth(
        df,
        geojson=geojson,
        locations="state_code",
        featureidkey="properties.id",
        color=display_col,
        color_continuous_scale="YlOrRd" if is_percent else "Blues",
        hover_name="state_name",
        hover_data={
            "state_code": True,
            display_col: ":.2f",
            "total_births": ":,",
        },
        title=f"{indicator_title} {title_suffix}"
    )
    
    # Update layout
    fig.update_geos(
        fitbounds="locations",
        visible=False,
        projection_type="mercator"
    )
    
    return fig


def _get_indicator_config(indicator: str):
    """Helper to find indicator configuration."""
    from config.constants import GEOGRAPHIC_INDICATORS
    
    for key, config in GEOGRAPHIC_INDICATORS.items():
        if indicator in config.get_absolute_columns() + config.get_relative_columns():
            return config
    
    # Default config if not found
    return type('obj', (object,), {
        'relative_title': indicator,
        'absolute_title': indicator
    })()
```

#### Step 3: Add Helper Functions

```python
def format_map_value(value: float, metric_type: str, indicator: str) -> str:
    """Format map hover values based on metric type."""
    if metric_type == "percentage":
        return f"{value:.1f}%"
    elif metric_type == "per_1k":
        return f"{value:.2f} por 1k hab."
    else:  # absolute
        return f"{int(value):,}".replace(",", ".")
```

### Testing Checklist

- [ ] Toggle between all three metric types
- [ ] Verify colors change appropriately (YlOrRd for %, Blues for absolute)
- [ ] Check hover data displays correctly
- [ ] Test with states that have missing population data
- [ ] Verify title updates with metric type
- [ ] Ensure legend shows appropriate units

---

## Task 6: Municipal Choropleth Map

### Goal
Add a new choropleth map to the municipal page showing municipality boundaries within the selected state.

### Prerequisites

**Data Requirement**: Municipality-level GeoJSON data
- Check if `dim_municipality` table has `geometry` column
- If not, need to load municipality GeoJSON from IBGE

### Implementation Steps

#### Step 1: Add Data Loader Method

**Location**: `dashboard/data/loader.py`

```python
@lru_cache(maxsize=27)  # One per state
def load_municipality_geojson(self, state_code: str) -> dict:
    """
    Load GeoJSON for municipalities within a specific state.
    
    Args:
        state_code: Two-digit state code (e.g., '35' for São Paulo)
    
    Returns:
        GeoJSON dictionary with municipality boundaries
    """
    try:
        # Try loading from database
        query = """
            SELECT 
                municipality_code,
                municipality_name,
                geometry
            FROM dim_municipality
            WHERE state_code = %(state_code)s
            AND geometry IS NOT NULL
        """
        gdf = gpd.read_postgis(
            query,
            self.engine,
            params={"state_code": state_code},
            geom_col="geometry"
        )
        
        if gdf.empty:
            return {}
        
        # Ensure proper orientation (exterior ring counter-clockwise)
        gdf["geometry"] = gdf["geometry"].apply(
            lambda geom: orient(geom, sign=1.0) if geom else None
        )
        
        return gdf.__geo_interface__
        
    except Exception as e:
        print(f"Error loading municipality GeoJSON for state {state_code}: {e}")
        return {}
```

#### Step 2: Add Map Section to Layout

**Location**: `dashboard/pages/municipal_level.py` in the content generation

```python
# Add after distribution charts, before footer
dbc.Row([
    dbc.Col(
        dbc.Card([
            dbc.CardHeader([
                dbc.Row([
                    dbc.Col(
                        html.H5("🗺️ Mapa Municipal", className="mb-0"),
                        width="auto"
                    ),
                    dbc.Col(
                        dcc.RadioItems(
                            id=f"mun-map-metric-type-{state_code}",  # Unique per state
                            options=[
                                {"label": "📊 Absoluto", "value": "absolute"},
                                {"label": "📈 Percentual", "value": "percentage"},
                                {"label": "👥 Por 1k hab.", "value": "per_1k"},
                            ],
                            value="percentage",
                            inline=True,
                            labelClassName="me-3 small"
                        ),
                        width="auto"
                    )
                ], align="center", justify="between")
            ], className="bg-light"),
            dbc.CardBody(
                dcc.Loading(
                    id=f"loading-mun-map-{state_code}",
                    children=html.Div(id=f"mun-map-container-{state_code}")
                ),
                style={"minHeight": "600px"}
            )
        ], className="shadow-sm"),
        width=12,
        className="mb-4"
    )
], className="mb-4")
```

#### Step 3: Add Map Callback

```python
@callback(
    Output(f"mun-map-container-{state_code}", "children"),
    [
        Input("municipal-indicator-dropdown", "value"),
        Input(f"mun-map-metric-type-{state_code}", "value"),
    ]
)
def update_municipal_map(indicator: str, metric_type: str):
    """Create municipality choropleth map."""
    
    # Load GeoJSON for this state
    geojson = data_loader.load_municipality_geojson(state_code)
    
    if not geojson:
        return html.Div(
            dbc.Alert(
                "Dados geográficos não disponíveis para este estado.",
                color="warning"
            )
        )
    
    # Prepare data (similar to state map logic)
    df_map = df_state_mun.copy()
    
    # Calculate display column based on metric type
    if metric_type == "absolute":
        display_col = indicator.replace("_pct", "_count") if "_pct" in indicator else indicator
    elif metric_type == "per_1k":
        # Load municipality population
        pop_df = data_loader.load_population_data(level="municipalities")
        df_map = df_map.merge(
            pop_df[["municipality_code", "population"]],
            on="municipality_code",
            how="left"
        )
        count_col = indicator.replace("_pct", "_count") if "_pct" in indicator else indicator
        display_col = f"{indicator}_per_1k"
        df_map[display_col] = (df_map[count_col] / df_map["population"]) * 1000
    else:
        display_col = indicator
    
    # Create choropleth
    fig = px.choropleth(
        df_map,
        geojson=geojson,
        locations="municipality_code",
        featureidkey="properties.municipality_code",
        color=display_col,
        color_continuous_scale="YlOrRd" if "_pct" in indicator else "Blues",
        hover_name="municipality_name",
        hover_data={
            display_col: ":.2f",
            "total_births": ":,"
        }
    )
    
    # Fit map to municipality boundaries
    fig.update_geos(
        fitbounds="geojson",
        visible=False,
        projection_type="mercator"
    )
    
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        height=600
    )
    
    return dcc.Graph(figure=fig, config=CHART_CONFIG)
```

### Challenges & Solutions

**Challenge 1**: Dynamic callback IDs per state
- **Solution**: Use f-strings to create unique IDs: `f"mun-map-{state_code}"`

**Challenge 2**: GeoJSON data may not exist for all states
- **Solution**: Graceful fallback with informative message

**Challenge 3**: Municipality population data may be missing
- **Solution**: Check for NaN and handle appropriately

### Testing Checklist

- [ ] Map loads for states with GeoJSON data
- [ ] Graceful message for states without GeoJSON
- [ ] Hover shows municipality name and values
- [ ] Toggle between metric types works
- [ ] Colors match indicator type
- [ ] Map fits municipality boundaries correctly
- [ ] Performance is acceptable (map loads in <3s)

---

## Task 7: Integration Testing

### Test Suite Structure

```python
# tests/test_geographic_pages.py

def test_zero_birth_filtering():
    """Test that municipalities with 0 births are filtered."""
    df = load_test_data()
    df_filtered = filter_municipalities(df, "35")
    assert all(df_filtered["total_births"] > 0)

def test_edge_case_few_municipalities():
    """Test handling of states with <5 municipalities."""
    # Mock data with only 3 municipalities
    result = update_municipal_content("53", 2024, "cesarean_pct")
    assert "Dados insuficientes" in result

def test_dynamic_ranking_titles():
    """Test that ranking titles adapt to available data."""
    # Mock state with 7 municipalities
    result = create_ranking_cards(7)
    assert "Top 7" in result

def test_indicator_configuration_loading():
    """Test that all indicators load from config."""
    from config.constants import GEOGRAPHIC_INDICATORS
    assert len(GEOGRAPHIC_INDICATORS) >= 7
    assert "cesarean" in GEOGRAPHIC_INDICATORS

def test_format_count_indicators():
    """Test formatting of count (absolute) indicators."""
    result = format_indicator_value(5234, "cesarean_count")
    assert result == "5.234"

def test_format_percentage_indicators():
    """Test formatting of percentage indicators."""
    result = format_indicator_value(45.2, "cesarean_pct")
    assert result == "45,2%"

def test_map_metric_toggle():
    """Test that map updates with metric type changes."""
    # Test absolute
    fig_abs = update_choropleth_map(2024, "cesarean_pct", "absolute")
    assert "cesarean_count" in fig_abs.data[0].customdata
    
    # Test per 1k
    fig_per1k = update_choropleth_map(2024, "cesarean_pct", "per_1k")
    assert "_per_1k" in fig_per1k.data[0].customdata
```

### Manual Testing Checklist

#### Municipal Page
- [ ] Select state → Data loads correctly
- [ ] Select state with 0-4 municipalities → Info message shows
- [ ] Select state with 5-10 municipalities → "Top N" adapts
- [ ] Switch indicators → Charts update
- [ ] Verify only municipalities with >0 births show
- [ ] Check distribution histogram shows mean line
- [ ] Verify scatter plot displays correctly

#### State Page
- [ ] Switch between indicators → Map updates
- [ ] Toggle metric type → Colors and values change
- [ ] Check WHO reference lines (cesarean, preterm)
- [ ] Verify regional comparison chart
- [ ] Check scatter plot with population data
- [ ] Test with different years

#### Cross-Page Consistency
- [ ] Same indicators available on both pages
- [ ] Same formatting used (count vs percentage)
- [ ] Consistent color schemes
- [ ] Similar layout patterns
- [ ] Consistent error messages

---

## Estimated Effort

| Task | Complexity | Estimated Time | Status |
|------|-----------|----------------|--------|
| Task 5: State Map Toggle | Medium | 3-4 hours | Not Started |
| Task 6: Municipal Map | High | 5-6 hours | Not Started |
| Task 7: Testing | Medium | 2-3 hours | Not Started |
| **Total** | | **10-13 hours** | |

---

## Prerequisites Before Starting

- [ ] Verify municipality GeoJSON data is available
- [ ] Check municipality population data exists
- [ ] Ensure state population data is accessible
- [ ] Review existing map implementation
- [ ] Understand GeoJSON structure in database

---

## Success Criteria

### Task 5: State Map
- ✅ Three metric types work correctly
- ✅ Map colors change appropriately
- ✅ Hover data shows correct values
- ✅ Title updates with metric type
- ✅ No performance degradation

### Task 6: Municipal Map
- ✅ Map loads for available states
- ✅ Graceful handling of missing data
- ✅ Municipality boundaries render correctly
- ✅ Three metric types functional
- ✅ Responsive to state selection

### Task 7: Testing
- ✅ All unit tests pass
- ✅ Manual test checklist complete
- ✅ Edge cases handled
- ✅ No regressions in existing features
- ✅ Performance benchmarks met

---

**Ready to implement when needed!**
