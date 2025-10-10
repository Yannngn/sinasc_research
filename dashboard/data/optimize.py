"""
Optimizes data types for tables in the staging database to reduce disk and memory usage.
OPTIMIZED VERSION using direct SQL instead of pandas for 10-100x better performance.

This script provides two approaches:
1. optimize_*_table_sql() - Direct SQL optimization (fast, recommended)
2. optimize_*_table() - Pandas-based optimization (slower, fallback for complex transformations)
"""

import argparse
import os
import sys

from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine
from sqlalchemy.types import BigInteger, Date, Integer, SmallInteger, String

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir))

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
    "OPORT_DN": "string",
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

CNES_ID_SCHEMA = {}

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


def _build_sql_cast_expression(col_name: str, dtype: str, table_name: str) -> str:
    """
    Build SQL CAST expression for a column based on target dtype.

    Args:
        col_name: Column name
        dtype: Target dtype from SINASC_OPTIMIZATION_SCHEMA
        table_name: Source table name (for checking column existence)

    Returns:
        SQL expression for casting the column
    """
    if dtype == "date":
        # Convert DDMMYYYY string to DATE
        return f"TO_DATE(NULLIF(\"{col_name}\", ''), 'DDMMYYYY') AS \"{col_name}\""

    elif dtype in ["Int8", "Int16", "Int32"]:
        # Convert to integer, handling NULL values and invalid codes (99, 999, etc.)
        sql_type = "SMALLINT" if dtype in ["Int8", "Int16"] else "INTEGER"
        # Replace common "unknown" codes with NULL
        return f'NULLIF(NULLIF("{col_name}"::TEXT, \'99\')::INTEGER, 9999)::{sql_type} AS "{col_name}"'

    elif dtype == "string":
        # Keep as TEXT
        return f'"{col_name}"::TEXT AS "{col_name}"'

    elif dtype == "category":
        # Columns that should receive '11' when NULL/empty (others will receive '9')
        ELEVEN_NULL_COLUMNS = {"TPROBSON"}

        null_replacement = "11" if col_name in ELEVEN_NULL_COLUMNS else "9"

        return (
            f"CASE "
            f"WHEN \"{col_name}\" IS NULL OR trim(\"{col_name}\"::TEXT) = '' THEN '{null_replacement}' "
            f"ELSE COALESCE(NULLIF(regexp_replace(trim(\"{col_name}\"::TEXT), '^0+', ''), ''), '0') "
            f'END AS "{col_name}"'
        )

    elif dtype == "boolean":
        # Determine mapping based on whether '2' appears in the column values for the table.
        # If any row contains '2' we treat 1='yes' and 2='no'. Otherwise assume 0/1 mapping (0=no, 1=yes).
        return f"""
        CASE
            WHEN (SELECT COUNT(1) FROM {table_name} WHERE \"{col_name}\" IS NOT NULL AND \"{col_name}\"::TEXT = '2') > 0 THEN
                CASE
                    WHEN \"{col_name}\"::TEXT IN ('1') THEN TRUE
                    WHEN \"{col_name}\"::TEXT IN ('2') THEN FALSE
                    ELSE NULL
                END
            ELSE
                CASE
                    WHEN \"{col_name}\"::TEXT IN ('1', 'SIM') THEN TRUE
                    WHEN \"{col_name}\"::TEXT IN ('0', 'NAO', 'NÃO') THEN FALSE
                    ELSE NULL
                END
        END AS \"{col_name}\"
        """.strip()

    elif dtype == "float64":
        return f'"{col_name}"::DOUBLE PRECISION AS "{col_name}"'

    else:
        # Default: keep as is
        return f'"{col_name}"'


