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

    return pd.read_csv(io.StringIO(response.text), sep=";", low_memory=False, encoding="utf-8", dtype=str)


def _request_zip(year: int):
    """Download data from ZIP archive endpoint."""
    url = f"{SINASC_API_PREFIX}{year}_csv.zip"
    response = requests.get(url)
    response.raise_for_status()

    with zipfile.ZipFile(io.BytesIO(response.content)) as z:
        csv_ = z.namelist()[0]

        with z.open(csv_) as f:
            return pd.read_csv(f, sep=";", low_memory=False, encoding="utf-8", dtype=str)


def _request(year: int, outpath: str):
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

    data.to_parquet(outpath, index=False)

    print(f"✅ Saved raw API response to {outpath}")


def load_data(year: int, output_dir: str, overwrite: bool = False):
    """
    Load SINASC data from file or download from API.

    Args:
        year: Year to load
        output_dir: Output directory for saved files
        overwrite: Whether to redownload even if file exists

    Returns:
        DataFrame with raw SINASC data
    """
    path_ = os.path.join(output_dir, str(year))
    os.makedirs(path_, exist_ok=True)

    parquet_file = os.path.join(path_, "raw.parquet")

    if overwrite or not file_exists(parquet_file):
        _request(year, path_)

    return pd.read_parquet(parquet_file)


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
    args = parser.parse_args()

    print(f"\n{'=' * 60}")
    print(f"Downloading SINASC Data: {args.year}")
    print(f"{'=' * 60}\n")

    # Download data
    df = load_data(args.year, output_dir=args.data_dir, overwrite=args.overwrite)
    print(f"\n✅ Data loaded for year {args.year}")
    print(f"   Shape: {df.shape[0]:,} records, {df.shape[1]} columns\n")


if __name__ == "__main__":
    main()
