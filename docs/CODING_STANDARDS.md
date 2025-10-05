# SINASC Scripts - Coding Standards

## Overview
All scripts in this project follow consistent conventions for documentation, structure, and output formatting.

---

## Module Documentation

### Module Docstring Format
Every script must have a comprehensive module-level docstring:

```python
"""
Brief description of script purpose.

Detailed explanation of what the script does, including:
- Main functionality
- Key operations performed
- Expected inputs/outputs

Usage:
    python script_name.py 2024
    python script_name.py 2024 --arg value
    python script_name.py --all
"""
```

### Function Docstring Format (Google Style)
All functions must have docstrings following Google style:

```python
def function_name(param1: type, param2: type) -> return_type:
    """
    Brief description of function.
    
    More detailed explanation if needed. Can span
    multiple lines.
    
    Args:
        param1: Description of first parameter
        param2: Description of second parameter
        
    Returns:
        Description of return value
        
    Raises:
        ErrorType: When and why it's raised (if applicable)
    """
    pass
```

---

## Code Structure

### Standard Imports Order
1. Standard library imports
2. Third-party imports
3. Local imports

```python
# Standard library
import argparse
import json
import os
from pathlib import Path

# Third-party
import pandas as pd
import numpy as np

# Local
from read_file import load_data
from clean_file import optimize_data_types
```

### Configuration Constants
Place at module level, after imports, before functions:

```python
# Default configuration
DIR = "data/SINASC"
YEAR = 2024
DATASET = "complete"
```

### Main Function Structure
Every script must have a `main()` function with this structure:

```python
def main():
    """Main execution function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Brief description")
    parser.add_argument("year", type=int, default=YEAR, help="Year to process")
    parser.add_argument("--data_dir", default=DIR, help="Data directory")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing data")
    args = parser.parse_args()
    
    # Define paths
    input_path = os.path.join(args.data_dir, str(args.year), f"{args.dataset}.parquet")
    output_path = os.path.join(args.data_dir, str(args.year), "output.parquet")
    
    # Header
    print(f"\n{'=' * 60}")
    print(f"Script Name: {args.year}")
    print(f"{'=' * 60}\n")
    
    # Load data
    print(f"📥 Loading data from {input_path}...")
    df = pd.read_parquet(input_path)
    print(f"  ✅ Loaded {len(df):,} records\n")
    
    # Process data
    df_processed = process_function(df)
    
    # Save results
    print(f"\n💾 Saving data to {output_path}...")
    df_processed.to_parquet(output_path)
    print("  ✅ Saved successfully\n")


if __name__ == "__main__":
    main()
```

---

## Print Statement Standards

### Emoji Usage
Use consistent emojis for specific operations:

- 📥 `📥` - Loading data
- 💾 `💾` - Saving data
- 🚀 `🚀` - Starting process
- ✅ `✅` - Success/completion
- ⚠️ `⚠️` - Warnings
- ❌ `❌` - Errors
- 📊 `📊` - Statistics/metrics
- 🔧 `🔧` - Configuration/optimization
- 🧹 `🧹` - Cleaning operations
- 🔍 `🔍` - Searching/filtering
- 📈 `📈` - Analysis/aggregation
- 🗺️ `🗺️` - Geographic operations
- 📅 `📅` - Temporal operations
- 🏙️ `🏙️` - Municipality operations

### Section Headers
Use bordered headers for major sections:

```python
print(f"\n{'=' * 60}")
print(f"Section Title: {variable}")
print(f"{'=' * 60}\n")
```

### Progress Messages
Use indented messages for sub-operations:

```python
print("🚀 Starting major operation...")
print("  ✅ Completed sub-step 1")
print("  ✅ Completed sub-step 2")
print(f"  📊 Result: {count:,} items processed")
```

### Number Formatting
Use thousands separator for large numbers:

```python
print(f"Loaded {len(df):,} records")  # Output: "Loaded 2,677,101 records"
```

### Multi-line Output
Use blank lines to separate logical sections:

```python
print(f"📥 Loading data from {path}...")
print(f"  ✅ Loaded {count:,} records\n")  # Note the \n

print("🔧 Processing data...")
```

---

## Comment Standards

### Inline Comments
Use for clarifying complex logic:

```python
# Convert datetime.time to hour (int) for binning
df_temp = df[column].apply(lambda t: t.hour if hasattr(t, 'hour') else np.nan)
```

### Section Comments
Use for separating major code blocks:

