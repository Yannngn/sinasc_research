"""
Promotes data from a source (staging) database to a destination (production) database.

This script copies all fact, dimension, and aggregate tables, ensuring the
production environment has the latest clean data ready for the dashboard.
"""

import argparse
import os

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect


def get_tables_to_promote(engine):
    """Get a list of fact, dimension, and aggregate tables from the database."""
    inspector = inspect(engine)
    all_tables = inspector.get_table_names()
    return [tbl for tbl in all_tables if (tbl.startswith("dim_") or tbl.startswith("agg_")) and not tbl.endswith("_backup")]


def promote_data(source_url: str, dest_url: str):
    """Copies all relevant tables from a source database to a destination database."""
    source_engine = create_engine(source_url)
    dest_engine = create_engine(dest_url)

    print(f"Source:      {source_engine.url.database} on {source_engine.url.host}")
    print(f"Destination: {dest_engine.url.database} on {dest_engine.url.host}")

    tables = get_tables_to_promote(source_engine)
    if not tables:
        print("\n❌ No tables found to promote (fact_*, dim_*, agg_*). Exiting.")
        return

    print(f"\nFound {len(tables)} tables to promote:")
    for table in sorted(tables):
        print(f"  - {table}")

    for table in sorted(tables):
        print(f"\nPromoting table: {table}...")
        try:
            df = pd.read_sql_table(table, source_engine)
            print(f"  Read {len(df):,} rows from source.")

            df.to_sql(table, dest_engine, if_exists="replace", index=False, chunksize=10000)
            print(f"  ✅ Successfully wrote {len(df):,} rows to destination.")
        except Exception as e:
            print(f"  ❌ FAILED to promote table {table}: {e}")
            raise

    print("\n✨ Data promotion complete!")


def main():
    """Main execution function."""
    load_dotenv()
    parser = argparse.ArgumentParser(description="Promote data from staging to a production database.")
    parser.add_argument(
        "destination",
        choices=["local", "render"],
        help="The destination environment ('local' for local production, 'render' for cloud production).",
    )
    args = parser.parse_args()

    source_url = os.getenv("STAGING_DATABASE_URL")
    if args.destination == "local":
        dest_url = os.getenv("PROD_LOCAL_DATABASE_URL")
        print("🚀 Promoting data to LOCAL production database...")
    else:  # render
        dest_url = os.getenv("PROD_RENDER_DATABASE_URL")
        print("🚀 Promoting data to RENDER production database...")

    if not source_url or not dest_url:
        print("❌ Error: Database URLs not found in .env file.")
        print("   Please ensure STAGING_DATABASE_URL and PROD_..._DATABASE_URL are set.")
        return

    promote_data(source_url, dest_url)


if __name__ == "__main__":
    main()
