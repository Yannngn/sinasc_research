import argparse
import os
import zipfile

import pandas as pd
import requests
from pandas.io.common import file_exists


def read_raw(file_path):
    if file_path.endswith(".parquet"):
        return pd.read_parquet(file_path)
    return pd.read_csv(file_path, sep=";", low_memory=False, encoding="latin-1", dtype=str, index_col="contador")


def read_parquet(file_path, dtypes_path="data/SINASC/dtypes.json"):
    df = pd.read_parquet(file_path)

    return df


def load_data(year: int, output_dir: str = "data/SINASC", overwrite: bool = False):
    os.makedirs(os.path.join(output_dir, str(year)), exist_ok=True)

    parquet_file = os.path.join(output_dir, str(year), "raw.parquet")
    csv_file = os.path.join(output_dir, str(year), "raw.csv")

    if not overwrite:
        if file_exists(parquet_file):
            df = read_raw(parquet_file)
            return df

        if file_exists(csv_file):
            # Load CSV and save to Parquet
            df = read_raw(csv_file)
            df.to_parquet(parquet_file)
            return df

    # Try first pattern (CSV)
    url1 = f"https://s3.sa-east-1.amazonaws.com/ckan.saude.gov.br/SINASC/csv/SINASC_{year}.csv"
    response = requests.get(url1)
    if response.status_code == 200:
        with open(csv_file, "wb") as f:
            f.write(response.content)
    else:
        # Try second pattern (ZIP)
        url2 = f"https://s3.sa-east-1.amazonaws.com/ckan.saude.gov.br/SINASC/csv/SINASC_{year}_csv.zip"
        response = requests.get(url2)
        if response.status_code == 200:
            temp_zip = "temp.zip"
            with open(temp_zip, "wb") as f:
                f.write(response.content)
            with zipfile.ZipFile(temp_zip, "r") as zip_ref:
                zip_ref.extractall(".")
            # Assume the extracted file is the CSV
            extracted_files = [f for f in os.listdir(".") if f.endswith(".csv")]
            if extracted_files:
                os.rename(extracted_files[0], csv_file)
            os.remove(temp_zip)
        else:
            raise Exception(f"Could not download data for year {year}")

    # Load CSV and save to Parquet
    df = read_raw(csv_file)
    df.to_parquet(parquet_file)

    return df


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Load SINASC data for a given year.")
    parser.add_argument("year", type=int, help="The year to load data for.")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing data.")
    args = parser.parse_args()

    df = load_data(args.year, overwrite=args.overwrite)
    print(f"Data loaded for year {args.year}. Shape: {df.shape}")
