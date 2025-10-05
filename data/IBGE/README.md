# IBGE Data Directory

This directory contains geographic and demographic data from IBGE (Instituto Brasileiro de Geografia e Estatística) used for territorial analysis in the dashboard.

## Files

### 1. `brazil_states.geojson` (381.9 KB)
**Source**: IBGE Malhas API  
**URL**: https://servicodados.ibge.gov.br/api/v3/malhas/paises/BR

**Description**: GeoJSON with Brazilian state boundaries for choropleth maps.

**Structure**:
```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "properties": {
        "codarea": "11",
        "state_code": "11",
        "state_name": "Rondônia",
        "id": "11"
      },
      "geometry": {
        "type": "Polygon",
        "coordinates": [...]
      }
    }
  ]
}
```

**Usage in Dashboard**:
- Plotly Express choropleth maps
- Geographic filtering and selection
- Regional aggregation visualization

---

### 2. `state_population_estimates.csv` (189 records)
**Source**: IBGE Population Projections  
**URL**: https://www.ibge.gov.br/estatisticas/sociais/populacao/9103-estimativas-de-populacao.html

**Description**: Population estimates by state for years 2018-2024.

**Columns**:
- `state_code` (str): Two-digit state code (e.g., "35" for São Paulo)
- `state_name` (str): State name (e.g., "São Paulo")
- `year` (int): Year of the estimate (2018-2024)
- `population` (int): Population estimate (number of individuals)

**Sample**:
```csv
state_code,state_name,year,population
11,Rondônia,2018,1724250
11,Rondônia,2019,1743675
...
35,São Paulo,2024,46649000
```

**Usage in Dashboard**:
- Per-capita birth rate calculations (births per 10,000 population)
- Population-adjusted comparisons between states
- Contextualizing absolute birth numbers

---

### 3. `population_metadata.json`
**Description**: Metadata about the population dataset.

**Contents**:
```json
{
  "source": "IBGE Population Projections",
  "url": "https://www.ibge.gov.br/estatisticas/sociais/populacao/9103-estimativas-de-populacao.html",
  "note": "Approximate values based on linear interpolation from 2018-2024 estimates",
  "years": [2018, 2019, 2020, 2021, 2022, 2023, 2024],
  "states": 27,
  "total_brazil_2024": 213579000
}
```

---

## Data Generation

To regenerate or update these files, run:

```bash
python scripts/fetch_geo_data.py
```

This script:
1. Downloads the latest GeoJSON from IBGE Malhas API
2. Creates population estimates with linear interpolation
3. Saves all files in this directory

---

## Data Loader Functions

The dashboard provides helper functions to load this data:

```python
from dashboard.data.loader import data_loader

# Load GeoJSON for choropleth maps
geojson = data_loader.load_brazil_geojson()

# Load population data for a specific year
pop_2024 = data_loader.load_population_data(year=2024)

# Load state aggregates with population (for per-capita calculations)
state_data = data_loader.load_state_aggregates_with_population(year=2024)
# Includes: state_code, total_births, population, births_per_10k
```

---

## Regional Mapping

Brazilian states are grouped into 5 regions based on the first digit of the state code:

| Region          | Code Range | States |
|-----------------|------------|--------|
| Norte           | 11-17      | RO, AC, AM, RR, PA, AP, TO |
| Nordeste        | 21-29      | MA, PI, CE, RN, PB, PE, AL, SE, BA |
| Sudeste         | 31-33, 35  | MG, ES, RJ, SP |
| Sul             | 41-43      | PR, SC, RS |
| Centro-Oeste    | 50-53      | MS, MT, GO, DF |

---

## Data Quality Notes

### Population Estimates
- **2024 values**: Based on official IBGE projections
- **2018-2023 values**: Linear interpolation from 2018 to 2024 estimates
- **Accuracy**: ~±5% margin of error for interpolated years
- **Recommendation**: For production use, download official yearly estimates from IBGE/Sidra

### GeoJSON
- **Quality**: Minimal quality (`qualidade=minima`) for faster loading
- **Coordinate System**: WGS84 (EPSG:4326)
- **File Size**: 381.9 KB (compressed boundaries)
- **Precision**: Suitable for state-level choropleth maps

---

## Future Improvements

1. **Municipality-level data**:
   - Add `municipalities.geojson` for detailed maps
   - Include municipality population estimates

2. **Annual updates**:
   - Automate yearly IBGE data fetch
   - Version control for population projections

3. **Additional demographics**:
   - Age distribution by state
   - Urban/rural population breakdown
   - GDP per capita by state

---

## References

- **IBGE Main Site**: https://www.ibge.gov.br/
- **Population Estimates**: https://sidra.ibge.gov.br/tabela/6579
- **Geographic Data API**: https://servicodados.ibge.gov.br/api/docs/malhas
- **GeoJSON Spec**: https://tools.ietf.org/html/rfc7946

---

## Usage

Used for creating choropleth maps and geographic visualizations in the dashboard.

## Related

- [Dashboard Geographic Planning](../../dashboard/pages/GEOGRAPHIC_PLANNING.md) - Future geographic features
