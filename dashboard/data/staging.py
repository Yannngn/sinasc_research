"""
Ingests raw data from sources into the staging database.
"""

import io
import json
import os
import sys
import zipfile
from typing import Literal

import pandas as pd
import requests
from geoalchemy2 import WKTElement
from geoalchemy2.types import Geometry
from pandas.io.common import file_exists
from shapely.geometry import shape
from sqlalchemy import inspect

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir))

from data.database import get_staging_db_engine

SINASC_API_PREFIX = "https://s3.sa-east-1.amazonaws.com/ckan.saude.gov.br/SINASC/csv/SINASC_"
IBGE_API = "https://servicodados.ibge.gov.br/api/v1/localidades"
CNES_API = "https://s3.sa-east-1.amazonaws.com/ckan.saude.gov.br/CNES/cnes_estabelecimentos_json.zip"
GEOJSON_API = "https://servicodados.ibge.gov.br/api/v4/malhas/paises/BR"
SIDRA_API = "https://servicodados.ibge.gov.br/api/v3/agregados/1378/periodos/2010/variaveis/93"


# root path for the project
PATH = "/home/yannn/projects/Yannngn/sinasc-dashboard/sinasc_research"


def fetch_sinasc_data(year: int) -> pd.DataFrame:
    def _request_csv() -> pd.DataFrame:
        """Download data from direct CSV endpoint."""
        url = f"{SINASC_API_PREFIX}{year}.csv"
        response = requests.get(url)
        response.raise_for_status()

        return pd.read_csv(
            io.StringIO(response.text),
            sep=";",
            low_memory=False,
            encoding="latin-1",
            dtype=str,
        )

    def _request_zip() -> pd.DataFrame:
        """Download data from ZIP archive endpoint."""
        url = f"{SINASC_API_PREFIX}{year}_csv.zip"
        response = requests.get(url)
        response.raise_for_status()

        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            csv_ = z.namelist()[0]

            with z.open(csv_) as f:
                return pd.read_csv(f, sep=";", low_memory=False, encoding="latin-1", dtype=str)

    try:
        data = _request_csv()
    except requests.HTTPError:
        try:
            data = _request_zip()
        except requests.HTTPError:
            raise RuntimeError(f"Failed to download data for year {year} from both direct CSV and ZIP endpoints.")

    if "contador" in data.columns:
        data.set_index("contador", inplace=True)
    elif "CONTADOR" in data.columns:
        data.set_index("CONTADOR", inplace=True)

    return data


def fetch_cnes_data() -> pd.DataFrame:
    response = requests.get(CNES_API)
    response.raise_for_status()

    with zipfile.ZipFile(io.BytesIO(response.content)) as z:
        # Pega o nome do primeiro arquivo dentro do ZIP (geralmente o único)
        json_ = z.namelist()[0]

        with z.open(json_) as f:
            estabelecimentos = json.load(f)

        return pd.DataFrame(estabelecimentos)


def fetch_ibge_id(intrarregiao: Literal["BR", "UF", "regiao", "municipio"]) -> pd.DataFrame:
    """
    Fetch IBGE location IDs and names for a given administrative level.

    Args:
        intrarregiao: The administrative level ('BR', 'UF', 'regiao', 'municipio').

    Returns:
        pd.DataFrame: DataFrame with only the 'id' and 'nome' columns.
    """
    map_intrarregiao = {"UF": "estados", "regiao": "regioes", "municipio": "municipios"}

    if intrarregiao not in ["BR"]:
        url = f"{IBGE_API}/{map_intrarregiao[intrarregiao]}"
    else:
        url = f"{IBGE_API}/paises/brasil"

    response = requests.get(url)
    response.raise_for_status()

    locations = response.json()

    df = pd.json_normalize(locations).rename(columns={"nome": "name"})

    if "id.M49" in df.columns:
        df.rename(columns={"id.M49": "id"}, inplace=True)

        return df[["id", "name"]]

    if "microrregiao.id" in df.columns:
        df.rename(
            columns={
                "microrregiao.id": "microrregiao_id",
                "microrregiao.nome": "microrregiao_name",
                "microrregiao.mesorregiao.id": "mesorregiao_id",
                "microrregiao.mesorregiao.nome": "mesorregiao_name",
                "microrregiao.mesorregiao.UF.id": "uf_id",
                "microrregiao.mesorregiao.UF.sigla": "uf_sigla",
                "microrregiao.mesorregiao.UF.nome": "uf_name",
                "microrregiao.mesorregiao.UF.regiao.id": "regiao_id",
                "microrregiao.mesorregiao.UF.regiao.sigla": "regiao_sigla",
                "microrregiao.mesorregiao.UF.regiao.nome": "regiao_name",
            },
            inplace=True,
        )
        return df

    if "regiao.id" in df.columns:
        df.rename(
            columns={
                "regiao.id": "regiao_id",
                "regiao.sigla": "regiao_sigla",
                "regiao.nome": "regiao_name",
            },
            inplace=True,
        )
        return df

    return df[["id", "name"]]


