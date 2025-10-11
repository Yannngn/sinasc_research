# .github/copilot-instructions.md

## Project Context

This is a **Plotly Dash web dashboard** for analyzing Brazilian perinatal health data (SINASC - Nascidos Vivos). The dashboard displays interactive visualizations, temporal trends, and geographic analysis of birth records across multiple years.

### Tech Stack
- **Framework**: Plotly Dash (Python web framework)
- **Database**: PostgreSQL with PostGIS (staging and production environments)
- **Data Processing**: Pandas, SQLAlchemy, SQL-based ETL pipeline
- **Visualization**: Plotly Express, Plotly Graph Objects
- **UI**: Dash Bootstrap Components
- **Deployment**: Docker (local), Render.com (cloud)

---

## Code Style & Conventions

### Python Style
- Follow PEP 8 style guide
- Use type hints for function parameters and returns
- Maximum line length: 120 characters
- Use descriptive variable names (avoid single letters except in loops)

### Naming Conventions
```python
# Functions: snake_case
def load_birth_data(year: int) -> pd.DataFrame:
    pass

# Classes: PascalCase
class DataAggregator:
    pass

# Constants: UPPER_SNAKE_CASE
MAX_RECORDS_PER_PAGE = 1000
DEFAULT_DATE_RANGE = (2020, 2024)

# Variables: snake_case
filtered_data = df[df['year'] == 2024]
```

### Docstring Format
Use Google-style docstrings:
```python
def filter_by_date_range(df: pd.DataFrame, start_date: str, end_date: str) -> pd.DataFrame:
    """
    Filter DataFrame by date range.
    
    Args:
        df: Input DataFrame with 'DTNASC' column
        start_date: Start date in 'YYYY-MM-DD' format
        end_date: End date in 'YYYY-MM-DD' format
        
    Returns:
        Filtered DataFrame within the specified date range
        
    Raises:
        ValueError: If date format is invalid
    """
    pass
```

---

## Dash-Specific Guidelines

### Component Structure
```python
# Organize imports by category
import dash
from dash import dcc, html, Input, Output, State, callback
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd

# Use Bootstrap components for modern UI
layout = dbc.Container([
    dbc.Row([
        dbc.Col([...], width=3),  # Sidebar
        dbc.Col([...], width=9),  # Main content
    ])
])
```

### Callback Best Practices
```python
# Use descriptive callback IDs
@callback(
    Output('births-timeline-chart', 'figure'),
    Output('loading-state', 'children'),
    Input('date-range-slider', 'value'),
    Input('state-dropdown', 'value'),
    State('current-data', 'data'),
    prevent_initial_call=False
)
def update_timeline_chart(date_range, selected_state, current_data):
    """Update timeline chart based on filters."""
    # Add loading state
    # Process data efficiently
    # Return optimized figure
    pass

# Avoid circular dependencies
# Use State for large data (not Input)
# Implement error handling
```

### Performance Optimization
```python
# Dashboard loads pre-aggregated data from database
from dashboard.data.loader import data_loader

# All queries use pre-computed aggregate tables (fast)
yearly_summary = data_loader.get_yearly_summary(year=2024)
monthly_data = data_loader.get_monthly_aggregates(year=2024)
state_data = data_loader.get_state_aggregates(year=2024)

# For SQL queries, use SQLAlchemy
from sqlalchemy import text
with engine.connect() as conn:
    result = conn.execute(text("""
        SELECT year, total_births 
        FROM agg_yearly 
        WHERE year >= 2020
    """))
    df = pd.DataFrame(result.fetchall(), columns=result.keys())
```

---

## Data Processing Guidelines

### Database Architecture
The project uses a **three-tiered database architecture**:
1. **Staging Database**: Raw data ingestion and transformation
2. **Local Production Database**: Docker container for local development
3. **Cloud Production Database**: Managed PostgreSQL for deployment

### Data Pipeline
The ETL pipeline is **SQL-centric** for memory efficiency:
1. **Staging** (`staging.py`): Ingest raw data from APIs
2. **Pipeline** (5 SQL-based steps):
   - Step 01: Select essential columns
   - Step 02: Create fact table (unified, all years)
   - Step 03: Create dimension tables
   - Step 04: Engineer features (boolean indicators)
   - Step 05: Create aggregations (pre-computed summaries)
3. **Promotion** (`promote.py`): Copy to production database

### Column Name Conventions
- **Original SINASC columns**: Keep uppercase (e.g., `DTNASC`, `IDADEMAE`)
- **Engineered features**: Use descriptive snake_case (e.g., `is_preterm`, `is_cesarean`)
- **Aggregate tables**: Prefix with `agg_` (e.g., `agg_yearly`, `agg_monthly`)
- **Dimension tables**: Prefix with `dim_` (e.g., `dim_maternal_age_group`)
- **Fact tables**: Prefix with `fact_` (e.g., `fact_births`)

