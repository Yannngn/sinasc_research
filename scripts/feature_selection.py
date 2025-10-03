import argparse
import os

import pandas as pd
from read_file import read_parquet

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

DIR = "data/SINASC"
YEAR = 2024
DATASET = "clean"


def feature_selection(df: pd.DataFrame, selected_features: list[str] = SELECTED_FEATURES) -> pd.DataFrame:
    return df[selected_features]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Feature selection for SINASC data")
    parser.add_argument("--data_dir", default=DIR, help="Data directory")
    parser.add_argument("--year", type=int, default=YEAR, help="Year")
    parser.add_argument("--dataset", default=DATASET, help="Dataset name")
    parser.add_argument("--selected_features", nargs="+", default=SELECTED_FEATURES, help="List of selected features")

    args = parser.parse_args()

    df = read_parquet(os.path.join(args.data_dir, str(args.year), f"{args.dataset}.parquet"))
    df_selected = feature_selection(df, args.selected_features)
    df_selected.to_parquet(os.path.join(args.data_dir, str(args.year), "selected_features.parquet"))
