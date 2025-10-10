"""
Optimizes data types for tables in the staging database to reduce disk and memory usage.
...
"""

import argparse
from typing import Literal

import pandas as pd
from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine
from sqlalchemy.types import BigInteger, Date, Integer, SmallInteger, String

from data.database import get_staging_db_engine

# Defines the target data types for SINASC columns.
# Using nullable pandas dtypes (e.g., 'Int8') to handle potential missing values (pd.NA).
SINASC_OPTIMIZATION_SCHEMA = {
    # --- Identifiers and Codes (string) ---
    "CODESTAB": "string",
    "CODMUNNASC": "string",
    "CODOCUPMAE": "string",
    "CODMUNRES": "string",
    "CODANOMAL": "string",
    "UFINFORM": "string",
    "CODCART": "string",
    "NUMREGCART": "string",
    "CODPAISRES": "string",
    "NUMEROLOTE": "string",
    "VERSAOSIST": "string",
    "NATURALMAE": "string",
    "CODMUNNATU": "string",
    "CODMUNCART": "string",
    "CODUFNATU": "string",
    # --- Numeric ---
    "IDADEMAE": "Int8",
    "PESO": "Int16",
    "APGAR1": "Int8",
    "APGAR5": "Int8",
    "SEMAGESTAC": "Int8",
    "CONSPRENAT": "Int16",
    "QTDPARTNOR": "Int8",
    "QTDPARTCES": "Int8",
    "QTDFILVIVO": "Int8",
    "QTDFILMORT": "Int8",
    "DIFDATA": "Int16",
    "SERIESCMAE": "Int8",
    "QTDGESTANT": "Int8",
    "IDADEPAI": "Int8",
    "MESPRENAT": "Int8",
    # --- Dates ---
    "DTNASC": "date",
    "DTCADASTRO": "date",
    "DTRECEBIM": "date",
    "DTREGCART": "date",
    "DTRECORIG": "date",
    "DTNASCMAE": "date",
    "DTULTMENST": "date",
    "DTRECORIGA": "date",
    "DTDECLARAC": "date",
    "DTOPORT": "date",
    # --- Time ---
    "HORANASC": "string",  # Keeping as string for later processing (e.g., '1230', '0130')
    # --- Categorical ---
    "ORIGEM": "category",
    "LOCNASC": "category",
    "ESTCIVMAE": "category",
    "ESCMAE": "category",
    "GESTACAO": "category",
    "GRAVIDEZ": "category",
    "PARTO": "category",
    "CONSULTAS": "category",
    "SEXO": "category",
    "RACACOR": "category",
    "RACACORMAE": "category",
    "TPMETESTIM": "category",
    "TPAPRESENT": "category",
    "STTRABPART": "category",
    "STCESPARTO": "category",
    "TPROBSON": "category",
    "RACACOR_RN": "category",
    "RACACORN": "category",
    "ESCMAE2010": "category",
    "TPNASCASSI": "category",
    "ESCMAEAGR1": "category",
    "TPFUNCRESP": "category",
    "TPDOCRESP": "category",
    "KOTELCHUCK": "category",
    # --- Boolean ---
    "IDANOMAL": "boolean",
    "PARIDADE": "boolean",
    "STDNNOVA": "boolean",
    "STDNEPIDEM": "boolean",
}

IBGE_POPULATION_OPTIMIZATION_SCHEMA = {
    "id": "string",
    "name": "string",
    "count": "Int32",
    "year": "Int8",
}

CNES_OPTIMIZATION_SCHEMA = {
    "CO_CNES": "string",
    "CO_UNIDADE": "string",
    "CO_UF": "string",
    "CO_IBGE": "string",
    "NU_CNPJ_MANTENEDORA": "string",
    "NO_RAZAO_SOCIAL": "string",
    "NO_FANTASIA": "string",
    "CO_NATUREZA_ORGANIZACAO": "string",
    "DS_NATUREZA_ORGANIZACAO": "string",
    "TP_GESTAO": "string",  # category
    "CO_NIVEL_HIERARQUIA": "string",
    "DS_NIVEL_HIERARQUIA": "string",
    "CO_ESFERA_ADMINISTRATIVA": "string",  # category
    "DS_ESFERA_ADMINISTRATIVA": "string",
    "CO_ATIVIDADE": "category",
    "TP_UNIDADE": "category",
    "CO_CEP": "string",
    "NU_LOGRADOURO": "string",
    "NU_ENDERECO": "string",
    "NO_BAIRRO": "string",
    "NU_TELEFONE": "string",
    "NU_LONGITUDE": "float64",
    "NU_LATITUDE": "float64",
    "CO_TURNO_ATENDIMENTO": "category",
    "DS_TURNO_ATENDIMENTO": "string",
    "NU_CNPJ": "string",
    "NO_EMAIL": "string",
    "CO_NATUREZA_JUR": "category",
    "ST_CENTRO_CIRURGICO": "boolean",
    "ST_CENTRO_OBSTETRICO": "boolean",
    "ST_CENTRO_NEONATAL": "boolean",
    "ST_ATEND_HOSPITALAR": "boolean",
    "ST_SERVICO_APOIO": "boolean",
    "ST_ATEND_AMBULATORIAL": "boolean",
    "CO_MOTIVO_DESAB": "category",
    "CO_AMBULATORIAL_SUS": "boolean",
}


