"""
Complete SINASC data processing pipeline for a single year.

This script executes the full data processing workflow:
1. Download raw data from DATASUS API
2. Clean and optimize data types
3. Select essential features
4. Calculate weight percentiles
5. Engineer new features
6. Save complete processed dataset

Usage:
    python run_one_year.py 2024
    python run_one_year.py 2024 --overwrite
    python run_one_year.py 2024 --data_dir data/SINASC
"""

import os

import pandas as pd
from calculate_weight_z import calculate_weight_percentile
from clean_file import optimize_data_types
from feature_engineering import feature_engineering
from feature_selection import feature_selection
from read_file import load_data


def run_one_year(year: int, data_dir: str, overwrite: bool = False) -> pd.DataFrame:
    """
    Execute complete data processing pipeline for one year.

    Args:
        year: Year to process
        data_dir: Data directory path
        overwrite: Whether to redownload raw data

    Returns:
        Fully processed DataFrame
    """
    print(f"\n{'=' * 60}")
    print(f"Processing Complete Pipeline: {year}")
    print(f"{'=' * 60}\n")

    data_path = os.path.join(data_dir, str(year))
    os.makedirs(data_path, exist_ok=True)

    df = load_data(year, output_dir=data_dir, overwrite=overwrite)

    clean = optimize_data_types(df)
    selected = feature_selection(clean)
    weight = calculate_weight_percentile(selected, os.path.join(data_path, "calculated_weight_percentiles.parquet"))
    fe = feature_engineering(weight)
    fe.to_parquet(os.path.join(data_path, "complete.parquet"))

    return fe


# Default configuration
DIR = "data/SINASC"
YEAR = 2024


def main():
    """Main execution function."""
    import argparse

    parser = argparse.ArgumentParser(description="Complete SINASC data processing pipeline")
    parser.add_argument("year", type=int, default=YEAR, help="Year to process")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing data")
    parser.add_argument("--data_dir", default=DIR, help="Data directory")
    args = parser.parse_args()

    run_one_year(args.year, args.data_dir, args.overwrite)


if __name__ == "__main__":
    main()
