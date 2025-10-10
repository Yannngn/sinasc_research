"""
Pipeline Step 02: Create the main `fact_births` table.

This script reads all selected `selected_sinasc_*` tables from the staging database
and combines them into a single `fact_births` table using SQL.

This approach is memory-efficient as it operates entirely in the database.
It also handles appending new data without creating duplicates.
"""

import argparse
import os

from dotenv import load_dotenv
from sqlalchemy import Engine, create_engine, text


def get_selected_tables(engine: Engine) -> list[str]:
    """
    Get a list of all selected SINASC tables from the database.

    Args:
        engine: SQLAlchemy engine connected to the staging database.

    Returns:
        A list of table names matching the 'selected_sinasc_%' pattern.
    """
    with engine.connect() as connection:
        result = connection.execute(
            text(
                "SELECT table_name FROM information_schema.tables "
                "WHERE table_schema = 'public' AND table_name LIKE 'selected_sinasc_%' "
                "ORDER BY table_name"
            )
        )
        tables = [row[0] for row in result]
    print(f"Found {len(tables)} selected SINASC tables: {tables}")
    return tables


def create_fact_births_table(engine: Engine, source_tables: list[str]):
    """
    Create or append to the fact_births table using SQL UNION ALL.

    This avoids loading data into memory and handles duplicates through database constraints.

    Args:
        engine: SQLAlchemy engine connected to the staging database.
        source_tables: List of source table names to combine.
    """
    print("\n🔨 Creating fact_births table from selected tables...")

    # Check if fact_births already exists
    with engine.connect() as connection:
        result = connection.execute(
            text("SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'fact_births')")
        )
        table_exists = result.scalar()

    mode = "append" if table_exists else "create"

    # Build UNION ALL query from source tables
    union_queries = [f"SELECT * FROM {table}" for table in source_tables]
    full_query = " UNION ALL ".join(union_queries)

    try:
        with engine.connect() as connection:
            tx = connection.begin()

            if mode == "create":
                # Deduplicate rows by composite key before creating the fact table so index creation doesn't fail
                dedup_sql = f"""
                CREATE TABLE fact_births AS
                WITH union_all AS (
                    {full_query}
                ), deduped AS (
                    SELECT union_all.*, ROW_NUMBER() OVER (
                        PARTITION BY "CODMUNNASC", "DTNASC", "IDADEMAE", "PESO", "SEXO", "HORANASC"
                        ORDER BY "DTNASC"
                    ) as rn
                    FROM union_all
                )
                SELECT * FROM deduped WHERE rn = 1;
                """

                connection.execute(text(dedup_sql))

                # Cleanup and add indexes
                connection.execute(text("ALTER TABLE fact_births DROP COLUMN IF EXISTS rn;"))
                connection.execute(text("ALTER TABLE fact_births ADD COLUMN id SERIAL PRIMARY KEY;"))
                connection.execute(
                    text(
                        "CREATE UNIQUE INDEX idx_fact_births_unique "
                        'ON fact_births ("CODMUNNASC", "DTNASC", "IDADEMAE", "PESO", "SEXO", "HORANASC") '
                        'WHERE "CODMUNNASC" IS NOT NULL AND "DTNASC" IS NOT NULL;'
                    )
                )
                print("  ✅ Created fact_births table with unique index.")
            else:
                # Get column list from fact_births (excluding the auto-generated 'id' column)
                result = connection.execute(
                    text(
                        "SELECT column_name FROM information_schema.columns "
                        "WHERE table_name = 'fact_births' AND column_name != 'id' "
                        "ORDER BY ordinal_position"
                    )
                )
                columns = [row[0] for row in result]
                columns_str = ", ".join([f'"{col}"' for col in columns])

                # Ensure unique index exists before attempting ON CONFLICT
                connection.execute(
                    text(
                        "CREATE UNIQUE INDEX IF NOT EXISTS idx_fact_births_unique "
                        'ON fact_births ("CODMUNNASC", "DTNASC", "IDADEMAE", "PESO", "SEXO", "HORANASC") '
                        'WHERE "CODMUNNASC" IS NOT NULL AND "DTNASC" IS NOT NULL;'
                    )
                )

                # Append only new records (those not matching the unique index)
                insert_sql = f"""
                INSERT INTO fact_births ({columns_str})
                SELECT {columns_str} FROM ({full_query}) AS new_data
                ON CONFLICT ("CODMUNNASC", "DTNASC", "IDADEMAE", "PESO", "SEXO", "HORANASC")
                DO NOTHING;
                """
                connection.execute(text(insert_sql))
                print("  ✅ Appended new records to fact_births (duplicates skipped).")

            tx.commit()

        # Get final row count
        with engine.connect() as connection:
            result = connection.execute(text("SELECT COUNT(*) FROM fact_births;"))
            count = result.scalar()

        print(f"  ✅ fact_births table ready with {count:,} total records.")

    except Exception as e:
        print(f"  ❌ FAILED to create fact_births table. Error: {e}")
        raise


def main():
    """Main execution function to create the fact table."""
    load_dotenv()
    parser = argparse.ArgumentParser(description="Create the `fact_births` table in the staging database.")
    parser.add_argument(
        "--db_url",
        default=os.getenv("STAGING_DATABASE_URL"),
        help="Database connection URL for the staging environment.",
    )
    args = parser.parse_args()

    if not args.db_url:
        raise ValueError("Database URL not provided. Set STAGING_DATABASE_URL in .env or pass --db_url.")

    print("🚀 Starting SQL-based fact table creation pipeline...")
    engine = create_engine(args.db_url)

    selected_tables = get_selected_tables(engine)
    if not selected_tables:
        print("❌ No `selected_sinasc_*` tables found. Run step_01_select.py first. Aborting.")
        return

    create_fact_births_table(engine, selected_tables)

    print("\n✨ Fact table creation process finished successfully!")


if __name__ == "__main__":
    main()