# Mapping from pandas dtypes in the schema to specific SQLAlchemy types for PostgreSQL.
PANDAS_TO_SQLALCHEMY_MAP = {
    "Int8": SmallInteger,
    "Int16": SmallInteger,
    "Int32": Integer,
    "Int64": BigInteger,  # Defaulting to BigInteger for larger values
    "date": Date,
    "string": String,
    "category": String,  # Categories are stored as strings in the database
}


def _optimize_chunk(column: pd.Series, dtype: str):
    if dtype == "date":
        return pd.to_datetime(column, format="%d%m%Y", errors="coerce").dt.date

    if dtype == "category":
        # Convert to numeric, which may result in a float dtype (e.g., for "1.0" or NaNs).
        numeric_col = pd.to_numeric(column, errors="coerce")
        if pd.api.types.is_numeric_dtype(numeric_col.dtype):
            numeric_col = numeric_col.astype("Int32").astype("Int8")
        return numeric_col.astype("category")

    if dtype == "string":
        return column.astype("string")

    if dtype == "boolean":
        if "SIM" in column.unique() or "NÃO" in column.unique() or "NAO" in column.unique():
            # Handle "SIM"/"NÃO" or "SIM"/"NAO" strings
            column = column.map({"SIM": True, "NÃO": False, "NAO": False, "": pd.NA}).astype("boolean")
            return column
        # Coerce to numeric to handle columns read as objects.
        numeric_col = pd.to_numeric(column, errors="coerce")

        # Check for SINASC-style boolean (1=True, 2=False) vs. standard (1=True, 0=False).
        # The presence of 2 indicates the former.
        if 2 in numeric_col.unique():
            # Map 1->True, 2->False. Values like 9 (Ignorado) become NA.
            column = numeric_col.map({1: True, 2: False, 9: pd.NA})
        else:
            # For standard 0/1 data, use the numeric column directly.
            column = numeric_col

        # Convert to nullable boolean type to support True, False, and pd.NA.
        return column.astype("boolean")

    column = column.astype("string")
    column = pd.to_numeric(column, errors="coerce")
    column = column.astype(dtype).replace({99: pd.NA})  # type: ignore

    return column


def optimize_sinasc_table(engine: Engine, year: int, overwrite: bool = False, chunksize: int = 500_000):
    """
    Reads a raw SINASC table, optimizes data types, and saves the result.

    Args:
        engine: The SQLAlchemy engine for the staging database.
        year: The year of the SINASC table to process.
        overwrite: If True, replaces the raw table with the optimized version.
                   If False, creates a new 'optimized_' table.
        chunksize: The number of rows to process in each chunk to manage memory usage.
    """
    raw_table_name = f"raw_sinasc_{year}"

    if overwrite:
        # Use a temporary table for the intermediate result to ensure a safe swap
        dest_table_name = f"temp_optimized_sinasc_{year}"
        print(f"Optimizing table '{raw_table_name}' in-place (via temporary table)...")
    else:
        dest_table_name = f"optimized_sinasc_{year}"
        print(f"Optimizing table '{raw_table_name}' -> '{dest_table_name}'...")

    try:
        iterator = pd.read_sql_table(raw_table_name, engine, chunksize=chunksize)
    except ValueError as e:
        print(f"Could not read table '{raw_table_name}'. Skipping. Error: {e}")
        return

    is_first_chunk = True
    total_rows = 0
    dtype_map = {}

    for chunk in iterator:
        # On the first chunk, build the dtype map for SQLAlchemy
        if is_first_chunk:
            for col, dtype in SINASC_OPTIMIZATION_SCHEMA.items():
                if col in chunk.columns:
                    sql_type = PANDAS_TO_SQLALCHEMY_MAP.get(dtype)
                    if sql_type:
                        dtype_map[col] = sql_type

        for col, dtype in SINASC_OPTIMIZATION_SCHEMA.items():
            if col not in chunk.columns:
                continue

            chunk[col] = _optimize_chunk(chunk[col], dtype)

        write_mode = "replace" if is_first_chunk else "append"
        chunk.to_sql(dest_table_name, engine, if_exists=write_mode, index=False, dtype=dtype_map)

        is_first_chunk = False
        total_rows += len(chunk)
        print(f"  ... processed chunk, {total_rows:,} total rows written.")

    # If overwriting, perform the atomic swap after the temporary table is fully created
    if overwrite:
        print("  ... swapping original table with optimized version.")
        with engine.connect() as connection:
            with connection.begin():  # Start a transaction
                connection.execute(text(f"DROP TABLE IF EXISTS {raw_table_name};"))
                connection.execute(text(f"ALTER TABLE {dest_table_name} RENAME TO {raw_table_name};"))
        print(f"✅ Finished optimizing and overwriting '{raw_table_name}'. Total rows: {total_rows:,}")
    else:
        print(f"✅ Finished creating '{dest_table_name}'. Total rows: {total_rows:,}")


