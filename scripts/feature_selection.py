"""
Feature selection for SINASC data.

This script selects essential columns from the complete SINASC dataset
for further processing and analysis. Reduces data size while retaining
all necessary information for demographic, clinical, and geographic analysis.

Usage:
    python feature_selection.py 2024
    python feature_selection.py 2024 --data_dir data/SINASC
    python feature_selection.py 2024 --dataset clean
"""

import os

import pandas as pd

# Essential features for analysis
SELECTED_FEATURES = [
    "CODESTAB",
    "CODMUNNASC",
    "LOCNASC",
    "CODMUNRES",
    "IDADEMAE",
    "ESTCIVMAE",
    "ESCMAE",
    "CODOCUPMAE",
    "IDADEPAI",
    "GRAVIDEZ",
    "PARTO",
    "PARIDADE",
    "CONSULTAS",
    "PESO",
    "GESTACAO",
    "SEMAGESTAC",
    "APGAR1",
    "APGAR5",
    "RACACOR",
    "RACACORMAE",
    "SEXO",
    "TPAPRESENT",
    # PARA ENGINEERING
    "DTNASC",
    "HORANASC",
    "QTDGESTANT",
    "QTDPARTNOR",
    "QTDPARTCES",
    "STTRABPART",
    "STCESPARTO",
    "CONSPRENAT",
    "MESPRENAT",
    # ENGINEERING SINASC
    "TPROBSON",
    "KOTELCHUCK",
]


def feature_selection(df: pd.DataFrame, selected_features: list[str] = SELECTED_FEATURES) -> pd.DataFrame:
    """
    Select essential features from complete dataset.

    Args:
        df: Input DataFrame with all columns
        selected_features: List of column names to keep

    Returns:
        DataFrame with only selected columns
    """
    return df[selected_features]


# Default configuration
DIR = "data/SINASC"
YEAR = 2024
DATASET = "clean"


def main():
    """Main execution function."""
    import argparse

    parser = argparse.ArgumentParser(description="Feature selection for SINASC data")
    parser.add_argument("year", type=int, default=YEAR, help="Year to process")
    parser.add_argument("--data_dir", default=DIR, help="Data directory")
    parser.add_argument("--dataset", default=DATASET, help="Dataset name")
    parser.add_argument("--selected_features", nargs="+", default=SELECTED_FEATURES, help="List of selected features")
    args = parser.parse_args()

    # Define paths
    input_path = os.path.join(args.data_dir, str(args.year), f"{args.dataset}.parquet")
    output_path = os.path.join(args.data_dir, str(args.year), "selected_features.parquet")

    print(f"\n{'=' * 60}")
    print(f"Feature Selection: {args.year}")
    print(f"{'=' * 60}\n")

    # Load data
    print(f"📥 Loading data from {input_path}...")
    df = pd.read_parquet(input_path)
    print(f"  ✅ Loaded {len(df):,} records with {len(df.columns)} columns\n")

    # Select features
    print(f"🔍 Selecting {len(args.selected_features)} essential features...")
    df_selected = feature_selection(df, args.selected_features)
    print(f"  ✅ Selected {len(df_selected.columns)} columns\n")

    # Save results
    print(f"💾 Saving selected data to {output_path}...")
    df_selected.to_parquet(output_path)
    print("  ✅ Saved successfully\n")


if __name__ == "__main__":
    main()