### Data Loading Pattern
```python
# Dashboard loads data from PostgreSQL, not Parquet files
from dashboard.data.loader import data_loader

# Get available years
years = data_loader.get_available_years()

# Load yearly summary (from agg_yearly table)
yearly_data = data_loader.get_yearly_summary(year=2024)

# Load monthly aggregates
monthly_data = data_loader.get_monthly_aggregates(year=2024)
```

### SQL-Based Transformations
```python
# Prefer SQL for heavy operations
from sqlalchemy import text

with engine.connect() as conn:
    # Create aggregations in SQL
    conn.execute(text("""
        CREATE TABLE agg_yearly AS
        SELECT 
            year,
            COUNT(*) as total_births,
            AVG(PESO) as avg_birth_weight
        FROM fact_births
        GROUP BY year
    """))
```

---

## Visualization Guidelines

### Chart Design Principles
1. **Clarity**: Clear titles, axis labels, and legends
2. **Consistency**: Use consistent colors across charts
3. **Accessibility**: Colorblind-friendly palettes
4. **Interactivity**: Enable hover tooltips, click interactions
5. **Responsiveness**: Charts adapt to screen size

### Color Palette
```python
# Define consistent color scheme
COLOR_PALETTE = {
    'primary': '#1f77b4',      # Blue
    'secondary': '#ff7f0e',    # Orange
    'success': '#2ca02c',      # Green
    'danger': '#d62728',       # Red
    'warning': '#ffbb00',      # Yellow
    'info': '#17becf',         # Cyan
    'neutral': '#7f7f7f',      # Gray
}

# Use for categorical data
DELIVERY_TYPE_COLORS = {
    'Vaginal': COLOR_PALETTE['primary'],
    'Cesarean': COLOR_PALETTE['secondary'],
}
```

### Chart Templates
```python
# Use consistent template
fig = px.histogram(
    df, x='maternal_age', 
    title='Maternal Age Distribution',
    template='plotly_white',  # Clean, modern look
    color_discrete_sequence=[COLOR_PALETTE['primary']]
)

# Add consistent styling
fig.update_layout(
    font_family='Arial, sans-serif',
    title_font_size=20,
    hoverlabel=dict(bgcolor='white', font_size=12),
    margin=dict(l=40, r=40, t=60, b=40),
)
```

### Map Visualizations
```python
# Use Brazilian geographic data
fig = px.choropleth(
    df_by_state,
    geojson=brazil_geojson,
    locations='state_code',
    featureidkey='properties.id',
    color='birth_count',
    color_continuous_scale='Viridis',
    title='Births by State',
)

fig.update_geos(
    center=dict(lat=-14.2350, lon=-51.9253),  # Brazil center
    projection_scale=3.5,
    visible=False,
)
```

---

## File Organization

### Module Structure
```
dashboard/
├── app.py                    # Main application entry point
├── components/               # Reusable UI components
│   ├── __init__.py
│   ├── cards.py             # Metric display cards
│   ├── charts.py            # Chart generation functions
│   └── geo_charts.py        # Geographic visualizations
├── pages/                    # Multi-page app
│   ├── __init__.py
│   ├── home.py              # Landing page
│   ├── annual.py            # Annual analysis
│   └── geographic.py        # Geographic analysis
├── data/                     # Data processing & ETL
│   ├── __init__.py
│   ├── database.py          # Database connections
│   ├── loader.py            # Dashboard data loading (SQL queries)
│   ├── staging.py           # Raw data ingestion from APIs
│   ├── optimize.py          # Data type optimization
│   ├── promote.py           # Staging → Production promotion
│   ├── pandas/              # Pandas-based fallback scripts
│   │   ├── optimize.py
│   │   └── promote.py
│   └── pipeline/            # SQL-based transformation pipeline
│       ├── README.md        # Pipeline documentation
│       ├── run_all.py       # Orchestrate all steps
│       ├── step_01_select.py    # Select essential columns
│       ├── step_02_create.py    # Create fact table
│       ├── step_03_bin.py       # Create dimension tables
│       ├── step_04_engineer.py  # Engineer features
│       └── step_05_aggregate.py # Create aggregations
├── config/                   # Configuration
│   ├── __init__.py
│   ├── settings.py          # App settings
│   ├── constants.py         # Constants and mappings
│   └── geographic.py        # Geographic data configurations
└── assets/                   # Static files
    └── styles.css           # Custom CSS
```

---

## Performance Requirements

### Memory Constraints
- **Target**: <512MB RAM usage (free tier hosting)
- **Strategy**: Pre-aggregated database tables, SQL queries, no large DataFrames in memory
- **Monitoring**: Profile memory usage during development

### Load Time Targets
- **Initial page load**: <3 seconds
- **Chart updates**: <1 second
- **Map rendering**: <2 seconds