def optimize_ibge_population_table(
    engine: Engine, location: Literal["brasil", "states", "regions", "municipalities"], overwrite: bool = False, chunksize: int = 1_000_000
):
    raw_table_name = f"raw_ibge_{location}_population"
    dest_table_name = f"optimized_ibge_{location}_population" if not overwrite else f"temp_optimized_ibge_{location}_population"

    try:
        iterator = pd.read_sql_table(raw_table_name, engine, chunksize=chunksize)
    except ValueError as e:
        print(f"Could not read table '{raw_table_name}'. Skipping. Error: {e}")
        return

    is_first_chunk = True
    total_rows = 0
    dtype_map = {}

    for chunk in iterator:
        # On the first chunk, build the dtype map for SQLAlchemy
        if is_first_chunk:
            for col, dtype in IBGE_POPULATION_OPTIMIZATION_SCHEMA.items():
                if col in chunk.columns:
                    sql_type = PANDAS_TO_SQLALCHEMY_MAP.get(dtype)
                    if sql_type:
                        dtype_map[col] = sql_type

        for col, dtype in IBGE_POPULATION_OPTIMIZATION_SCHEMA.items():
            if col not in chunk.columns:
                continue

            chunk[col] = _optimize_chunk(chunk[col], dtype)

        write_mode = "replace" if is_first_chunk else "append"
        chunk.to_sql(dest_table_name, engine, if_exists=write_mode, index=False, dtype=dtype_map)

        is_first_chunk = False
        total_rows += len(chunk)
        print(f"  ... processed chunk, {total_rows:,} total rows written.")

    # If overwriting, perform the atomic swap after the temporary table is fully created
    if overwrite:
        print("  ... swapping original table with optimized version.")
        with engine.connect() as connection:
            with connection.begin():  # Start a transaction
                connection.execute(text(f"DROP TABLE IF EXISTS {raw_table_name};"))
                connection.execute(text(f"ALTER TABLE {dest_table_name} RENAME TO {raw_table_name};"))
        print(f"✅ Finished optimizing and overwriting '{raw_table_name}'. Total rows: {total_rows:,}")
    else:
        print(f"✅ Finished creating '{dest_table_name}'. Total rows: {total_rows:,}")


def optimize_cnes_table(engine: Engine, overwrite: bool = False, chunksize: int = 1_000_000):
    raw_table_name = "raw_cnes_establishments"
    dest_table_name = "optimized_cnes_establishments" if not overwrite else "temp_optimized_cnes_establishments"

    try:
        iterator = pd.read_sql_table(raw_table_name, engine, chunksize=chunksize)
    except ValueError as e:
        print(f"Could not read table '{raw_table_name}'. Skipping. Error: {e}")
        return

    is_first_chunk = True
    total_rows = 0
    dtype_map = {}

    for chunk in iterator:
        # On the first chunk, build the dtype map for SQLAlchemy
        if is_first_chunk:
            for col, dtype in CNES_OPTIMIZATION_SCHEMA.items():
                if col in chunk.columns:
                    sql_type = PANDAS_TO_SQLALCHEMY_MAP.get(dtype)
                    if sql_type:
                        dtype_map[col] = sql_type

        for col, dtype in CNES_OPTIMIZATION_SCHEMA.items():
            if col not in chunk.columns:
                continue

            chunk[col] = _optimize_chunk(chunk[col], dtype)

        write_mode = "replace" if is_first_chunk else "append"
        chunk.to_sql(dest_table_name, engine, if_exists=write_mode, index=False, dtype=dtype_map)

        is_first_chunk = False
        total_rows += len(chunk)
        print(f"  ... processed chunk, {total_rows:,} total rows written.")

    # If overwriting, perform the atomic swap after the temporary table is fully created
    if overwrite:
        print("  ... swapping original table with optimized version.")
        with engine.connect() as connection:
            with connection.begin():  # Start a transaction
                connection.execute(text(f"DROP TABLE IF EXISTS {raw_table_name};"))
                connection.execute(text(f"ALTER TABLE {dest_table_name} RENAME TO {raw_table_name};"))
        print(f"✅ Finished optimizing and overwriting '{raw_table_name}'. Total rows: {total_rows:,}")
    else:
        print(f"✅ Finished creating '{dest_table_name}'. Total rows: {total_rows:,}")


