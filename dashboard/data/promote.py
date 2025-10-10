"""
Promotes data from a source (staging) database to a destination (production) database.

This script copies all fact, dimension, and aggregate tables, ensuring the
production environment has the latest clean data ready for the dashboard.

Uses pandas for reliable cross-database promotion. PostgreSQL doesn't support
cross-database queries natively, so pandas is the most reliable approach.
"""

import argparse
import os

import pandas as pd
from dotenv import load_dotenv
from geoalchemy2.types import Geometry
from geopandas import GeoDataFrame
from sqlalchemy import create_engine, inspect


def get_tables_to_promote(engine, scope: str = "all"):
    """
    Get a list of dimension and aggregate tables from the database based on scope.

    Args:
        engine: SQLAlchemy engine for the source database.
        scope: The scope of tables to promote ('all', 'dim', or 'agg').

    Note: Fact tables (fact_births) are excluded - too large for production.
    The dashboard uses pre-aggregated tables instead for performance.
    """
    inspector = inspect(engine)
    all_tables = inspector.get_table_names()

    # Filter out backup tables first
    filtered_tables = [tbl for tbl in all_tables if not tbl.endswith("_backup")]

    if scope == "dim":
        return [tbl for tbl in filtered_tables if tbl.startswith("dim_")]
    elif scope == "agg":
        return [tbl for tbl in filtered_tables if tbl.startswith("agg_")]
    else:  # 'all'
        return [tbl for tbl in filtered_tables if tbl.startswith("dim_") or tbl.startswith("agg_")]


def promote_data(source_url: str, dest_url: str, use_pandas: bool = True, scope: str = "all"):
    """
    Copies all relevant tables from a source database to a destination database.

    Args:
        source_url: Connection string for staging database
        dest_url: Connection string for production database
        use_pandas: Uses pandas-based copy (reliable for all PostgreSQL scenarios).
                   PostgreSQL doesn't support cross-database queries.
        scope: The scope of tables to promote ('all', 'dim', or 'agg').
    """
    source_engine = create_engine(source_url)
    dest_engine = create_engine(dest_url)

    print(f"Source:      {source_engine.url.database} on {source_engine.url.host}")
    print(f"Destination: {dest_engine.url.database} on {dest_engine.url.host}")
    print(f"Scope:       Promoting '{scope}' tables")

    tables = get_tables_to_promote(source_engine, scope=scope)
    if not tables:
        print(f"\n❌ No tables found to promote for scope '{scope}' (dim_*, agg_*). Exiting.")
        return

    # Categorize tables for better display
    dim_tables = [t for t in tables if t.startswith("dim_")]
    agg_tables = [t for t in tables if t.startswith("agg_")]

    print(f"\nFound {len(tables)} tables to promote:")
    print("⚠️  Note: Fact tables (fact_births ~27M rows) are excluded - too large for production.")
    print("    Dashboard uses pre-aggregated tables for performance.\n")

    if dim_tables:
        print(f"  📐 Dimension Tables ({len(dim_tables)}):")
        for table in sorted(dim_tables):
            print(f"    - {table}")
    if agg_tables:
        print(f"\n  📈 Aggregate Tables ({len(agg_tables)}):")
        for table in sorted(agg_tables):
            print(f"    - {table}")

    # PostgreSQL doesn't support cross-database queries, so we always use pandas
    # Even for same-host scenarios with different databases
    print("\n📦 Using pandas-based copy for reliable cross-database promotion...")
    if not use_pandas:
        print("⚠️  Note: --pandas flag is always used. PostgreSQL doesn't support cross-database queries.")
    _promote_pandas(source_engine, dest_engine, tables)

    # Summary
    dim_count = len([t for t in tables if t.startswith("dim_")])
    agg_count = len([t for t in tables if t.startswith("agg_")])

    print("\n" + "=" * 60)
    print("✨ Data promotion complete!")
    print("=" * 60)
    print(f" Dimension tables promoted: {dim_count}")
    print(f"📈 Aggregate tables promoted: {agg_count}")
    print(f"📦 Total tables promoted:     {len(tables)}")
    print("=" * 60)
    print("ℹ️  Fact tables kept in staging only (27M+ rows)")
    print("   Most granular in production: monthly municipality aggregates")
    print("=" * 60)


def _promote_pandas(source_engine, dest_engine, tables):
    """Fallback pandas-based promotion (original method)."""
    total_tables = len(tables)
    for idx, table in enumerate(sorted(tables), 1):
        _promote_pandas_single(source_engine, dest_engine, table, idx, total_tables)


def _promote_pandas_single(source_engine, dest_engine, table, idx=None, total=None):
    """Promote a single table using pandas (fallback method)."""

    if idx and total:
        print(f"\n[{idx}/{total}] Promoting table: {table}...")
    else:
        print(f"\nPromoting table: {table}...")
    try:
        # Read table schema to check for geometry columns
        inspector = inspect(source_engine)
        columns = inspector.get_columns(table)
        has_geometry = any(isinstance(col["type"], Geometry) for col in columns)

        if has_geometry:
            # Use GeoPandas to read the table if it contains geometry columns
            print("  Detected geometry column. Using GeoPandas for spatial data.")
            df = GeoDataFrame.from_postgis(f'SELECT * FROM "{table}"', source_engine, geom_col="geometry")

            # Convert the geometry object directly to its WKT representation.
            # The `to_shape` function was causing errors because the object from GeoPandas
            # was not a WKBElement. Accessing `.wkt` is the most direct method.
            df["geometry"] = df["geometry"].apply(lambda geom: geom.wkt if geom else None)
            dtype_map = {"geometry": Geometry(srid=4674)}  # type: ignore
        else:
            # Use Pandas for non-spatial tables
            df = pd.read_sql_table(table, source_engine)
            dtype_map = None

        print(f"  Read {len(df):,} rows from source.")

        # Write to destination database
        df.to_sql(table, dest_engine, if_exists="replace", index=False, chunksize=10000, dtype=dtype_map)  # type: ignore
        print(f"  ✅ Successfully wrote {len(df):,} rows to destination.")
    except Exception as e:
        print(f"  ❌ FAILED to promote table {table}: {e}")
        raise


def main():
    """Main execution function."""
    load_dotenv()
    parser = argparse.ArgumentParser(description="Promote data from staging to a production database using pandas.")
    parser.add_argument(
        "destination",
        choices=["local", "render"],
        help="The destination environment ('local' for local production, 'render' for cloud production).",
    )
    parser.add_argument(
        "--scope",
        choices=["all", "dim", "agg"],
        default="all",
        help="The scope of tables to promote: 'dim' for dimension tables, 'agg' for aggregate tables, or 'all' for both.",
    )
    args = parser.parse_args()

    source_url = os.getenv("STAGING_DATABASE_URL")
    if args.destination == "local":
        dest_url = os.getenv("PROD_LOCAL_DATABASE_URL")
        print("🚀 Promoting data to LOCAL production database...")
    else:  # render
        dest_url = os.getenv("PROD_POSTGRES_EXTERNAL_DATABASE_URL")
        print("🚀 Promoting data to RENDER production database...")

    if not source_url or not dest_url:
        print("❌ Error: Database URLs not found in .env file.")
        print("   Please ensure STAGING_DATABASE_URL and PROD_..._DATABASE_URL are set.")
        return

    promote_data(source_url, dest_url, use_pandas=True, scope=args.scope)


if __name__ == "__main__":
    main()
