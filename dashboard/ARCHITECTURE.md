# SINASC Dashboard - Technical Architecture

## System Overview

The SINASC Dashboard is a data-intensive web application for analyzing Brazilian birth records. This document details the technical architecture, data flow, and implementation decisions.

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        User Browser                          │
│  ┌────────────┐  ┌─────────────┐  ┌──────────────────┐     │
│  │  Filters   │  │   Charts    │  │      Maps        │     │
│  └────────────┘  └─────────────┘  └──────────────────┘     │
└───────────────────────┬─────────────────────────────────────┘
                        │ HTTP/WebSocket
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                    Dash Application Server                   │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Callback Engine (Python)                 │  │
│  │  • Input validation                                   │  │
│  │  • State management                                   │  │
│  │  • Event handling                                     │  │
│  └──────────────────────────────────────────────────────┘  │
│                        │                                     │
│  ┌──────────────────────────────────────────────────────┐  │
│  │            Data Processing Layer                      │  │
│  │  • Filtering    • Aggregation    • Transformation    │  │
│  └──────────────────────────────────────────────────────┘  │
│                        │                                     │
│  ┌──────────────────────────────────────────────────────┐  │
│  │               Caching Layer                           │  │
│  │  • In-memory cache (LRU)                             │  │
│  │  • Pre-computed aggregates                           │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────┘
                         │ File I/O
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   Data Storage Layer                         │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────┐   │
│  │   Raw Data  │  │  Aggregated  │  │  Geo Reference  │   │
│  │   (Parquet) │  │    (Parquet) │  │     (GeoJSON)   │   │
│  └─────────────┘  └──────────────┘  └─────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## Data Flow

### 1. **Initial Load**
```
User opens dashboard
    → App loads configuration
    → Load pre-aggregated metadata (years, states, counts)
    → Render initial UI with default filters
    → Display cached/default visualizations
```

### 2. **User Interaction**
```
User changes filter (e.g., date range)
    → Callback triggered
    → Validate inputs
    → Check cache for existing result
    → If cache miss:
        → Load relevant data chunks
        → Apply filters
        → Aggregate/transform data
        → Cache result
    → Generate visualization
    → Update UI components
```

### 3. **Multi-Year Query**
```
User selects multiple years
    → Load yearly index file
    → Identify required data files
    → Load files in parallel (if possible)
    → Concatenate DataFrames
    → Apply filters across combined data
    → Paginate results
    → Stream to visualization
```

---

## Data Storage Strategy

### File Structure
```
dashboard_data/
├── metadata.json                        # Years, record counts, schema info
├── aggregates/                          # Pre-computed aggregates
│   ├── yearly.parquet                  # All years combined (5 years: 2019-2024)
│   ├── combined_yearly.parquet         # Legacy support
│   ├── monthly_2019.parquet            # Monthly aggregates by year
│   ├── monthly_2020.parquet
│   ├── monthly_2021.parquet
│   ├── monthly_2022.parquet
│   ├── monthly_2023.parquet
│   ├── monthly_2024.parquet
│   ├── state_2019.parquet              # State-level aggregates
│   ├── state_2020.parquet
│   ├── state_2021.parquet
│   ├── state_2022.parquet
│   ├── state_2023.parquet
│   ├── state_2024.parquet
│   ├── municipality_2019.parquet       # Municipality aggregates
│   ├── municipality_2020.parquet
│   ├── municipality_2021.parquet
│   ├── municipality_2022.parquet
│   ├── municipality_2023.parquet
│   └── municipality_2024.parquet
└── years/
    ├── 2019_essential.parquet          # Essential columns only
    ├── 2020_essential.parquet
    ├── 2021_essential.parquet
    ├── 2022_essential.parquet
    ├── 2023_essential.parquet
    └── 2024_essential.parquet
```

### Data Optimization

#### Parquet Optimization
```python
# Writing optimized Parquet files
df.to_parquet(
    'output.parquet',
    engine='pyarrow',
    compression='snappy',      # Fast compression
    index=False,
    partition_cols=['year'],   # Partition by year for fast filtering
    row_group_size=100000,     # Optimize for chunk reading
)
```

