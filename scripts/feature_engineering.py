"""
Feature engineering for SINASC data.

This script creates new features from existing SINASC columns:
1. Boolean indicators (first pregnancy, previous births, etc.)
2. Categorical groupings (occupation, location)
3. Binned numeric variables (age groups, weight categories)
4. Time-based features (birth time periods)
5. APGAR evolution patterns

Usage:
    python feature_engineering.py 2024
    python feature_engineering.py 2024 --data_dir data/SINASC
    python feature_engineering.py 2024 --dataset weight_percentiles
"""

import argparse
import json
import os

import numpy as np
import pandas as pd

BOOL_COLUMNS = {
    "PRIMEGEST": (
        "QTDGESTANT",
        lambda x: x == 0,
    ),
    "PARTNORPREV": (
        "QTDPARTNOR",
        lambda x: x > 0,
    ),
    "PARTCESPREV": (
        "QTDPARTCES",
        lambda x: x > 0,
    ),
    "PAIREGIST": (
        "IDADEPAI",
        lambda x: isinstance(x, (int, float)),
    ),
}

NEW_CAT_COLUMNS = {
    "OCUPMAE": (
        "CODOCUPMAE",
        ["999991", "999992", "6", "2", "3", "4", "5"],
        [1, 2, 3, 4, 5, 6, 7],
        [
            "Estudante",
            "Trabalhadora do Lar",
            "Trabalhadora Rural",
            "Profissionais das Ciências e das Artes",
            "Técnicos e Profissionais de Nível Médio",
            "Trabalhadores de Serviços Administrativos",
            "Trabalhadores dos Serviços, Vendedores do Comércio em Lojas e Mercados",
        ],
    )
}

COMPARISON_COLUMNS = {
    "DESLOCNASCBOOL": (("CODMUNNASC", "CODMUNRES"), lambda x, y: x != y, "boolean"),
}

BIN_COLUMNS = {
    "IDADEMAE": (
        [8, 13, 17, 25, 35, 40, 50, 99],
        [1, 2, 3, 4, 5, 6, 7],
        ["Menor que 13", "13-16", "17-24", "25-34", "35-39", "40-49", "50 ou mais", "Ignorado"],
    ),
    "IDADEPAI": (
        [8, 13, 17, 25, 35, 50, 65, 99],
        [1, 2, 3, 4, 5, 6, 7],
        ["Menor que 13", "13-16", "17-24", "25-34", "35-49", "50-64", "65 ou mais", "Ignorado"],
    ),
    "PESO": (
        [100, 1000, 1500, 2500, 4000, 7000],
        [1, 2, 3, 4, 5],
        ["Menor que 1000g", "1000-1499g", "1500-2499g", "2500-3999g", "4000g ou mais", "Ignorado"],
    ),
    "PESOPERC": (
        [0, 0.10, 0.90, 1.0],
        [1, 2, 3],
        ["Pequeno para Idade", "Adequado para Idade", "Grande para Idade", "Ignorado"],
    ),
    "APGAR1": (
        [0, 2, 4, 7, 10],
        [1, 2, 3, 4],
        ["0-2", "3-4", "5-7", "8-10", "Ignorado"],
    ),
    "APGAR5": (
        [0, 2, 4, 7, 10],
        [1, 2, 3, 4],
        ["0-2", "3-4", "5-7", "8-10", "Ignorado"],
    ),
    "QTDGESTANT": (
        [1, 2, 3, 4, 5, 99],
        [1, 2, 3, 4, 5],
        ["1", "2", "3", "4", "5 ou mais", "Ignorado"],
    ),
    "QTDPARTNOR": (
        [1, 2, 3, 4, 5, 99],
        [1, 2, 3, 4, 5],
        ["1", "2", "3", "4", "5 ou mais", "Ignorado"],
    ),
    "QTDPARTCES": (
        [1, 2, 3, 4, 5, 99],
        [1, 2, 3, 4, 5],
        ["1", "2", "3", "4", "5 ou mais", "Ignorado"],
    ),
    "MESPRENAT": (
        [1, 3, 6, 99],
        [1, 2, 3],
        ["Primeiro Trimestre", "Segundo Trimestre", "Terceiro Trimestre", "Ignorado"],
    ),
}

TIME_COLUMNS = {
    "HORANASC": (
        [0, 6, 12, 18, 24],
        [1, 2, 3, 4],
        ["00:00-05:59", "06:00-11:59", "12:00-17:59", "18:00-23:59", "Ignorado"],
    ),
}


