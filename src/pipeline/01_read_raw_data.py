"""
Download SINASC data from DATASUS API.

This script downloads birth records data from the Brazilian Ministry of Health
(DATASUS) API and saves as Parquet format for efficient processing.

Usage:
    python read_file.py 2024
    python read_file.py 2024 --overwrite
    python read_file.py 2024 --data_dir data/SINASC
"""

import io
import os
import zipfile

import pandas as pd
import requests
from pandas.io.common import file_exists

# DATASUS API endpoint
SINASC_API_PREFIX = "https://s3.sa-east-1.amazonaws.com/ckan.saude.gov.br/SINASC/csv/SINASC_"


def _request_csv(year: int) -> pd.DataFrame:
    """Download data from direct CSV endpoint."""
    url = f"{SINASC_API_PREFIX}{year}.csv"
    response = requests.get(url)
    response.raise_for_status()

    return pd.read_csv(
        io.StringIO(response.text),
        sep=";",
        low_memory=False,
        encoding="utf-8",
        dtype=str,
    )


def _request_zip(year: int):
    """Download data from ZIP archive endpoint."""
    url = f"{SINASC_API_PREFIX}{year}_csv.zip"
    response = requests.get(url)
    response.raise_for_status()

    with zipfile.ZipFile(io.BytesIO(response.content)) as z:
        csv_ = z.namelist()[0]

        with z.open(csv_) as f:
            return pd.read_csv(f, sep=";", low_memory=False, encoding="utf-8", dtype=str)


def _request(year: int) -> pd.DataFrame:
    """Download and save SINASC data trying CSV then ZIP endpoints."""
    try:
        data = _request_csv(year)
    except requests.HTTPError:
        try:
            data = _request_zip(year)
        except requests.HTTPError:
            raise RuntimeError(f"Failed to download data for year {year} from both direct CSV and ZIP endpoints.")

    if "contador" in data.columns:
        data.set_index("contador", inplace=True)
    elif "CONTADOR" in data.columns:
        data.set_index("CONTADOR", inplace=True)

    return data


def load_data(year: int, input_path: str = "raw.parquet", overwrite: bool = False):
    """
    Load SINASC data from file or download from API.

    Args:
        year: Year to load
        input_path: Path to input Parquet file
        overwrite: Whether to redownload even if file exists

    Returns:
        DataFrame with raw SINASC data
    """

    if overwrite or not file_exists(input_path):
        data = _request(year)
        data.to_parquet(input_path, index=False)  # securing raw copy
        return data

    return pd.read_parquet(input_path)


# Default configuration
DIR = "data/SINASC"
YEAR = 2024


def main():
    """Main execution function."""
    import argparse

    parser = argparse.ArgumentParser(description="Download SINASC data from DATASUS API")
    parser.add_argument("year", type=int, default=YEAR, help="Year to download")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing data")
    parser.add_argument("--data_dir", default=DIR, help="Data directory")
    parser.add_argument("--input_name", default="raw.parquet", help="Input file name")
    parser.add_argument("--output_name", default="raw.parquet", help="Output file name")
    args = parser.parse_args()

    print(f"\n{'=' * 60}")
    print(f"Downloading SINASC Data: {args.year}")
    print(f"{'=' * 60}\n")

    path_ = os.path.join(args.data_dir, str(args.year))
    os.makedirs(path_, exist_ok=True)
    input_path = os.path.join(path_, args.input_name)
    output_file = os.path.join(path_, args.output_name)

    # Download data
    data = load_data(args.year, input_path=input_path, overwrite=args.overwrite)
    data.to_parquet(output_file, index=False)
    print(f"\n✅ Data loaded for year {args.year}")
    print(f"   Shape: {data.shape[0]:,} records, {data.shape[1]} columns\n")


if __name__ == "__main__":
    main()