#### Column Selection
```python
# Only load required columns
ESSENTIAL_COLUMNS = [
    'DTNASC', 'CODMUNNASC', 'CODMUNRES', 'IDADEMAE', 
    'GESTACAO', 'PARTO', 'PESO', 'APGAR1', 'APGAR5'
]

df = pd.read_parquet('data.parquet', columns=ESSENTIAL_COLUMNS)
```

#### Data Type Optimization
```python
# Optimize memory usage
DTYPE_MAPPING = {
    'IDADEMAE': 'int8',        # 8-bit integer (0-127)
    'GESTACAO': 'int8',
    'PESO': 'int16',           # 16-bit integer
    'CODMUNNASC': 'category',  # Categorical for repeated values
    'PARTO': 'category',
    'SEXO': 'category',
}
```

#### Brazilian Number Formatting
```python
# Settings configuration (config/settings.py)
NUMBER_FORMAT = {
    'thousands_sep': '.',      # Dots for thousands: 2.677.101
    'decimal_sep': ',',        # Commas for decimals: 28,5
}

# Implementation pattern
formatted_number = f"{total_births:_}".replace("_", ".")  # 2.677.101
formatted_decimal = f"{maternal_age:.1f}".replace(".", ",")  # 28,5 anos
```

---

## Caching Strategy

### Three-Tier Caching

#### 1. **Application-Level Cache** (In-Memory)
```python
from functools import lru_cache
from dash import dcc

# Cache expensive computations
@lru_cache(maxsize=128)
def compute_age_distribution(year: int, state: str) -> dict:
    """Compute and cache age distribution."""
    # Computation logic
    return result

# Cache in Dash Store component
dcc.Store(id='cached-data', storage_type='session')
```

#### 2. **Pre-Computed Aggregates** (Disk)
```python
# Generate aggregates during data preprocessing
def generate_aggregates(df: pd.DataFrame) -> None:
    """Generate all common aggregates."""
    
    # Monthly totals
    monthly = df.groupby([df['birth_date'].dt.to_period('M')]).size()
    monthly.to_parquet('aggregates/monthly_totals.parquet')
    
    # State-level summary
    state_summary = df.groupby('state_code').agg({
        'PESO': 'mean',
        'IDADEMAE': 'mean',
        'APGAR5': 'mean',
    })
    state_summary.to_parquet('aggregates/state_summary.parquet')
```

#### 3. **Browser-Level Cache** (LocalStorage)
```python
# Cache visualization configurations
dcc.Store(
    id='user-preferences',
    storage_type='local',  # Persists across sessions
    data={'default_year': 2024, 'default_state': 'SP'}
)
```

---

## Component Architecture

### Page Structure

#### Home Page (`pages/home.py`)
```python
layout = dbc.Container([
    # Hero section with key metrics
    dbc.Row([
        dbc.Col([metric_card('Total Births', total_births)], width=3),
        dbc.Col([metric_card('Cesarean Rate', cesarean_rate)], width=3),
        dbc.Col([metric_card('Avg Maternal Age', avg_age)], width=3),
        dbc.Col([metric_card('Avg Birth Weight', avg_weight)], width=3),
    ]),
    
    # Primary visualization
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='yearly-trend-chart')
        ])
    ]),
    
    # Secondary visualizations
    dbc.Row([
        dbc.Col([dcc.Graph(id='delivery-type-pie')], width=6),
        dbc.Col([dcc.Graph(id='maternal-age-hist')], width=6),
    ]),
])
```

