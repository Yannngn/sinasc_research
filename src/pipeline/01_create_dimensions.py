"""
Pipeline Step 01: Create and populate all dimension tables.

This script reads data from various raw sources in the staging database
and creates clean, final dimension tables that will be used for joins
and analysis.

It creates two types of dimensions:
1. Geographic Dimensions: `dim_state` and `dim_municipality` from raw IBGE tables.
2. Categorical Dimensions: `dim_*` tables from SINASC value mappings.
"""

import argparse
import os
import sys

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import Engine, create_engine

# Add src to the Python path to allow importing from 'utils'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
try:
    from utils.sinasc_definitions import VALUE_MAPPINGS
except ImportError:
    print("Error: Could not import VALUE_MAPPINGS. Ensure src/utils/sinasc_definitions.py exists.")
    sys.exit(1)


def create_geo_dimensions(engine: Engine):
    """
    Create geographic dimension tables from raw IBGE data.

    Reads from `raw_ibge_states` and `raw_ibge_municipalities` to create
    clean `dim_state` and `dim_municipality` tables.

    Args:
        engine: SQLAlchemy engine connected to the staging database.
    """
    print("\n--- Creating Geographic Dimensions ---")

    # --- Create dim_state ---
    try:
        print("Creating table: dim_state")
        df_states = pd.read_sql("SELECT * FROM raw_ibge_states", engine)

        dim_states = df_states[["id", "sigla", "nome", "regiao_nome"]].rename(
            columns={
                "id": "state_code",
                "sigla": "state_abbr",
                "nome": "state_name",
            }
        )
        dim_states["state_code"] = dim_states["state_code"].astype(str)

        dim_states.to_sql("dim_state", engine, if_exists="replace", index=False)
        print(f"  ✅ Successfully created dim_state with {len(dim_states)} records.")
    except Exception as e:
        print(f"  ❌ FAILED to create dim_state. Error: {e}")
        raise

    # --- Create dim_municipality ---
    try:
        print("Creating table: dim_municipality")
        df_mun = pd.read_sql("SELECT * FROM raw_ibge_municipalities", engine)

        dim_mun = df_mun[["id", "nome", "uf_id", "uf_sigla", "uf_nome", "regiao_nome"]].rename(
            columns={
                "id": "municipality_code",
                "nome": "municipality_name",
                "uf_id": "state_code",
                "uf_sigla": "state_abbr",
                "uf_nome": "state_name",
            }
        )
        dim_mun["municipality_code"] = dim_mun["municipality_code"].astype(str)
        dim_mun["state_code"] = dim_mun["state_code"].astype(str)

        dim_mun.to_sql("dim_municipality", engine, if_exists="replace", index=False)
        print(f"  ✅ Successfully created dim_municipality with {len(dim_mun)} records.")
    except Exception as e:
        print(f"  ❌ FAILED to create dim_municipality. Error: {e}")
        raise


def create_categorical_dimensions(engine: Engine):
    """
    Create dimension tables for all SINASC categorical variables.

    Iterates through the VALUE_MAPPINGS dictionary and creates a separate
    dimension table for each entry (e.g., `dim_parto`, `dim_escmae`).

    Args:
        engine: SQLAlchemy engine connected to the staging database.
    """
    print("\n--- Creating Categorical Dimensions ---")
    created_count = 0
    for category_name, mappings in VALUE_MAPPINGS.items():
        dim_table_name = f"dim_{category_name.lower()}"
        print(f"Creating table: {dim_table_name}")

        try:
            df = pd.DataFrame(list(mappings.items()), columns=["id", "name"])
            df["id"] = df["id"].astype(str)

            df.to_sql(dim_table_name, con=engine, if_exists="replace", index=False)
            created_count += 1
        except Exception as e:
            print(f"  ❌ FAILED to create {dim_table_name}. Error: {e}")
            continue
    print(f"\n  ✅ Successfully created {created_count} categorical dimension tables.")


def main():
    """Main execution function to run the dimension creation pipeline."""
    load_dotenv()
    parser = argparse.ArgumentParser(description="Create and populate dimension tables in the staging database.")
    parser.add_argument(
        "--db_url",
        default=os.getenv("STAGING_DATABASE_URL"),
        help="Database connection URL for the staging environment.",
    )
    args = parser.parse_args()

    if not args.db_url:
        raise ValueError("Database URL not provided. Set STAGING_DATABASE_URL in .env or pass --db_url.")

    print("🚀 Starting dimension creation pipeline...")
    print(f"Connecting to database: {args.db_url.split('@')[-1]}")
    engine = create_engine(args.db_url)

    create_geo_dimensions(engine)
    create_categorical_dimensions(engine)

    print("\n✨ Dimension creation process finished successfully!")


if __name__ == "__main__":
    main()
