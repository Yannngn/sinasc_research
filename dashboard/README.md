# SINASC Dashboard - Brazilian Perinatal Health Analytics

## 📋 Project Overview

A modern, interactive web dashboard for analyzing Brazilian perinatal health data (SINASC - Sistema de Informações sobre Nascidos Vivos). Built with Plotly Dash for deployment on GitHub Pages and free hosting platforms.

### Purpose
- Provide public health insights on Brazilian births
- Enable temporal and geographic analysis
- Support data-driven decision making in maternal and child health
- Portfolio showcase for data visualization and web development

---

## 🎯 Core Features

### 1. **Multi-Year Overview (2019-2024)**
- 5 years of data: 10,036,633 birth records
- Year summary cards with 6 key metrics per year
- Brazilian number formatting (dots for thousands, commas for decimals)
- Compact inline layout for easy scanning
- Shows last 3 years by default

### 2. **Enhanced Key Metrics**
- 📊 Total births with evolution bar chart
- 👶 Maternal age and birth weight trends
- 🏥 Cesarean rate comparison (vaginal vs cesarean)
- ⚠️ Preterm births analysis (total + extreme <32 weeks)
- 👧 Adolescent pregnancy tracking (total + very young <15 years)
- 💯 APGAR 5 scores
- 🏥 Hospital births percentage

### 3. **Advanced Visualizations**
- **Stacked Bar Charts**: Preterm births and adolescent pregnancies with inside/outside text labels
- **Dual-Line Charts**: Total vs extreme categories with WHO reference lines
- **Bar Charts**: Birth evolution with Brazilian formatted text labels
- **Comparison Charts**: Cesarean rates across years
- **Optimized Layout**: No redundant titles, centralized configuration

### 4. **Performance Optimizations**
- Pre-aggregated data files (yearly.parquet: 12.5KB for 5 years)
- LRU caching for expensive computations
- Lazy loading with pagination
- Efficient Parquet compression
- Brazilian number formatting throughout

---

## 🏗️ Architecture

### Technology Stack
- **Framework**: Plotly Dash (Python)
- **Data Processing**: Pandas, PyArrow
- **Visualization**: Plotly Express, Plotly Graph Objects
- **Storage**: Parquet files (optimized for web)
- **Deployment**: Render.com / Hugging Face Spaces (free tier)

### Project Structure
```
dashboard/
├── README.md                 # This file
├── ARCHITECTURE.md           # Detailed architecture documentation
├── app.py                    # Main Dash application
├── pages/                    # Multi-page app structure
│   ├── home.py              # Overview/landing page
│   ├── timeline.py          # Temporal analysis
│   ├── geographic.py        # Maps and regional analysis
│   └── insights.py          # Deep-dive analytics
├── components/               # Reusable UI components
│   ├── filters.py           # Filter controls
│   ├── cards.py             # Metric cards
│   ├── charts.py            # Chart components
│   └── maps.py              # Map components
├── data/                     # Data processing utilities
│   ├── loader.py            # Efficient data loading
│   ├── aggregator.py        # Pre-aggregation for web
│   └── cache.py             # Caching strategies
├── assets/                   # Static files
│   ├── styles.css           # Custom CSS
│   └── logo.png             # Branding
├── config/                   # Configuration files
│   ├── settings.py          # App settings
│   └── constants.py         # Constants and mappings
└── requirements.txt          # Python dependencies
```

---

## 📊 Data Strategy

### Performance Optimization
Given the large dataset size, we implement several optimization strategies:

1. **Pre-Aggregation**
   - Monthly/yearly summaries
   - State/region aggregates
   - Common query results cached

2. **Lazy Loading**
   - Load only visible data ranges
   - Paginate large result sets
   - Server-side filtering

3. **Data Compression**
   - Parquet format with compression
   - Categorical dtypes for string columns
   - Efficient integer types (Int8, Int16, Int32)

4. **Smart Caching**
   - Cache filtered results
   - Memoize expensive computations
   - Session-based state management

### Multi-Year Support
- **5 Years**: 2019-2024 (10,036,633 records total)
- **Unified Schema**: Consistent columns across all years
- **Yearly Aggregates**: yearly.parquet with 23 metrics per year
- **Monthly Granularity**: monthly_{year}.parquet for temporal analysis
- **State-Level**: state_{year}.parquet for geographic analysis
- **New Metrics**: 
  - `extreme_preterm_birth_pct` (GESTACAO < 3, <32 weeks): 0.55-0.61%
  - `very_young_pregnancy_pct` (IDADEMAE < 13): 0.019-0.028%
  - `preterm_birth_count` and `extreme_preterm_birth_count`
  - `adolescent_pregnancy_count` and `very_young_pregnancy_count`

---

## 🎨 UI/UX Design Principles

### Modern Dashboard Design
- **Clean Layout**: Card-based metric displays
- **Responsive**: Mobile-friendly design
- **Interactive**: Hover tooltips, click interactions
- **Accessible**: WCAG compliance, screen reader support
- **Performance**: Loading skeletons, progress indicators

### Color Scheme
- Primary: Blues and teals (healthcare theme)
- Accent: Orange/amber for highlights
- Neutral: Grays for backgrounds
- Semantic: Red/yellow/green for health indicators

### Component Hierarchy
```
Layout
├── Header (Logo, Title, Navigation)
├── Filters Sidebar (Collapsible)
│   ├── Date Range Slider
│   ├── Geographic Filters
│   ├── Demographic Filters
│   └── Apply/Reset Buttons
├── Main Content Area
│   ├── Key Metrics Cards (4-6 cards)
│   ├── Primary Visualization (Large chart/map)
│   ├── Secondary Visualizations (2-3 smaller charts)
│   └── Data Table (Paginated)
└── Footer (Credits, Data source, GitHub link)
```