```python
# Define paths
input_path = os.path.join(...)
output_path = os.path.join(...)

# Load data
df = pd.read_parquet(input_path)

# Process data
df_processed = process(df)

# Save results
df_processed.to_parquet(output_path)
```

### Docstring vs Comment
- **Docstrings**: For functions, classes, modules (what it does)
- **Comments**: For implementation details (how it works)

---

## ArgParse Standards

### Required Positional Arguments
```python
parser.add_argument("year", type=int, default=YEAR, help="Year to process")
```

### Optional Arguments
```python
parser.add_argument("--data_dir", default=DIR, help="Data directory")
parser.add_argument("--dataset", default=DATASET, help="Dataset name")
parser.add_argument("--overwrite", action="store_true", help="Overwrite existing data")
parser.add_argument("--all", action="store_true", help="Process all available years")
```

### Help Messages
- Use sentence case
- Be concise but clear
- No trailing periods

---

## File Naming Standards

#### Scripts
- Use snake_case: `prepare_deployment.py`
- Use numbered prefixes for pipeline steps: `01_read_raw_data.py`, `02_clean_data.py`
- Use descriptive verbs for orchestrators: `run_pipeline.py`

### Data Files
- Include year: `2024_essential.parquet`
- Include scope: `monthly_2024.parquet`, `state_2024.parquet`
- Use descriptive names: `raw.parquet`, `clean.parquet`, `complete.parquet`

---

## Error Handling

### Try-Except Pattern
```python
try:
    result = risky_operation()
except SpecificError as e:
    print(f"⚠️ Warning: {str(e)}")
    # Fallback or continue
except Exception as e:
    print(f"❌ Error: {str(e)}")
    raise
```

### Path Validation
```python
if not os.path.exists(input_path):
    print(f"⚠️ File not found: {input_path}")
    print(f"Skipping year {year}")
    return None
```

---

## Type Hints

### Function Signatures
Always include type hints:

```python
def process_data(df: pd.DataFrame, year: int, overwrite: bool = False) -> pd.DataFrame:
    """Process SINASC data."""
    pass
```

### Common Types
```python
from typing import Literal, Optional, Union

def function(
    required: str,
    optional: Optional[int] = None,
    choice: Literal["A", "B", "C"] = "A"
) -> Union[pd.DataFrame, None]:
    pass
```

---

## Data Processing Patterns

### Loading Data
```python
print(f"📥 Loading data from {input_path}...")
df = pd.read_parquet(input_path)
print(f"  ✅ Loaded {len(df):,} records with {len(df.columns)} columns\n")
```

### Saving Data
```python
print(f"\n💾 Saving data to {output_path}...")
df.to_parquet(output_path, compression="snappy", index=False)
file_size = os.path.getsize(output_path) / 1024**2
print(f"  ✅ Saved successfully ({file_size:.1f} MB)\n")
```

### Progress Tracking
```python
print("🔧 Processing items...")
for i, item in enumerate(items):
    if (i + 1) % 100 == 0:
        print(f"  Processed {i + 1:,}/{len(items):,} items...")
print(f"  ✅ Completed {len(items):,} items\n")
```

---

## Testing Guidelines

### Manual Testing Commands
Include in module docstring:

```python
"""
Usage:
    python script.py 2024
    python script.py 2024 --overwrite
    python script.py --all
"""
```

### Validation Checks
```python
# Validate results
assert len(df_output) > 0, "Output DataFrame is empty"
assert "required_column" in df_output.columns, "Missing required column"
print(f"✅ Validation passed: {len(df_output):,} records")
```

---

## Examples by Script Type

### Data Download Script (read_file.py)
- Module docstring with API details
- Helper functions for different endpoints
- Caching logic with overwrite option
- Error handling for network issues

### Data Cleaning Script (clean_file.py)
- Schema validation functions
- Type optimization with memory tracking
- Unknown value replacement
- Before/after statistics

### Feature Engineering Script (feature_engineering.py)
- Feature creation functions by type
- Label generation and saving
- Comprehensive docstrings for complex logic
- Category definitions at module level

### Pipeline Script (run_one_year.py)
- Orchestrates multiple steps
- Clear separation of stages
- Progress tracking throughout
- Final summary statistics

### Main Entry Point (main.py)
- Handles multiple years
- Calls subprocess for dashboard creation
- Overall pipeline progress
- Success message at end

---

## Changelog
- **2025-10-03**: Initial standardization across all scripts
  - Added module docstrings
  - Standardized print statement format
  - Improved function docstrings
  - Consistent argparse structure
  - Fixed f-string linting issues

---

*This document defines the coding standards for SINASC research project scripts.*