def new_category_column(df: pd.DataFrame, column: str, new_column: str, to_replace: list, bins: list) -> pd.DataFrame:
    """
    Create new categorical column from existing column using mappings.

    Args:
        df: Input DataFrame
        column: Source column name
        new_column: New column name
        to_replace: List of values to replace
        bins: List of replacement values

    Returns:
        DataFrame with new categorical column
    """
    df[new_column] = pd.NA
    for val, bin_val in zip(to_replace, bins):
        df.loc[df[column].notna() & df[column].str.startswith(val), new_column] = bin_val

    df.loc[df[column].isna(), new_column] = 9

    df[new_column] = df[new_column].astype("Int8").fillna(8)

    return df


def bool_column(df: pd.DataFrame, column: str, new_column: str, func) -> pd.DataFrame:
    """
    Create boolean column by applying function to existing column.

    Args:
        df: Input DataFrame
        column: Source column name
        new_column: New column name
        func: Function to apply for boolean evaluation

    Returns:
        DataFrame with new boolean column
    """
    df[new_column] = df[column].astype("Int8").apply(lambda x: func(x) if pd.notna(x) else pd.NA)
    return df


def comparison_column(df: pd.DataFrame, column1: str, column2: str, new_column: str, func) -> pd.DataFrame:
    """
    Create comparison column by applying function to two columns.

    Args:
        df: Input DataFrame
        column1: First column name
        column2: Second column name
        new_column: New column name
        func: Comparison function to apply

    Returns:
        DataFrame with new comparison column
    """
    df[new_column] = pd.NA
    mask = df[column1].notna() & df[column2].notna()
    df[new_column] = func(df.loc[mask, column1], df.loc[mask, column2]).astype("boolean")
    return df


def bin_column(df: pd.DataFrame, column: str, bins: list[int], labels: list[str], new_column: str) -> pd.DataFrame:
    """
    Create binned categorical column from numeric column.

    Args:
        df: Input DataFrame
        column: Source column name
        bins: List of bin edges
        labels: List of bin labels
        new_column: New column name

    Returns:
        DataFrame with new binned column
    """
    df[new_column] = pd.cut(df[column], bins=bins, labels=labels, right=False, include_lowest=True)
    df[new_column] = df[new_column].cat.add_categories("9").fillna("9")

    return df


def bin_time_column(df: pd.DataFrame, column: str, bins: list[int], labels: list[str], new_column: str) -> pd.DataFrame:
    """
    Create binned categorical column from time column.

    Args:
        df: Input DataFrame
        column: Source time column name
        bins: List of hour bin edges
        labels: List of bin labels
        new_column: New column name

    Returns:
        DataFrame with new binned time column
    """
    # Convert datetime.time to hour (int) for binning
    df_temp = df[column].apply(lambda t: t.hour if hasattr(t, "hour") and pd.notnull(t) else np.nan)
    df[new_column] = pd.cut(df_temp, bins=bins, labels=labels, right=False, include_lowest=True)
    df[new_column] = df[new_column].cat.add_categories("9").fillna("9")

    return df