#### Timeline Page (`pages/timeline.py`)
```python
layout = dbc.Container([
    # Filter controls
    dbc.Row([
        dbc.Col([
            html.Label('Date Range'),
            dcc.RangeSlider(
                id='date-range-slider',
                min=2010,
                max=2024,
                value=[2020, 2024],
                marks={i: str(i) for i in range(2010, 2025)},
            )
        ])
    ]),
    
    # Timeline visualization
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='timeline-chart', config={'displayModeBar': False})
        ])
    ]),
    
    # Data table with pagination
    dbc.Row([
        dbc.Col([
            dash_table.DataTable(
                id='timeline-table',
                page_size=50,
                page_action='custom',  # Server-side pagination
            )
        ])
    ]),
])
```

#### Geographic Page (`pages/geographic.py`)
```python
layout = dbc.Container([
    # Map controls
    dbc.Row([
        dbc.Col([
            dcc.Dropdown(
                id='map-metric-dropdown',
                options=[
                    {'label': 'Total Births', 'value': 'total_births'},
                    {'label': 'Cesarean Rate', 'value': 'cesarean_rate'},
                    {'label': 'Maternal Mortality', 'value': 'mortality'},
                ],
                value='total_births'
            )
        ], width=6),
    ]),
    
    # Choropleth map
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='brazil-map', style={'height': '600px'})
        ])
    ]),
    
    # Regional comparison
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='regional-comparison-bar')
        ])
    ]),
])
```

---

## Callback Patterns

### Pattern 1: Simple Filter Update
```python
@callback(
    Output('chart', 'figure'),
    Input('year-dropdown', 'value')
)
def update_chart(selected_year):
    """Update chart when year changes."""
    df_filtered = load_year_data(selected_year)
    fig = px.histogram(df_filtered, x='maternal_age')
    return fig
```

### Pattern 2: Multiple Inputs with State
```python
@callback(
    Output('chart', 'figure'),
    Output('loading-spinner', 'children'),
    Input('apply-filters-button', 'n_clicks'),
    State('date-range', 'value'),
    State('state-dropdown', 'value'),
    State('cached-data', 'data'),
    prevent_initial_call=True
)
def apply_filters(n_clicks, date_range, state, cached_data):
    """Apply multiple filters when button clicked."""
    # Validate inputs
    # Load/filter data
    # Update visualization
    return fig, "Updated"
```

### Pattern 3: Chained Updates
```python
@callback(
    Output('municipality-dropdown', 'options'),
    Input('state-dropdown', 'value')
)
def update_municipality_options(selected_state):
    """Update municipality options based on selected state."""
    municipalities = get_municipalities_for_state(selected_state)
    return [{'label': m, 'value': m} for m in municipalities]

@callback(
    Output('chart', 'figure'),
    Input('municipality-dropdown', 'value'),
    State('state-dropdown', 'value')
)
def update_chart(municipality, state):
    """Update chart for selected municipality."""
    # Filter and visualize
    return fig
```

### Pattern 4: Background Callback (Long Operations)
```python
from dash import DiskcacheManager, CeleryManager

# For long-running operations
@callback(
    Output('result', 'children'),
    Input('compute-button', 'n_clicks'),
    background=True,
    running=[
        (Output('compute-button', 'disabled'), True, False),
        (Output('loading-spinner', 'children'), "Computing...", ""),
    ],
    manager=DiskcacheManager(cache_by=[lambda: "compute-key"])
)
def long_computation(n_clicks):
    """Perform long computation in background."""
    # Heavy computation
    time.sleep(5)
    return "Result ready"
```

---

## Performance Optimization

### Data Loading Strategy

#### Lazy Loading
```python
class DataLoader:
    """Lazy data loader with caching."""
    
    def __init__(self):
        self._cache = {}
        
    def load_year(self, year: int, columns: list = None) -> pd.DataFrame:
        """Load year data with caching."""
        cache_key = f"{year}_{hash(tuple(columns or []))}"
        
        if cache_key not in self._cache:
            df = pd.read_parquet(
                f'data/years/{year}/complete.parquet',
                columns=columns
            )
            self._cache[cache_key] = df
            
        return self._cache[cache_key]
```