---

## 🚀 Deployment Strategy

### Free Hosting Options

#### Option 1: Render.com (Recommended)
- **Pros**: 512MB RAM, automatic deploys, custom domain
- **Cons**: Cold starts after inactivity
- **Setup**: Connect GitHub repo, deploy from `dashboard/` folder

#### Option 2: Hugging Face Spaces
- **Pros**: ML community, easy sharing, persistent
- **Cons**: 16GB storage limit
- **Setup**: Create Space, push Dash app

#### Option 3: PythonAnywhere
- **Pros**: Always-on free tier
- **Cons**: Limited resources (512MB RAM)
- **Setup**: Manual deployment

### Deployment Checklist
- [ ] Optimize data files (<100MB total)
- [ ] Configure environment variables
- [ ] Set up requirements.txt
- [ ] Test on free tier limits
- [ ] Configure custom domain (optional)
- [ ] Set up monitoring/analytics

---

## 📈 Key Metrics to Display

### Maternal Health
- Age distribution
- Education levels
- Marital status
- Prenatal care consultations
- Occupation categories

### Delivery Characteristics
- Delivery type (Normal vs Cesarean)
- Gestational weeks distribution
- Place of birth (hospital, home, etc.)
- Delivery presentation
- Labor complications

### Newborn Health
- Birth weight distribution
- APGAR scores (1min, 5min)
- Sex distribution
- Race/ethnicity
- Congenital anomalies

### Geographic Insights
- Births by state/region
- Urban vs rural patterns
- Migration patterns (birth vs residence)
- Healthcare access indicators

---

## 🔧 Development Workflow

### Local Development
```bash
# Activate virtual environment
source .venv/bin/activate

# Install dependencies
pip install -r dashboard/requirements.txt

# Run development server
python dashboard/app.py
```

### Testing Data Loading
```bash
# Test with small dataset first
python dashboard/data/loader.py --test

# Profile memory usage
python -m memory_profiler dashboard/app.py
```

### Performance Monitoring
- Track page load times
- Monitor memory usage
- Log user interactions
- A/B test visualizations

---

## 📚 Data Dictionary

### Key Columns
- `DTNASC`: Birth date
- `CODMUNNASC`: Municipality code (birth location)
- `CODMUNRES`: Municipality code (residence)
- `IDADEMAE`: Maternal age
- `ESTCIVMAE`: Maternal marital status
- `ESCMAE`: Maternal education
- `QTDGESTANT`: Number of previous pregnancies
- `GESTACAO`: Gestational weeks
- `GRAVIDEZ`: Pregnancy type (single, twins, etc.)
- `PARTO`: Delivery type
- `PESO`: Birth weight (grams)
- `APGAR1`: APGAR score at 1 minute
- `APGAR5`: APGAR score at 5 minutes
- `SEXO`: Newborn sex
- `RACACOR`: Newborn race/ethnicity

### Engineered Features
- `IDADEMAEBIN`: Binned maternal age
- `PESOBIN`: Binned birth weight categories
- `SEMAGESTAC`: Gestational weeks categories
- `TPROBSON`: Robson classification
- `KOTELCHUCK`: Prenatal care adequacy index

---

## 🎓 Learning Resources

### Dash Documentation
- [Dash Overview](https://dash.plotly.com/)
- [Dash Layout](https://dash.plotly.com/layout)
- [Dash Callbacks](https://dash.plotly.com/basic-callbacks)
- [Dash Bootstrap Components](https://dash-bootstrap-components.opensource.faculty.ai/)

### Plotly Visualization
- [Plotly Express](https://plotly.com/python/plotly-express/)
- [Plotly Maps](https://plotly.com/python/maps/)
- [Plotly Time Series](https://plotly.com/python/time-series/)

### Performance Optimization
- [Dash Performance](https://dash.plotly.com/performance)
- [Pandas Performance](https://pandas.pydata.org/docs/user_guide/enhancingperf.html)

---

## 🤝 Contributing

This is a portfolio project, but suggestions are welcome!

### Development Guidelines
- Follow PEP 8 style guide
- Add docstrings to functions
- Write unit tests for data processing
- Document complex visualizations
- Optimize for performance

---

## 📄 License & Data Source

### Data Source
- **DATASUS**: Brazilian Ministry of Health
- **Dataset**: SINASC (Sistema de Informações sobre Nascidos Vivos)
- **Public Domain**: Open data for research and analysis

### Project License
- Code: MIT License
- Data: Public domain (DATASUS)

---

## 🔮 Future Enhancements

### Phase 2 Features
- [ ] Machine learning predictions (birth weight, preterm risk)
- [ ] Advanced statistical tests
- [ ] Downloadable reports (PDF/Excel)
- [ ] User accounts for saved filters
- [ ] Real-time data updates (when available)
- [ ] Mobile app version
- [ ] API for data access
- [ ] Integration with other health datasets

### Visualization Ideas
- Animated temporal maps
- 3D surface plots for multi-variable analysis
- Sankey diagrams for patient flow
- Network graphs for regional connections
- Heatmaps for correlation analysis

---

## 📞 Contact & Links

- **GitHub Repository**: [sinasc-dashboard](https://github.com/Yannngn/sinasc-dashboard)
- **Live Demo**: [To be deployed]
- **Portfolio**: [Your portfolio link]
- **LinkedIn**: [Your LinkedIn]

---

*Last Updated: October 3, 2025*
