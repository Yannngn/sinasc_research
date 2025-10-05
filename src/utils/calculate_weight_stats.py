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

from functools import lru_cache

import pandas as pd
from pandarallel import pandarallel
from pandas.io.common import file_exists
from pygrowthstandards import functional as F
from pygrowthstandards.utils.config import DataSexType

pandarallel.initialize(progress_bar=True, verbose=0)

SEX_MAP: dict[int, DataSexType] = {0: "U", 1: "M", 2: "F"}


@lru_cache
def get_weight_percentile(value: float, sex: DataSexType, gestational_age: int):
    return F.percentile(
        "weight",
        value=value,
        sex=sex,
        gestational_age=gestational_age,
    )


def calculate_weight_percentile(
    weight: pd.Series, sex: pd.Series, gestational_age: pd.Series, stats_file: str, overwrite: bool = False
) -> pd.Series:
    """
    Calculate weight statistics for a given column.

    Args:
        weight: Input Series representing the weight data (in grams).
        sex: Input Series representing the sex data.
        gestational_age: Input Series representing the gestational age data (in weeks).
        stats_file: Path to save/load cached statistics.
        overwrite: Whether to recalculate even if cache exists.

    Returns:
        Series with calculated weight percentiles (rounded to 2 decimals), with pd.NA for invalid rows.
    """
    if file_exists(stats_file) and not overwrite:
        stats_series = pd.read_parquet(stats_file).squeeze("columns")  # Load as Series
        print("  ✅ Loaded existing stats.")
        return stats_series  # type: ignore

    # Create mask for valid rows to avoid processing invalid data
    valid_rows_mask = (
        weight.notna() & sex.notna() & gestational_age.notna() & gestational_age.between(33, 42)  # pygrowthstandards valid range
    )

    # Initialize result Series with pd.NA (using Float32 for memory efficiency)
    stats_series = pd.Series(pd.NA, index=weight.index, dtype="Float32")

    if valid_rows_mask.any():
        # Work only on valid rows to reduce memory usage and computation
        valid_weight = weight.loc[valid_rows_mask].astype("float32") / 1000  # Convert to kg
        valid_sex = sex.loc[valid_rows_mask].replace(SEX_MAP).astype("category")  # Use category for efficiency
        valid_gest_age = gestational_age.loc[valid_rows_mask].astype("Int16") * 7  # Weeks to days

        # Create a temporary DataFrame only for valid rows
        temp_df = pd.DataFrame({"weight": valid_weight, "sex": valid_sex, "gestational_age": valid_gest_age})

        # Calculate percentiles in parallel on the smaller DataFrame
        percentiles = (
            temp_df.parallel_apply(
                lambda row: get_weight_percentile(value=row["weight"], sex=row["sex"], gestational_age=row["gestational_age"]),
                axis=1,
            )  # type: ignore
            .astype("float32")
            .round(2)
        )  # Round to 2 decimals immediately

        # Assign back to the full series
        stats_series.loc[valid_rows_mask] = percentiles.values

    # Save the result for future use
    stats_series.to_frame().to_parquet(stats_file, index=True)
    print("  ✅ Calculated and saved weight stats.")

    return stats_series


def save_stats_column(stats: pd.Series, stats_file: str):
    """
    Save the statistics Series to a Parquet file.

    Args:
        stats: Series containing the statistics data.
        stats_file: Path to save the statistics.
    """
    stats.to_frame().to_parquet(stats_file, index=True)
    print(f"  ✅ Saved stats to {stats_file}")