def fetch_geojson_data(intrarregiao: Literal["BR", "UF", "regiao", "municipio"]) -> pd.DataFrame:
    """
    Fetches GeoJSON data for a given administrative level from IBGE.

    Args:
        intrarregiao: The administrative level ('BR', 'UF', 'regiao', 'municipio').

    Returns:
        A DataFrame containing the GeoJSON features, with coordinates stored as JSON strings.
    """
    params = {"qualidade": "intermediaria", "formato": "application/vnd.geo+json"}

    if intrarregiao not in ["BR"]:
        params["intrarregiao"] = intrarregiao

    response = requests.get(GEOJSON_API, params=params)
    response.raise_for_status()

    geojson = response.json()

    # Manually construct the DataFrame to prevent deep normalization of the 'geometry' object.
    # This avoids creating the problematic 'geometry.coordinates' column.
    records = []
    for feature in geojson.get("features", []):
        properties = feature.get("properties", {})
        # Keep the geometry object whole
        properties["geometry"] = feature.get("geometry")
        records.append(properties)

    if not records:
        return pd.DataFrame()

    df = pd.DataFrame(records)

    # Convert the raw geometry dictionary into a WKT string using shapely.
    # This is the standard format that PostGIS understands.
    if "geometry" in df.columns:
        df["geometry"] = df["geometry"].apply(lambda geom: shape(geom).wkt if geom and isinstance(geom, dict) else None)

    df.rename(columns={"codarea": "id"}, inplace=True)

    return df


def fetch_sidra_data(intrarregiao: Literal["BR", "UF", "regioes", "municipios"]) -> pd.DataFrame:
    """
    Fetch IBGE population data by municipality from the 2010 Demographic Census.

    This function uses the SIDRA API for table 1378 to get population data for all municipalities.
    Metadata: https://servicodados.ibge.gov.br/api/v3/agregados/1378/metadados

    Returns:
        pd.DataFrame: DataFrame with columns 'id', 'name', 'count', 'year'.

    N1 (Brasil), N2 (Região), N3 (Unidade da Federação), N8 (Mesorregião), N9 (Microrregião), N7 (Região metropolitana), N6 (Município), N10 (Distrito), N11 (Subdistrito), N102 (Bairro), N15 (Aglomeração urbana), N14 (Região Integrada de Desenvolvimento), N13 (Região metropolitana e subdivisão)

    Raises:
        requests.HTTPError: If the API request fails.
        KeyError: If the JSON structure is unexpected.
    """

    name_map = {"BR": "N1", "regiao": "N2", "UF": "N3", "municipio": "N6", "mesorregiao": "N8", "microregiao": "N9"}

    response = requests.get(SIDRA_API, params={"localidades": f"{name_map[intrarregiao]}[all]"})
    response.raise_for_status()

    data = response.json()

    try:
        # The data is nested within the JSON response
        series_data = data[0]["resultados"][0]["series"]
    except (IndexError, KeyError) as e:
        raise KeyError(f"Unexpected JSON structure from SIDRA API: {e}")

    records = []
    for item in series_data:
        localidade = item["localidade"]
        serie = item["serie"]

        # Population value for the year 2010
        population_str = serie.get("2010")

        # Some values might be '...' or '-' if not applicable, so we check if it's a digit
        if population_str and population_str.isdigit():
            records.append(
                {
                    "id": localidade.get("id"),
                    "name": localidade.get("nome"),
                    "count": int(population_str),
                    "year": 2010,
                }
            )

    df = pd.DataFrame(records)

    if not df.empty:
        df.rename(columns={"nome": "name"}, inplace=True)
        split_names = df["name"].str.rsplit(" - ", n=1, expand=True)  # Remove " - UF"
        df["id"] = df["id"].astype(str)
        df["name"] = split_names[0].str.strip()
        df["count"] = df["count"].astype("Int64")
        df["year"] = df["year"].astype("Int32")

    return df