#### Chunked Reading
```python
def read_large_file_in_chunks(filepath: str, chunk_size: int = 100000):
    """Read large Parquet file in chunks."""
    parquet_file = pq.ParquetFile(filepath)
    
    for batch in parquet_file.iter_batches(batch_size=chunk_size):
        df_chunk = batch.to_pandas()
        yield df_chunk
```

### Visualization Optimization

#### Downsampling Large Datasets
```python
def create_optimized_scatter(df: pd.DataFrame, max_points: int = 10000):
    """Create scatter plot with downsampling."""
    if len(df) > max_points:
        df_sample = df.sample(n=max_points, random_state=42)
    else:
        df_sample = df
        
    fig = px.scatter(df_sample, x='maternal_age', y='birth_weight')
    return fig
```

#### WebGL for Large Visualizations
```python
fig = go.Figure(
    data=go.Scattergl(  # Use WebGL for performance
        x=df['x'],
        y=df['y'],
        mode='markers',
        marker=dict(size=2)
    )
)
```

---

## Deployment Architecture

### Render.com Deployment

#### Project Structure
```
dashboard/
├── app.py              # Main entry point
├── requirements.txt    # Python dependencies
├── Procfile           # Process definition
└── render.yaml        # Render configuration
```

#### `Procfile`
```
web: gunicorn app:server --workers 2 --threads 4 --timeout 120
```

#### `render.yaml`
```yaml
services:
  - type: web
    name: sinasc-dashboard
    env: python
    plan: free
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn app:server --workers 2 --threads 4
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
      - key: DATA_PATH
        value: ./data
```

### Memory Management
```python
import gc

@callback(...)
def expensive_operation(...):
    # Computation
    result = process_data()
    
    # Explicit garbage collection
    gc.collect()
    
    return result
```

---

## Monitoring & Logging

### Performance Monitoring
```python
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def timed_callback(func):
    """Decorator to time callback execution."""
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start
        logger.info(f"{func.__name__} took {duration:.2f}s")
        return result
    return wrapper

@callback(...)
@timed_callback
def update_chart(...):
    # Callback logic
    pass
```

### Error Tracking
```python
import traceback

@callback(...)
def safe_callback(...):
    try:
        # Callback logic
        return result
    except Exception as e:
        logger.error(f"Error in callback: {str(e)}")
        logger.error(traceback.format_exc())
        return error_layout(str(e))
```

---

## Security Considerations

### Input Validation
```python
def validate_year(year: int) -> bool:
    """Validate year input."""
    return 2010 <= year <= 2024

def validate_state_code(code: str) -> bool:
    """Validate Brazilian state code."""
    valid_codes = [str(i) for i in range(11, 54)]
    return code in valid_codes
```

### Rate Limiting (Future)
```python
from flask_limiter import Limiter

limiter = Limiter(
    app.server,
    key_func=lambda: request.remote_addr,
    default_limits=["200 per day", "50 per hour"]
)
```

---

## Testing Strategy

### Unit Tests
```python
# tests/test_data_processing.py
import pytest
from data.loader import DataLoader

def test_load_year_data():
    loader = DataLoader()
    df = loader.load_year(2024)
    assert len(df) > 0
    assert 'DTNASC' in df.columns
```

### Integration Tests
```python
# tests/test_callbacks.py
from dash.testing.application_runners import import_app

def test_filter_callback(dash_duo):
    app = import_app("app")
    dash_duo.start_server(app)
    
    # Interact with components
    dash_duo.wait_for_element("#year-dropdown").send_keys("2024")
    
    # Assert results
    assert dash_duo.find_element("#chart").is_displayed()
```

---

## Future Enhancements

### Phase 2: Advanced Features
- **Real-time updates**: WebSocket integration
- **ML predictions**: Birth weight prediction models
- **Export functionality**: PDF reports, Excel downloads
- **User authentication**: Saved dashboards, custom views
- **API endpoints**: RESTful API for data access

### Technical Debt
- Implement proper logging system
- Add comprehensive test coverage
- Set up CI/CD pipeline
- Optimize database queries
- Add monitoring/alerting

---

*Last Updated: October 3, 2025*
