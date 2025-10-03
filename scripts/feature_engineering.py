import argparse
import os

import numpy as np
import pandas as pd
from read_file import read_parquet

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
            "Trabalhadora do Lar",
            "Estudante",
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
    df[new_column] = pd.NA
    for val, bin_val in zip(to_replace, bins):
        df.loc[df[column].notna() & df[column].str.startswith(val), new_column] = bin_val

    df.loc[df[column].isna(), new_column] = 9

    df[new_column] = df[new_column].astype("Int8").fillna(8)

    return df


def bool_column(df: pd.DataFrame, column: str, new_column: str, func) -> pd.DataFrame:
    df[new_column] = df[column].astype("Int8").apply(lambda x: func(x) if pd.notna(x) else pd.NA)
    return df


def comparison_column(df: pd.DataFrame, column1: str, column2: str, new_column: str, func) -> pd.DataFrame:
    df[new_column] = pd.NA
    mask = df[column1].notna() & df[column2].notna()
    df[new_column] = func(df.loc[mask, column1], df.loc[mask, column2]).astype("boolean")
    return df


def bin_column(df: pd.DataFrame, column: str, bins: list[int], labels: list[str], new_column: str) -> pd.DataFrame:
    df[new_column] = pd.cut(df[column], bins=bins, labels=labels, right=False, include_lowest=True)
    df[new_column] = df[new_column].cat.add_categories("9").fillna("9")

    return df


def bin_time_column(df: pd.DataFrame, column: str, bins: list[int], labels: list[str], new_column: str) -> pd.DataFrame:
    # Convert datetime.time to hour (int) for binning
    df_temp = df[column].apply(lambda t: t.hour if hasattr(t, "hour") and pd.notnull(t) else np.nan)
    df[new_column] = pd.cut(df_temp, bins=bins, labels=labels, right=False, include_lowest=True)
    df[new_column] = df[new_column].cat.add_categories("9").fillna("9")

    return df


def feature_engineering(df: pd.DataFrame) -> pd.DataFrame:
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
    return df


DIR = "data/SINASC"
YEAR = 2024
DATASET = "weight_percentiles"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Feature engineering for SINASC data")
    parser.add_argument("--data_dir", default=DIR, help="Data directory")
    parser.add_argument("--year", type=int, default=YEAR, help="Year")
    parser.add_argument("--dataset", default=DATASET, help="Dataset name (without extension)")
    args = parser.parse_args()

    input_path = os.path.join(args.data_dir, str(args.year), f"{args.dataset}.parquet")
    output_path = os.path.join(args.data_dir, str(args.year), "engineered_features.parquet")

    print(f"Loading data from {input_path}...")
    df = read_parquet(input_path)

    df_fe = feature_engineering(df)

    print(f"Saving engineered data to {output_path}...")
    df_fe.to_parquet(output_path)
