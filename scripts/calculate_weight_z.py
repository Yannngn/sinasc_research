import argparse
import os
import warnings
from functools import lru_cache
from typing import Literal

import pandas as pd
from pandarallel import pandarallel
from pandas.io.common import file_exists
from pygrowthstandards import functional as F
from read_file import read_parquet

pandarallel.initialize(progress_bar=True, verbose=0)
warnings.filterwarnings("ignore")


def calculate_weight_percentile(df: pd.DataFrame, z_score_path: str, overwrite: bool = False) -> pd.DataFrame:
    print("🚀 Starting weight percentile calculation...")

    if file_exists(z_score_path) and not overwrite:
        df["PESOPERC"] = pd.read_parquet(z_score_path)["PESOPERC"]
        print("✅ Loaded existing birth weight percentiles.")
        return df
    else:
        # Note: pygrowthstandards expects sex as 'M'/'F' and gestational_age in days.

        sex_map: dict[int, Literal["M", "F", "U"]] = {1: "M", 2: "F", 9: "U"}  # SINASC: 1 for Male, 2 for Female

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

        print("✅ Calculated and Saved birth weight percentiles.")

        return df


DIR = "data/SINASC"
YEAR = 2024
DATASET = "selected_features"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Feature engineering for SINASC data")
    parser.add_argument("--data_dir", default=DIR, help="Data directory")
    parser.add_argument("--year", type=int, default=YEAR, help="Year")
    parser.add_argument("--dataset", default=DATASET, help="Dataset name (without extension)")
    args = parser.parse_args()

    input_path = os.path.join(args.data_dir, str(args.year), f"{args.dataset}.parquet")
    output_path = os.path.join(args.data_dir, str(args.year), "weight_percentiles.parquet")

    print(f"Loading data from {input_path}...")
    df = read_parquet(input_path)

    df = calculate_weight_percentile(df, z_score_path=os.path.join(args.data_dir, str(args.year), "calculated_weight_percentiles.parquet"))

    print(f"Saving engineered data to {output_path}...")
    df.to_parquet(output_path)
