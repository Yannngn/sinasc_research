"""
Clean and optimize SINASC data files.

This script performs data cleaning based on SINASC specifications:
1. Validates schema compliance
2. Replaces unknown flags with NaN
3. Optimizes data types for memory efficiency
4. Converts date/time columns to proper formats

Usage:
    python clean_file.py 2024
    python clean_file.py 2024 --data_dir data/SINASC
"""

import json
import os
from collections import defaultdict

import pandas as pd

# Load SINASC schema definitions
SINASC_COLUMNS = json.load(open("data/SINASC/dtypes.json", "r"))


NUMERICAL_WITH_UNKNOWN_FLAGS = {
    "IDADEMAE": 99,
    "APGAR1": 99,
    "APGAR5": 99,
    "QTDFILVIVO": 99,
    "QTDFILMORT": 99,
    "IDADEPAI": 99,
    "SEMAGESTAC": 99,
    "QTDGESTANT": 99,
    "QTDPARTNOR": 99,
    "QTDPARTCES": 99,
    "CONSPRENAT": 99,
    "MESPRENAT": 99,
}


def check_data(df: pd.DataFrame) -> None:
    """
    Validate DataFrame schema against official SINASC specification.

    Args:
        df: Input DataFrame to validate
    """
    found_columns = []
    missing_from_dataset = []
    unexpected_columns = []

    # Check which schema columns are present in dataset
    for col in SINASC_COLUMNS.keys():
        if col in df.columns:
            found_columns.append(col)
        else:
            missing_from_dataset.append(col)

    # Check for columns in dataset not in schema
    for col in df.columns:
        if col not in SINASC_COLUMNS:
            unexpected_columns.append(col)

    print("📋 Schema compliance check:")
    print(f"\t✅ Found {len(found_columns)}/{len(SINASC_COLUMNS)} expected columns")

    if missing_from_dataset:
        print(f"\t⚠️  Missing {len(missing_from_dataset)} columns from official schema:")
        for col in missing_from_dataset[:10]:  # Show first 10
            print(f"\t\t- {col}")
        if len(missing_from_dataset) > 10:
            print(f"\t\t... and {len(missing_from_dataset) - 10} more")

    if unexpected_columns:
        print(f"\t🔍 Found {len(unexpected_columns)} unexpected columns not in schema:")
        for col in unexpected_columns[:5]:  # Show first 5
            print(f"\t\t- {col}")
        if len(unexpected_columns) > 5:
            print(f"\t\t... and {len(unexpected_columns) - 5} more")