def run_ingestion(years: list[int] | None = None, auto_optimize: bool = True, overwrite: bool = False):
    """
    Fetch and ingest raw data into the staging database.
    - SINASC: Live birth records
    - CNES: Healthcare establishment data
    - IBGE: Geographic boundaries (geojson), locations, and population data

    Args:
        overwrite (bool): If True, existing tables will be overwritten. Defaults to False.
        years (list[int] | None): List of SINASC years to ingest. If None, uses incremental mode
                                  (auto-detects missing years and ingests only those).
        auto_optimize (bool): If True, automatically runs optimization after ingestion. Defaults to True.
    """
    staging_engine = get_staging_db_engine()
    inspector = inspect(staging_engine)

    def ingest_data(table_name: str, fetch_func, *args):
        """Generic function to ingest data, checking for existence if not overwriting."""
        if not overwrite and inspector.has_table(table_name) and not auto_optimize:
            print(f"Table '{table_name}' already exists. Skipping ingestion.")

            return

        if file_exists(os.path.join(PATH, "data", "staging", f"{table_name}.csv")) and "sinasc" in table_name:
            print(f"Loading data for '{table_name}' from local CSV file...")

            df = pd.read_csv(os.path.join(PATH, "data", "staging", f"{table_name}.csv"), dtype=str)

            print(f"Loaded {len(df):,} records from local CSV for '{table_name}'.")

        else:
            print(f"Fetching data for '{table_name}'...")

            df: pd.DataFrame = fetch_func(*args)

            print(f"Loading {len(df):,} records into '{table_name}'...")

            # Save a local copy for faster future access
            df.to_csv(os.path.join(PATH, "data", "staging", f"{table_name}.csv"), index=False)

            print(f"Saved a local copy of '{table_name}' to CSV.")

        # If a 'geometry' column exists, convert it to a PostGIS-compatible format
        # using GeoAlchemy2's WKTElement.
        if "geometry" in df.columns:
            df["geometry"] = df["geometry"].apply(lambda wkt: WKTElement(wkt, srid=4674) if wkt else pd.NA)  # type: ignore
            dtype_map = {"geometry": Geometry}
            chunksize = 100_000

        else:
            dtype_map = None
            chunksize = 500_000

        df.to_sql(table_name, con=staging_engine, if_exists="replace", index=False, chunksize=chunksize, dtype=dtype_map)  # type: ignore

        print(f"✅ Loaded '{table_name}' into staging.")

    # Ingest SINASC data year by year
    # Determine which years to process
    existing_years = set()
    for table in inspector.get_table_names():
        if table.startswith("raw_sinasc_"):
            year_str = table.split("_")[-1]
            if year_str.isdigit():
                existing_years.add(int(year_str))

    if years is None:
        # Incremental mode: add only missing years
        all_years = range(2015, 2025)  # 2015-2025
        if overwrite:
            years_to_process = list(all_years)
            print(f"📊 Overwrite mode: Will process all years {years_to_process}")
        else:
            years_to_process = [y for y in all_years if y not in existing_years]

        if years_to_process:
            print(
                f"📊 Incremental mode: Found {len(existing_years)} existing years, adding {len(years_to_process)} new years: {years_to_process}"
            )
        else:
            print("✅ All years (2015-2025) already ingested. Use --overwrite to re-ingest.")
    else:
        years_to_process = years
        print(f"📊 Processing specified years: {years_to_process}")

    # Ingest each year
    for year in sorted(years_to_process, reverse=True):
        print(f"\n📅 Ingesting SINASC {year}...")
        ingest_data(f"raw_sinasc_{year}", fetch_sinasc_data, year)

    ingest_data("raw_cnes_establishments", fetch_cnes_data)

    name_map = {"BR": "brasil", "UF": "states", "regiao": "regions", "municipio": "municipalities"}

    for intrarregiao in {"BR", "UF", "regiao", "municipio"}:
        ingest_data(f"dim_ibge_id_{name_map[intrarregiao]}", fetch_ibge_id, intrarregiao)

        ingest_data(f"dim_ibge_geojson_{name_map[intrarregiao]}", fetch_geojson_data, intrarregiao)

        ingest_data(f"dim_ibge_population_{name_map[intrarregiao]}", fetch_sidra_data, intrarregiao)

    print("✨ Raw data ingestion complete.")

    # Auto-optimize if requested
    if auto_optimize and years_to_process:
        print("\n🔧 Starting automatic optimization (SQL mode for speed)...")
        try:
            from data.optimize import run_optimization

            run_optimization(years=years_to_process, overwrite=overwrite, use_sql=True)
        except ImportError:
            # Fallback to pandas-based optimization
            print("⚠️  SQL optimizer not found, using pandas mode...")
            from data.pandas.optimize import run_optimization

            run_optimization(years=years_to_process, overwrite=overwrite)
        print("✅ Optimization complete.")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Ingest raw SINASC, CNES, and IBGE data into the staging database.")
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="If set, existing tables will be dropped and re-ingested.",
    )
    parser.add_argument(
        "--years",
        type=int,
        nargs="+",
        help="Specific SINASC year(s) to ingest (e.g., --years 2024 2025). If not specified, uses incremental mode (auto-detects missing years).",
    )
    parser.add_argument(
        "--no-optimize",
        action="store_true",
        help="Skip automatic optimization after ingestion.",
    )
    args = parser.parse_args()

    run_ingestion(years=args.years, auto_optimize=not args.no_optimize, overwrite=args.overwrite)


if __name__ == "__main__":
    main()