def optimize_sinasc_table_sql(engine: Engine, year: int, overwrite: bool = False):
    """
    Optimizes SINASC table using direct SQL (10-100x faster than pandas).

    Args:
        engine: The SQLAlchemy engine for the staging database.
        year: The year of the SINASC table to process.
        overwrite: If True, replaces the raw table with the optimized version.
                   If False, creates a new 'optimized_' table.
    """
    raw_table_name = f"raw_sinasc_{year}"

    if overwrite:
        dest_table_name = f"temp_optimized_sinasc_{year}"
        print(f"🔧 Optimizing '{raw_table_name}' in-place (via temporary table) using SQL...")
    else:
        dest_table_name = f"optimized_sinasc_{year}"
        print(f"🔧 Optimizing '{raw_table_name}' -> '{dest_table_name}' using SQL...")

    # Get existing columns from raw table
    inspector = inspect(engine)
    try:
        raw_columns = [col["name"] for col in inspector.get_columns(raw_table_name)]
    except Exception as e:
        print(f"  ❌ Could not read table '{raw_table_name}'. Error: {e}")
        return

    # Build SELECT statement with CAST expressions
    select_expressions = []
    for col in raw_columns:
        if col in SINASC_OPTIMIZATION_SCHEMA:
            dtype = SINASC_OPTIMIZATION_SCHEMA[col]
            select_expressions.append(_build_sql_cast_expression(col, dtype, raw_table_name))
        else:
            # Column not in schema, keep as is
            select_expressions.append(col)

    select_clause = ",\n    ".join(select_expressions)

    # Execute optimization in single SQL statement
    with engine.begin() as conn:
        # Drop destination table if exists
        conn.execute(text(f"DROP TABLE IF EXISTS {dest_table_name}"))

        # Create optimized table with proper types
        create_sql = f"""
        CREATE TABLE {dest_table_name} AS
        SELECT 
            {select_clause}
        FROM {raw_table_name}
        WHERE \"DTNASC\" IS NOT NULL AND \"DTNASC\" != ''
        """

        print("  Executing SQL optimization...")
        conn.execute(text(create_sql))

        # Get row count
        count_result = conn.execute(text(f"SELECT COUNT(*) FROM {dest_table_name}"))
        row_count = count_result.scalar()
        print(f"  ✅ Created {dest_table_name} with {row_count:,} rows")

        # Create indexes for common query columns
        print("  Creating indexes...")
        index_columns = ["DTNASC", "CODMUNNASC", "CODMUNRES", "CODESTAB", "PARTO", "RACACOR"]
        for idx_col in index_columns:
            if idx_col in raw_columns:
                try:
                    conn.execute(
                        text(f"""
                        CREATE INDEX idx_{dest_table_name}_{idx_col.lower()} 
                        ON {dest_table_name}("{idx_col}")
                    """)
                    )
                    print(f"    - Index on {idx_col}")
                except Exception as e:
                    print(f"    ⚠️  Could not create index on {idx_col}: {e}")

    # If overwriting, perform atomic swap
    if overwrite:
        print("  Swapping tables...")
        with engine.begin() as conn:
            conn.execute(text(f"DROP TABLE IF EXISTS {raw_table_name}"))
            conn.execute(text(f"ALTER TABLE {dest_table_name} RENAME TO {raw_table_name}"))
        print(f"✅ Optimized and replaced '{raw_table_name}'. Total rows: {row_count:,}")
    else:
        print(f"✅ Created '{dest_table_name}'. Total rows: {row_count:,}")


def optimize_sinasc_table_pandas(engine: Engine, year: int, overwrite: bool = False, chunksize: int = 500_000):
    """
    FALLBACK: Pandas-based optimization (slower but handles complex transformations).
    Use optimize_sinasc_table_sql() for better performance.
    """
    from dashboard.data.pandas.optimize import optimize_sinasc_table as legacy_optimize

    print("⚠️  Using pandas-based optimization (slower). Consider using SQL mode.")
    legacy_optimize(engine, year, overwrite, chunksize)