def clean_unknown_sinasc_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Replace unknown value flags with NaN based on SINASC specifications.

    Args:
        df: Input DataFrame with SINASC data

    Returns:
        Cleaned DataFrame with unknown flags replaced by NaN
    """
    print("🧹 Replacing unknown flags from integer columns...")
    cleaning_log = []
    # 2. Replace known "unknown" codes with NaN for integer columns
    for col, unknown_value in NUMERICAL_WITH_UNKNOWN_FLAGS.items():
        if col in df.columns:
            unknown_count = (df[col] == unknown_value).sum()
            if unknown_count > 0:
                df.loc[df[col] == unknown_value, col] = pd.NA
                cleaning_log.append(f"⚠️ Replaced {unknown_count} '{unknown_value}' entries with NaN in '{col}'")
            # df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int8")

    # df["PESO"] = pd.to_numeric(df["PESO"], errors="coerce").astype("Int16")
    # 4. Basic statistics
    cleaning_log.append(f"📊 Final dataset shape: {df.shape}")

    # Print cleaning log
    for log_entry in cleaning_log:
        print(log_entry)

    return df


def optimize_data_types(df: pd.DataFrame) -> pd.DataFrame:
    """
    Optimize data types to reduce memory usage based on official SINASC schema.

    Args:
        df: Input DataFrame with raw SINASC data

    Returns:
        Optimized DataFrame with proper data types
    """

    check_data(df)

    print("🔧 Optimizing data types based on official SINASC schema...")
    original_memory = df.memory_usage(deep=True).sum() / 1024**2

    conversion_count = 0
    print("\n🔄 Converting data types...")

    # Group columns by target type
    conversions = defaultdict(list)
    for col in SINASC_COLUMNS.keys():
        if col in df.columns:
            conversions[SINASC_COLUMNS[col]].append(col)

    # Perform conversions by type
    for target_type, cols in conversions.items():
        try:
            if target_type == "category":
                print(f"Converting categorical columns: {cols}")

                df[cols] = df[cols].fillna("09").astype("category")

                conversion_count += len(cols)
            elif target_type == "string":
                print(f"Converting text columns: {cols}")
                for col in cols:
                    df[col] = df[col].astype("string")

                conversion_count += len(cols)
            elif target_type == "bool":
                print(f"Converting boolean columns: {cols}")

                df[cols] = df[cols].astype("Int8").astype("boolean")

                conversion_count += len(cols)

            elif target_type in ["Int8", "Int16", "Int32"]:
                print(f"Converting integer columns: {cols}")

                for col in cols:
                    df[col] = pd.to_numeric(df[col], errors="coerce").astype(target_type)

                conversion_count += len(cols)
            elif target_type == "date":
                print(f"Converting date columns: {cols}")

                for col in cols:
                    date_str = df[col].astype("string").str.replace(r"\.0$", "", regex=True).str.zfill(8)
                    valid_mask = date_str.str.match(r"^\d{8}$", na=False)
                    df[col] = pd.to_datetime(
                        date_str.where(valid_mask, pd.NA),
                        format="%d%m%Y",
                        errors="coerce",
                    )

                conversion_count += len(cols)
            elif target_type == "time":
                print(f"Converting time columns: {cols}")

                for col in cols:
                    time_str = df[col].astype("string").str.replace(r"\.0$", "", regex=True).str.zfill(4)
                    valid_mask = time_str.str.match(r"^\d{4}$", na=False)
                    df[col] = pd.to_datetime(
                        time_str.where(valid_mask, pd.NA),
                        format="%H%M",
                        errors="coerce",
                    ).dt.time

                conversion_count += len(cols)

        except Exception as e:
            for col in cols:
                print(f"⚠️  Could not convert {col} to {target_type}: {str(e)[:80]}...")

    df = clean_unknown_sinasc_data(df)

    optimized_memory = df.memory_usage(deep=True).sum() / 1024**2
    reduction_percent = (original_memory - optimized_memory) / original_memory * 100

    print("\n💾 Optimization results:")
    print(f"\t✅ Converted {conversion_count} columns using schema definitions")
    print(f"\t📊 Memory: {original_memory:.1f} MB → {optimized_memory:.1f} MB")
    print(f"\t📉 Reduction: {reduction_percent:.1f}%")

    return df


# Default configuration
DIR = "data/SINASC"
YEAR = 2024


def main():
    """Main execution function."""
    import argparse

    parser = argparse.ArgumentParser(description="Clean and optimize SINASC data for a given year")
    parser.add_argument("year", type=int, default=YEAR, help="Year to process")
    parser.add_argument("--data_dir", default=DIR, help="Data directory")
    parser.add_argument("--input_name", default="raw.parquet", help="Input file name")
    parser.add_argument("--output_name", default="clean.parquet", help="Output file name")

    args = parser.parse_args()

    # Define paths
    input_path = os.path.join(args.data_dir, str(args.year), args.input_name)
    output_path = os.path.join(args.data_dir, str(args.year), args.output_name)

    print(f"\n{'=' * 60}")
    print(f"Cleaning SINASC Data: {args.year}")
    print(f"{'=' * 60}\n")

    # Load data
    print(f"📥 Loading data from {input_path}...")
    data = pd.read_parquet(input_path)
    print(f"  ✅ Loaded {len(data):,} records\n")

    # Clean and optimize
    data = optimize_data_types(data)

    # Save results
    print(f"\n💾 Saving cleaned data to {output_path}...")
    data.to_parquet(output_path)
    print("  ✅ Saved successfully\n")


if __name__ == "__main__":
    main()
