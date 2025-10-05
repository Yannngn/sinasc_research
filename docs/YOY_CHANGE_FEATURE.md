# Year-over-Year Change Feature

## Overview

Added year-over-year (YoY) percentage change indicators to metric cards in the Annual Analysis page.

## Visual Design

Each metric card now displays a small badge in the **top-right corner** showing the percentage change from the previous year:

```
┌─────────────────────────────┐
│                    [+5.2%] ↗│  ← Badge with % change
│         👶                   │
│      2.834.567              │
│   Nascimentos Totais        │
└─────────────────────────────┘
```

## Badge Colors

The badge color indicates whether the change is positive, negative, or neutral:

- **Green** (success) with ↗ arrow: Positive change (+)
- **Red** (danger) with ↘ arrow: Negative change (-)
- **Gray** (secondary) with — symbol: No change (0%)

## Implementation Details

### 1. Enhanced `create_metric_card()` Function

**File**: `dashboard/components/cards.py`

**New Parameter**:
```python
def create_metric_card(
    title: str,
    value: str,
    icon: str,
    color: str = "primary",
    yoy_change: float | None = None,  # ← New parameter
) -> dbc.Card:
```

**Features**:
- Accepts optional `yoy_change` parameter (e.g., `5.2` for +5.2%, `-3.1` for -3.1%)
- Automatically determines badge color based on sign
- Uses Brazilian number formatting (comma as decimal separator)
- Positioned absolutely in top-right corner
- Small font size (10px) to avoid cluttering the card

### 2. Updated `create_year_summary()` Function

**File**: `dashboard/pages/annual.py`

**Changes**:
- Checks if previous year data is available
- Calculates YoY percentage change for each metric
- Passes `yoy_change` parameter to each card

**Helper Function**:
```python
def calculate_yoy_change(current_value: float, prev_value: float | None) -> float | None:
    """Calculate percentage change from previous year."""
    if prev_value is None or prev_value == 0:
      return None
    return ((current_value - prev_value) / prev_value) * 100
```

## Metrics with YoY Indicators

All 8 metric cards on the Annual Analysis page now show YoY changes:

1. **Nascimentos Totais** (Total Births)
2. **Taxa de Cesáreas** (Cesarean Rate)
3. **Taxa de Gestações Abaixo de 20 anos** (Teen Pregnancy Rate)
4. **Taxa de Gestações Abaixo de 15 anos** (Very Young Pregnancy Rate)
5. **Taxa de Baixo Peso ao Nascer** (Low Birth Weight Rate)
6. **Taxa de Prematuridade** (Preterm Birth Rate)
7. **Taxa de Nascimentos em Hospital** (Hospital Birth Rate)
8. **Taxa de APGAR5 Baixo** (Low APGAR5 Rate)

## Examples

### Positive Change (Green Badge)
```
┌─────────────────────────────┐
│                    [+3.8%] ↗│
│         🏥                   │
│        98,5%                │
│ Taxa de Nascimentos Hospital│
└─────────────────────────────┘
```
*Hospital births increased by 3.8% compared to previous year*

### Negative Change (Red Badge)
```
┌─────────────────────────────┐
│                    [-2.4%] ↘│
│         👶                   │
│      2.734.123              │
│   Nascimentos Totais        │
└─────────────────────────────┘
```
*Total births decreased by 2.4% compared to previous year*

### No Previous Year Data
```
┌─────────────────────────────┐
│                             │  ← No badge shown
│         👶                   │
│      2.834.567              │
│   Nascimentos Totais        │
└─────────────────────────────┘
```
*First year in dataset - no comparison available*

## Edge Cases Handled

1. **No Previous Year**: Badge not displayed if comparing first year in dataset
2. **Zero Previous Value**: Returns `None` to avoid division by zero
3. **Exact Match**: Shows "0,0%" with gray badge and minus symbol
4. **Brazilian Formatting**: Uses comma as decimal separator (e.g., "5,2%" not "5.2%")

## User Benefits

- **Quick Trend Identification**: Users can instantly see if metrics are improving or worsening
- **Year-over-Year Context**: Provides temporal context without cluttering the main value
- **Visual Clarity**: Color coding makes it easy to spot concerning trends
- **Minimal UI Impact**: Small badge doesn't interfere with primary metric display

## Technical Notes

### CSS Classes Used
- `position-absolute` - Absolute positioning for badge
- `top-0 end-0 m-2` - Top-right corner with 2-unit margin
- `badge bg-{color}` - Bootstrap badge styling
- `position-relative` - Parent card for absolute positioning context

### Icon Classes
- `fas fa-arrow-up` - Up arrow for positive change
- `fas fa-arrow-down` - Down arrow for negative change
- `fas fa-minus` - Minus symbol for no change

### Bootstrap Colors
- `bg-success` - Green for positive changes
- `bg-danger` - Red for negative changes
- `bg-secondary` - Gray for zero change

## Future Enhancements

1. **Tooltip with Details**: Hover tooltip showing absolute values
   ```python
   title=f"Previous year: {prev_value:.1f}% | Current: {current_value:.1f}%"
   ```

2. **Multi-Year Trends**: Show 3-year trend arrow (↗↗, ↗→, etc.)

3. **Threshold Warnings**: Highlight concerning trends (e.g., >10% increase in cesarean rate)

4. **Customizable Interpretation**: Some metrics are "good" when increasing (hospital births), others are "bad" (cesarean rate) - could adjust badge colors accordingly

5. **Export to Reports**: Include YoY changes in downloadable summary reports

---

## Code Quality

✅ **Type Hints**: All functions properly typed  
✅ **Documentation**: Comprehensive docstrings  
✅ **Error Handling**: Null checks for missing data  
✅ **Brazilian Standards**: Comma decimal separators  
✅ **Accessibility**: Color + icon for colorblind users  
✅ **Responsive Design**: Works on mobile and desktop  

---

*Feature completed: 2024-01-14*  
*Dashboard Status*: 🟢 Running with hot-reload enabled