def run_optimization(years: list[int] | None = None, overwrite: bool = False, use_sql: bool = True):
    """
    Main function to run the optimization process for specified years.

    Args:
        years: A list of specific years to optimize. If None, all available years are optimized.
        overwrite: If True, raw tables are replaced. If False, new tables are created.
        use_sql: If True, uses direct SQL optimization (fast). If False, uses pandas (slow).
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

    if not years:
        print("⚠️  No SINASC tables found to optimize.")
        return

    print(f"\n{'=' * 60}")
    print(f"Optimization mode: {'🚀 SQL (fast)' if use_sql else '🐢 Pandas (slow)'}")
    print(f"Years to process: {years}")
    print(f"Overwrite mode: {overwrite}")
    print(f"{'=' * 60}\n")

    for year in years:
        if use_sql:
            optimize_sinasc_table_sql(engine, year, overwrite=overwrite)
        else:
            optimize_sinasc_table_pandas(engine, year, overwrite=overwrite)


def create_dim_health_facility_sql(engine: Engine, overwrite: bool = False):
    """
    Create a canonical `dim_health_facility` table derived from `raw_cnes_establishments`.

    This uses a single SQL statement to select distinct facility identifiers and
    normalize commonly used columns. It is safe to run multiple times; use
    `overwrite=True` to replace an existing dim table atomically.
    """
    raw_table = "raw_cnes_establishments"
    dest_table = "dim_health_facility"

    print(f"🔧 Building '{dest_table}' from '{raw_table}' (overwrite={overwrite})...")

    inspector = inspect(engine)
    try:
        _cols = [c["name"] for c in inspector.get_columns(raw_table)]
    except Exception as e:
        print(f"  ❌ Could not read table '{raw_table}'. Error: {e}")
        return

    # Basic column selection - map common CNES source columns to canonical dim columns
    select_columns = []

    select_columns.append('"CO_CNES"::TEXT as cnes_code')
    select_columns.append('"NO_FANTASIA" as facility_name')
    select_columns.append('"CO_UF" as state_id')
    select_columns.append('"CO_IBGE" as municipality_code')
    select_columns.append('"CO_NATUREZA_JUR" as legal_nature')
    select_columns.append(
        "CASE "
        "WHEN NULLIF(trim(\"ST_CENTRO_OBSTETRICO\"::TEXT), '') IS NULL THEN NULL "
        "WHEN upper(trim(\"ST_CENTRO_OBSTETRICO\"::TEXT)) IN ('1','1.0') THEN TRUE "
        "WHEN upper(trim(\"ST_CENTRO_OBSTETRICO\"::TEXT)) IN ('0','0.0') THEN FALSE "
        "ELSE NULL END AS has_obstetric_center"
    )

    select_columns.append("NULLIF(\"NU_LONGITUDE\", '')::DOUBLE PRECISION as longitude")
    select_columns.append("NULLIF(\"NU_LATITUDE\", '')::DOUBLE PRECISION as latitude")

    # Ensure we have at least the code and a name
    if not any(s.startswith('"CO_CNES"') for s in select_columns):
        print("  ❌ raw_cnes_establishments doesn't contain a CNES identifier column (CO_CNES). Aborting.")
        return

    select_clause = ",\n        ".join(select_columns)

    create_sql = f"""
    CREATE TABLE {dest_table} AS
    SELECT DISTINCT
        {select_clause}
    FROM {raw_table}
    WHERE \"CO_CNES\" IS NOT NULL AND \"CO_CNES\" != ''
    """

    # Execute creation
    with engine.begin() as conn:
        if overwrite:
            temp_table = f"{dest_table}_tmp"
            conn.execute(text(f"DROP TABLE IF EXISTS {temp_table}"))
            conn.execute(text(create_sql.replace(f"CREATE TABLE {dest_table} AS", f"CREATE TABLE {temp_table} AS")))
            conn.execute(text(f"DROP TABLE IF EXISTS {dest_table}"))
            conn.execute(text(f"ALTER TABLE {temp_table} RENAME TO {dest_table}"))
            print(f"  ✅ Replaced existing '{dest_table}'")
        else:
            conn.execute(text(f"DROP TABLE IF EXISTS {dest_table}"))
            conn.execute(text(create_sql))
            print(f"  ✅ Created '{dest_table}'")

        # Create some indexes
        try:
            conn.execute(text(f"CREATE INDEX IF NOT EXISTS idx_{dest_table}_cnes_code ON {dest_table}(cnes_code)"))
            if any("municipality_code" in s for s in select_columns):
                conn.execute(text(f"CREATE INDEX IF NOT EXISTS idx_{dest_table}_municipality ON {dest_table}(municipality_code)"))
            print("  ✅ Indexes created")
        except Exception as e:
            print(f"  ⚠️ Could not create indexes: {e}")

    print("\n✨ Optimization process complete.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Optimize data types for tables in the staging database (SQL-optimized version).")
    parser.add_argument(
        "--years",
        type=int,
        nargs="+",
        help="Specific year(s) to optimize. If not provided, all found 'raw_sinasc' tables will be optimized.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="If set, overwrites the raw tables with their optimized versions instead of creating new tables.",
    )
    parser.add_argument(
        "--pandas",
        action="store_true",
        help="Use pandas-based optimization instead of SQL (slower but safer for complex cases).",
    )
    parser.add_argument(
        "--create-dim-health-facility",
        action="store_true",
        help="Create dim_health_facility table from raw_cnes_establishments.",
    )
    args = parser.parse_args()

    if args.create_dim_health_facility:
        engine = get_staging_db_engine()
        create_dim_health_facility_sql(engine, overwrite=args.overwrite)
    else:
        run_optimization(years=args.years, overwrite=args.overwrite, use_sql=not args.pandas)
