import json
from collections import defaultdict

import pandas as pd

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


def optimize_data_types(df: pd.DataFrame) -> pd.DataFrame:
    """
    Optimize data types to reduce memory usage based on official SINASC schema
    """
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
                    df[col] = pd.to_datetime(date_str.where(valid_mask, pd.NA), format="%d%m%Y", errors="coerce")

                conversion_count += len(cols)
            elif target_type == "time":
                print(f"Converting time columns: {cols}")

                for col in cols:
                    time_str = df[col].astype("string").str.replace(r"\.0$", "", regex=True).str.zfill(4)
                    valid_mask = time_str.str.match(r"^\d{4}$", na=False)
                    df[col] = pd.to_datetime(time_str.where(valid_mask, pd.NA), format="%H%M", errors="coerce").dt.time

                conversion_count += len(cols)

        except Exception as e:
            for col in cols:
                print(f"⚠️  Could not convert {col} to {target_type}: {str(e)[:80]}...")

    optimized_memory = df.memory_usage(deep=True).sum() / 1024**2
    reduction_percent = (original_memory - optimized_memory) / original_memory * 100

    print("\n💾 Optimization results:")
    print(f"\t✅ Converted {conversion_count} columns using schema definitions")
    print(f"\t📊 Memory: {original_memory:.1f} MB → {optimized_memory:.1f} MB")
    print(f"\t📉 Reduction: {reduction_percent:.1f}%")

    return df


def clean_empty_rows(df: pd.DataFrame) -> pd.DataFrame:
    print("🧹 Starting cleaning empty rows...")
    cleaning_log = []
    # 1. Check for completely empty rows
    empty_rows = df.isnull().all(axis=1).sum()
    if empty_rows > 0:
        df = df.dropna(how="all")
        cleaning_log.append(f"🗑️  Removed {empty_rows} completely empty rows")

    for log_entry in cleaning_log:
        print(log_entry)

    return df


def clean_unknown_sinasc_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Perform initial data cleaning based on SINASC specifications
    """
    print("🧹 Starting replacing unknown flags from integer columns...")
    cleaning_log = []
    # 2. Replace known "unknown" codes with NaN for integer columns
    for col, unknown_value in NUMERICAL_WITH_UNKNOWN_FLAGS.items():
        if col in df.columns:
            unknown_count = (df[col] == unknown_value).sum()
            if unknown_count > 0:
                df.loc[df[col] == unknown_value, col] = pd.NA
                cleaning_log.append(f"⚠️ Replaced {unknown_count} '{unknown_value}' entries with NaN in '{col}'")

    # 4. Basic statistics
    cleaning_log.append(f"📊 Final dataset shape: {df.shape}")

    # Print cleaning log
    for log_entry in cleaning_log:
        print(log_entry)

    return df


if __name__ == "__main__":
    # Example usage
    data = pd.read_parquet("data/SINASC/2024/raw.parquet")
    # Apply optimizations
    check_data(data)
    data = optimize_data_types(data)
    data = clean_empty_rows(data)
    data = clean_unknown_sinasc_data(data)
    data.to_parquet("data/SINASC/2024/clean.parquet", index=False)