def apgar_feature(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create APGAR evolution feature based on 1-minute and 5-minute scores.

    Categories:
    - Normal: Both scores >= 7
    - Desconforto Superado: 1min < 7, 5min >= 7 (improved)
    - Desconforto Tardio: 1min >= 7, 5min < 7 (deteriorated)
    - Desconforto Mantido: Both scores < 7 (persistent distress)

    Args:
        df: Input DataFrame with APGAR1 and APGAR5 columns

    Returns:
        DataFrame with EVOAPGAR categorical column
    """
    df["EVOAPGAR"] = pd.NA

    mask_normal = (df["APGAR1"] >= 7) & (df["APGAR5"] >= 7)
    df.loc[mask_normal, "EVOAPGAR"] = 1

    mask_superado = (df["APGAR1"] < 7) & (df["APGAR5"] >= 7)
    df.loc[mask_superado, "EVOAPGAR"] = 2

    mask_tardio = (df["APGAR1"] >= 7) & (df["APGAR5"] < 7)
    df.loc[mask_tardio, "EVOAPGAR"] = 3

    mask_mantido = (df["APGAR1"] < 7) & (df["APGAR5"] < 7)
    df.loc[mask_mantido, "EVOAPGAR"] = 4

    df["EVOAPGAR"] = df["EVOAPGAR"].fillna(9).astype("Int8")
    df["EVOAPGAR"] = df["EVOAPGAR"].astype("category")

    return df


def save_labels(output_path: str = "data/SINASC/engineered_categorical.json") -> None:
    """
    Save categorical labels for all engineered features to JSON file.

    Args:
        output_path: Path to save labels JSON file
    """
    # Load original categorical labels
    categorical_path = os.path.join(os.path.dirname(output_path), "categorical.json")
    with open(categorical_path, "r", encoding="utf-8") as f:
        labels = json.load(f)

    # Add labels for new categorical columns
    for col, (_, _, bins, label_list) in NEW_CAT_COLUMNS.items():
        labels[col] = dict(zip(map(str, bins), label_list))
        labels[col]["9"] = "Ignorado"

    # Add labels for binned columns
    for col, (_, bin_values, label_list) in BIN_COLUMNS.items():
        labels[col + "BIN"] = dict(zip(map(str, bin_values), label_list))
        labels[col + "BIN"]["9"] = "Ignorado"

    # Add labels for time columns
    for col, (_, bin_values, label_list) in TIME_COLUMNS.items():
        labels[col + "BIN"] = dict(zip(map(str, bin_values), label_list))
        labels[col + "BIN"]["9"] = "Ignorado"

    # Add labels for APGAR evolution
    labels["EVOAPGAR"] = {"1": "Normal", "2": "Desconforto Superado", "3": "Desconforto Tardio", "4": "Desconforto Mantido", "9": "Ignorado"}

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(labels, f, ensure_ascii=False, indent=4)


def feature_engineering(df: pd.DataFrame) -> pd.DataFrame:
    """
    Execute complete feature engineering pipeline.

    Creates:
    - Boolean indicators (first pregnancy, previous births, father registered)
    - New categorical groupings (occupation categories)
    - Binned numeric features (age groups, weight categories, APGAR categories)
    - Time-based features (birth time periods)
    - APGAR evolution patterns

    Args:
        df: Input DataFrame with selected SINASC features

    Returns:
        DataFrame with all engineered features added
    """
    print("🚀 Starting feature engineering...")

    for col, (source_col, func) in BOOL_COLUMNS.items():
        print(f"Creating boolean column: {col} from {source_col}")
        df = bool_column(df, source_col, col, func)
        df[col] = df[col].astype("boolean")

    for col, (source_col, to_replace, bins, _) in NEW_CAT_COLUMNS.items():
        print(f"Creating new categorical column: {col} from {source_col}")
        df = new_category_column(df, source_col, col, to_replace, bins)
        df[col] = df[col].astype("category")

    for col, ((col1, col2), func, dtype) in COMPARISON_COLUMNS.items():
        print(f"Creating comparison column: {col} from {col1} and {col2}")
        df = comparison_column(df, col1, col2, col, func)
        df[col] = df[col].astype(dtype)  # type: ignore

    for col, (bins, bin_values, _) in BIN_COLUMNS.items():
        print(f"Creating binned column: {col}")
        df = bin_column(df, col, bins=bins, labels=list(map(str, bin_values)), new_column=col + "BIN")
        df[col] = df[col].astype("category")

    for col, (bins, bin_values, _) in TIME_COLUMNS.items():
        print(f"Creating binned column: {col}")
        df = bin_time_column(df, col, bins=bins, labels=list(map(str, bin_values)), new_column=col + "BIN")
        df[col] = df[col].astype("category")

    print("✅ Feature engineering completed.")
    save_labels()
    print("✅ Saved categorical labels.")

    return df


# Default configuration
DIR = "data/SINASC"
YEAR = 2024
DATASET = "weight_percentiles"


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(description="Feature engineering for SINASC data")
    parser.add_argument("year", type=int, default=YEAR, help="Year to process")
    parser.add_argument("--data_dir", default=DIR, help="Data directory")
    parser.add_argument("--dataset", default=DATASET, help="Dataset name (without extension)")
    args = parser.parse_args()

    # Define paths
    input_path = os.path.join(args.data_dir, str(args.year), f"{args.dataset}.parquet")
    output_path = os.path.join(args.data_dir, str(args.year), "engineered_features.parquet")

    print(f"\n{'=' * 60}")
    print(f"Feature Engineering: {args.year}")
    print(f"{'=' * 60}\n")

    # Load data
    print(f"📥 Loading data from {input_path}...")
    df = pd.read_parquet(input_path)
    print(f"  ✅ Loaded {len(df):,} records\n")

    # Engineer features
    df_fe = feature_engineering(df)

    # Save results
    print(f"\n💾 Saving engineered data to {output_path}...")
    df_fe.to_parquet(output_path)
    print("  ✅ Saved successfully\n")


if __name__ == "__main__":
    main()