### Optimization Techniques
```python
# 1. Use pre-aggregated tables (already computed in pipeline)
# Dashboard queries agg_* tables, not fact_births (27M rows)
df = data_loader.get_yearly_summary(year=2024)  # Small, pre-computed

# 2. Use SQL for filtering and aggregation
from sqlalchemy import text
with engine.connect() as conn:
    df = pd.read_sql(text("""
        SELECT year, state_code, total_births
        FROM agg_state_yearly
        WHERE year >= 2020
    """), conn)

# 3. Fact table (fact_births) stays in staging database
# Production database only has dim_* and agg_* tables (<500MB)

# 4. Pipeline creates all aggregations in SQL (memory-efficient)
# See: dashboard/data/pipeline/step_05_aggregate.py
```

---

## Testing Guidelines

### Test Data
```python
# Create small test dataset
def create_test_data(n_records: int = 1000) -> pd.DataFrame:
    """Generate synthetic test data for development."""
    return pd.DataFrame({
        'DTNASC': pd.date_range('2024-01-01', periods=n_records, freq='h'),
        'IDADEMAE': np.random.randint(15, 45, n_records),
        'PESO': np.random.normal(3200, 500, n_records),
        # ... other columns
    })
```

### Unit Tests
```python
# Test data processing functions
def test_filter_by_date_range():
    df = create_test_data()
    result = filter_by_date_range(df, '2024-01-01', '2024-01-31')
    assert len(result) <= len(df)
    assert result['birth_date'].min() >= pd.to_datetime('2024-01-01')
```

---

## Deployment Checklist

### Pre-Deployment
- [ ] Test with production data size
- [ ] Profile memory usage (<512MB)
- [ ] Optimize data files
- [ ] Test on mobile devices
- [ ] Add error handling
- [ ] Set up monitoring

### Requirements File
```txt
# dashboard/requirements.txt
dash==2.14.2
dash-bootstrap-components==1.5.0
plotly==5.18.0
pandas==2.1.4
pyarrow==14.0.1
gunicorn==21.2.0  # For deployment
```

### Environment Variables
```python
# config/settings.py
import os

DEBUG = os.getenv('DEBUG', 'False') == 'True'
DATA_PATH = os.getenv('DATA_PATH', '../data/SINASC')
MAX_RECORDS = int(os.getenv('MAX_RECORDS', 100000))
```

---

## Common Patterns

### Loading State
```python
# Add loading component
dcc.Loading(
    id='loading-chart',
    type='default',  # or 'circle', 'dot', 'cube'
    children=dcc.Graph(id='main-chart')
)
```

### Error Handling
```python
@callback(...)
def update_chart(...):
    try:
        # Process data
        fig = create_chart(data)
        return fig
    except Exception as e:
        # Return error message as chart
        return {
            'layout': {
                'xaxis': {'visible': False},
                'yaxis': {'visible': False},
                'annotations': [{
                    'text': f'Error loading data: {str(e)}',
                    'showarrow': False,
                }]
            }
        }
```

### Pagination
```python
# Implement server-side pagination
@callback(
    Output('data-table', 'data'),
    Input('page-number', 'value'),
    Input('page-size', 'value'),
)
def paginate_data(page, page_size):
    start = page * page_size
    end = start + page_size
    return df.iloc[start:end].to_dict('records')
```

---

## Security & Privacy

### Data Privacy
- No personally identifiable information (PII) in dashboard
- Aggregate data only (no individual records shown)
- Comply with Brazilian data protection laws (LGPD)

### Input Validation
```python
def validate_date_range(start: str, end: str) -> bool:
    """Validate date range inputs."""
    try:
        start_date = pd.to_datetime(start)
        end_date = pd.to_datetime(end)
        return start_date <= end_date
    except:
        return False
```

---

## Code Review Checklist

Before committing:
- [ ] Code follows PEP 8 style
- [ ] Functions have docstrings
- [ ] No hardcoded paths (use config)
- [ ] Error handling implemented
- [ ] Performance optimized (profiled)
- [ ] Mobile-responsive design tested
- [ ] Comments explain complex logic
- [ ] No debug print statements left

---

## Resources & References

### Documentation
- [Dash Documentation](https://dash.plotly.com/)
- [Plotly Python](https://plotly.com/python/)
- [Pandas Best Practices](https://pandas.pydata.org/docs/user_guide/index.html)

### SINASC Data Dictionary
- [DATASUS Documentation](http://tabnet.datasus.gov.br/cgi/sinasc/nvdescr.htm)
- [SINASC Variables](http://svs.aids.gov.br/dantps/centrais-de-conteudos/paineis-de-monitoramento/natalidade/nascidos-vivos/)

---

*These instructions help GitHub Copilot provide context-aware suggestions for this project.*
