# .github/copilot-instructions.md

## Project Context

This is a **Plotly Dash web dashboard** for analyzing Brazilian perinatal health data (SINASC - Nascidos Vivos). The dashboard displays interactive visualizations, temporal trends, and geographic analysis of birth records across multiple years.

### Tech Stack
- **Framework**: Plotly Dash (Python web framework)
- **Data**: Pandas, PyArrow (Parquet files)
- **Visualization**: Plotly Express, Plotly Graph Objects
- **UI**: Dash Bootstrap Components
- **Deployment**: Free tier hosting (Render.com/Hugging Face Spaces)

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
# Cache expensive computations
from functools import lru_cache

@lru_cache(maxsize=128)
def load_aggregated_data(year: int) -> pd.DataFrame:
    """Load pre-aggregated data for a specific year."""
    pass

# Use efficient data types
df['maternal_age'] = df['IDADEMAE'].astype('Int8')
df['state_code'] = df['CODMUNNASC'].astype('category')

# Limit data in callbacks
df_sample = df.head(10000)  # For initial load
```

---

## Data Processing Guidelines

### Column Name Conventions
- **Original SINASC columns**: Keep uppercase (e.g., `DTNASC`, `IDADEMAE`)
- **Engineered features**: Use descriptive snake_case (e.g., `maternal_age_group`, `is_preterm`)
- **Aggregated columns**: Prefix with `agg_` (e.g., `agg_births_total`, `agg_cesarean_rate`)

### Handling Missing Data
```python
# Document missing value codes
MISSING_VALUE_CODES = {
    'IDADEMAE': [0, 99],
    'ESCMAE': [9],
    'ESTCIVMAE': [9],
}

# Replace with pd.NA for consistency
df['IDADEMAE'] = df['IDADEMAE'].replace(MISSING_VALUE_CODES['IDADEMAE'], pd.NA)
```

### Date Handling
```python
# Convert DTNASC to datetime
df['birth_date'] = pd.to_datetime(df['DTNASC'], format='%d%m%Y', errors='coerce')
df['birth_year'] = df['birth_date'].dt.year
df['birth_month'] = df['birth_date'].dt.month
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
│   ├── filters.py           # Filter controls (sliders, dropdowns)
│   ├── cards.py             # Metric display cards
│   ├── charts.py            # Chart generation functions
│   └── maps.py              # Map visualization functions
├── pages/                    # Multi-page app
│   ├── __init__.py
│   ├── home.py              # Landing page
│   ├── timeline.py          # Temporal analysis
│   ├── geographic.py        # Geographic analysis
│   └── insights.py          # Deep-dive insights
├── data/                     # Data processing
│   ├── __init__.py
│   ├── loader.py            # Data loading utilities
│   ├── aggregator.py        # Pre-aggregation functions
│   └── cache.py             # Caching mechanisms
├── config/                   # Configuration
│   ├── __init__.py
│   ├── settings.py          # App settings
│   └── constants.py         # Constants and mappings
└── assets/                   # Static files
    ├── styles.css           # Custom CSS
    └── favicon.ico          # App icon
```

---

## Performance Requirements

### Memory Constraints
- **Target**: <512MB RAM usage (free tier hosting)
- **Strategy**: Lazy loading, pagination, pre-aggregation
- **Monitoring**: Profile memory usage during development

### Load Time Targets
- **Initial page load**: <3 seconds
- **Chart updates**: <1 second
- **Map rendering**: <2 seconds

### Optimization Techniques
```python
# 1. Load only required columns
columns_needed = ['DTNASC', 'IDADEMAE', 'PESO', 'GESTACAO']
df = pd.read_parquet('data.parquet', columns=columns_needed)

# 2. Use categorical dtypes
df['state'] = df['state'].astype('category')

# 3. Downsample for visualizations
df_sample = df.sample(frac=0.1) if len(df) > 100000 else df

# 4. Pre-aggregate common queries
monthly_aggregates = df.groupby(['year', 'month']).size().reset_index()
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