def optimize_ibge_id_table(
    engine: Engine, location: Literal["brasil", "states", "regions", "municipalities"], overwrite: bool = False, chunksize: int = 100_000
):
    """
    Optimizes the IBGE ID mapping table by converting all columns to string type.

    Args:
        engine: The SQLAlchemy engine for the staging database.
        overwrite: If True, replaces the raw table with the optimized version.
                   If False, creates a new 'optimized_' table.
        chunksize: The number of rows to process in each chunk.
    """
    raw_table_name = f"raw_ibge_{location}_id"
    if overwrite:
        dest_table_name = f"temp_optimized_ibge_{location}_id"
        print(f"Optimizing table '{raw_table_name}' in-place (via temporary table)...")
    else:
        dest_table_name = f"optimized_ibge_{location}_id"
        print(f"Optimizing table '{raw_table_name}' -> '{dest_table_name}'...")

    try:
        iterator = pd.read_sql_table(raw_table_name, engine, chunksize=chunksize)
    except ValueError as e:
        print(f"Could not read table '{raw_table_name}'. Skipping. Error: {e}")
        return

    is_first_chunk = True
    total_rows = 0
    dtype_map = {}

    for chunk in iterator:
        if is_first_chunk:
            dtype_map = {col: String for col in chunk.columns}

        for col in chunk.columns:
            numeric_as_int_str = pd.to_numeric(chunk[col], errors="coerce").astype("Int64").astype("string")
            chunk[col] = numeric_as_int_str.fillna(chunk[col].astype("string"))

        write_mode = "replace" if is_first_chunk else "append"
        chunk.to_sql(dest_table_name, engine, if_exists=write_mode, index=False, dtype=dtype_map)  # type: ignore

        is_first_chunk = False
        total_rows += len(chunk)
        print(f"  ... processed chunk, {total_rows:,} total rows written.")

    if overwrite:
        print("  ... swapping original table with optimized version.")
        with engine.connect() as connection:
            with connection.begin():
                connection.execute(text(f"DROP TABLE IF EXISTS {raw_table_name};"))
                connection.execute(text(f"ALTER TABLE {dest_table_name} RENAME TO {raw_table_name};"))
        print(f"✅ Finished optimizing and overwriting '{raw_table_name}'. Total rows: {total_rows:,}")
    else:
        print(f"✅ Finished creating '{dest_table_name}'. Total rows: {total_rows:,}")


def run_optimization(years: list[int] | None = None, overwrite: bool = False):
    """
    Main function to run the optimization process for specified years.

    Args:
        years: A list of specific years to optimize. If None, all available years are optimized.
        overwrite: If True, raw tables are replaced. If False, new tables are created.
    """
    engine = get_staging_db_engine()

    if not years:
        print("No years specified. Discovering SINASC tables in the database...")
        inspector = inspect(engine)
        all_tables = inspector.get_table_names()
        years = sorted(
            [int(table.split("_")[-1]) for table in all_tables if table.startswith("raw_sinasc_") and table.split("_")[-1].isdigit()]
        )
        print(f"Found SINASC tables for years: {years}")

    # for year in years:
    #     optimize_sinasc_table(engine, year, overwrite=overwrite)

    for location in ["brasil", "states", "regions", "municipalities"]:
        #     optimize_ibge_population_table(engine, location=location, overwrite=overwrite)  # type: ignore
        optimize_ibge_id_table(engine, location=location, overwrite=overwrite)  # type: ignore

    # optimize_cnes_table(engine, overwrite=overwrite)
    print("✨ Optimization process complete.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Optimize data types for tables in the staging database to reduce disk and memory usage.")
    parser.add_argument(
        "--year",
        type=int,
        nargs="+",
        help="Specific year(s) to optimize. If not provided, all found 'raw_sinasc' tables will be optimized.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="If set, overwrites the raw tables with their optimized versions instead of creating new tables.",
    )
    args = parser.parse_args()

    run_optimization(years=args.year, overwrite=args.overwrite)
