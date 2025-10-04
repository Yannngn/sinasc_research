"""
Calculate weight percentiles for SINASC data.

This script calculates birth weight percentiles using WHO growth standards    # Save results
    print(f"\n💾 Saving data to {output_path}...")
    df.to_parquet(output_path)
    print("  ✅ Saved successfully\n")ed on gestational age and sex. Uses parallel processing for efficiency.

Usage:
    python calculate_weight_z.py 2024
    python calculate_weight_z.py 2024 --data_dir data/SINASC
    python calculate_weight_z.py 2024 --dataset selected_features
"""

import os
import warnings
from functools import lru_cache
from typing import Literal

import pandas as pd
from pandarallel import pandarallel
from pandas.io.common import file_exists
from pygrowthstandards import functional as F

pandarallel.initialize(progress_bar=True, verbose=0)
warnings.filterwarnings("ignore")


def calculate_weight_percentile(df: pd.DataFrame, z_score_path: str, overwrite: bool = False) -> pd.DataFrame:
    """
    Calculate birth weight percentiles using WHO growth standards.

    Args:
        df: Input DataFrame with PESO, SEXO, and SEMAGESTAC columns
        z_score_path: Path to save/load cached percentiles
        overwrite: Whether to recalculate even if cache exists

    Returns:
        DataFrame with added PESOPERC column
    """
    print("🚀 Starting weight percentile calculation...")

    if file_exists(z_score_path) and not overwrite:
        df["PESOPERC"] = pd.read_parquet(z_score_path)["PESOPERC"]
        print("  ✅ Loaded existing birth weight percentiles.")
        return df
    else:
        # Calculate percentiles using pygrowthstandards
        # Note: Library expects sex as 'M'/'F' and gestational_age in days

        sex_map: dict[int, Literal["M", "F", "U"]] = {
            1: "M",
            2: "F",
            9: "U",
        }  # SINASC: 1 for Male, 2 for Female

        # Create a boolean mask for rows that can be processed
        # This avoids using .apply on the entire DataFrame, which is slow.
        valid_rows_mask = (
            df["PESO"].notna()
            & df["SEXO"].notna()
            & df["SEMAGESTAC"].notna()
            & df["SEMAGESTAC"].between(33, 42)  # pygrowthstandards valid range
        )

        # Initialize the new column with a numeric type that supports NA
        df["PESOPERC"] = pd.Series(dtype="float64")

        # Calculate percentiles only for the valid rows
        # Create a cache directory (adjust path as needed)

        @lru_cache
        def get_weight_percentile(value: float, sex: Literal["M", "F", "U"], gestational_age: int):
            return F.percentile(
                "weight",
                value=value,
                sex=sex,
                gestational_age=gestational_age,
            )

        percentiles = df.loc[valid_rows_mask].parallel_apply(
            lambda row: get_weight_percentile(
                value=row["PESO"] / 1000,
                sex=sex_map.get(row["SEXO"], "U"),
                gestational_age=row["SEMAGESTAC"] * 7,
            ),
            axis=1,
        )  # type: ignore

        # Assign the calculated percentiles back to the original DataFrame
        df.loc[valid_rows_mask, "PESOPERC"] = percentiles
        df.loc[:, "PESOPERC"].to_frame().to_parquet(z_score_path, index=False)

        print("  ✅ Calculated and saved birth weight percentiles.")

        return df


# Default configuration
DIR = "data/SINASC"
YEAR = 2024
DATASET = "selected_features"


def main():
    """Main execution function."""
    import argparse

    parser = argparse.ArgumentParser(description="Calculate weight percentiles for SINASC data")
    parser.add_argument("year", type=int, default=YEAR, help="Year to process")
    parser.add_argument("--data_dir", default=DIR, help="Data directory")
    parser.add_argument("--dataset", default=DATASET, help="Dataset name (without extension)")
    args = parser.parse_args()

    # Define paths
    input_path = os.path.join(args.data_dir, str(args.year), f"{args.dataset}.parquet")
    output_path = os.path.join(args.data_dir, str(args.year), "weight_percentiles.parquet")
    z_score_path = os.path.join(args.data_dir, str(args.year), "calculated_weight_percentiles.parquet")

    print(f"\n{'=' * 60}")
    print(f"Calculating Weight Percentiles: {args.year}")
    print(f"{'=' * 60}\n")

    # Load data
    print(f"📥 Loading data from {input_path}...")
    df = pd.read_parquet(input_path)
    print(f"  ✅ Loaded {len(df):,} records\n")

    # Calculate percentiles
    df = calculate_weight_percentile(df, z_score_path=z_score_path)

    # Save results
    print(f"\n💾 Saving data to {output_path}...")
    df.to_parquet(output_path)
    print("  ✅ Saved successfully\n")


if __name__ == "__main__":
    main()
