import argparse
import os

import pandas as pd
from calculate_weight_z import calculate_weight_percentile
from clean_file import check_data, clean_empty_rows, clean_unknown_sinasc_data, optimize_data_types
from feature_engineering import feature_engineering
from feature_selection import feature_selection
from read_file import load_data


def run_one_year(data_dir: str, year: int) -> pd.DataFrame:
    data_path = os.path.join(data_dir, str(year))
    os.makedirs(data_path, exist_ok=True)

    df = load_data(year, output_dir=data_dir)

    check_data(df)
    df = optimize_data_types(df)
    clean = clean_empty_rows(df)
    clean = clean_unknown_sinasc_data(clean)
    selected = feature_selection(clean)
    weight = calculate_weight_percentile(selected, os.path.join(data_path, "calculated_weight_percentiles.parquet"))
    fe = feature_engineering(weight)
    fe.to_parquet(os.path.join(data_path, "complete.parquet"))

    return fe


DIR = "data/SINASC"
YEAR = 2024

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Feature engineering for SINASC data")
    parser.add_argument("--data_dir", default=DIR, help="Data directory")
    parser.add_argument("--year", type=int, default=YEAR, help="Year")
    args = parser.parse_args()

    run_one_year(args.data_dir, args.year)
