"""
Pipeline Step 04: Engineer Features using SQL (Optimized).

This script creates a new, enriched fact table with all computed features
in a single, memory-efficient pass using a `CREATE TABLE AS SELECT` statement.
This avoids slow, iterative UPDATEs and is significantly faster.
"""

import argparse
import os
import re

from dotenv import load_dotenv
from sqlalchemy import Engine, create_engine, text


def get_feature_definitions() -> list[tuple[str, str]]:
    """
    Returns a list of all feature definitions as (column_name, sql_formula) tuples.
    """
    # All features are boolean for simplicity and aggregation performance
    features = [
        # Gestational features
        ("is_preterm", "\"GESTACAO\" IN ('1', '2', '3', '4')"),
        ("is_extreme_preterm", "\"GESTACAO\" IN ('1', '2', '3')"),
        # Delivery type
        ("is_cesarean", "\"PARTO\" = '2'"),
        # Pregnancy type
        ("is_multiple_birth", "\"GRAVIDEZ\" IN ('2', '3')"),
        # Maternal age features
        ("is_adolescent_pregnancy", 'CAST("IDADEMAE" AS INTEGER) < 20'),
        ("is_very_young_pregnancy", 'CAST("IDADEMAE" AS INTEGER) < 15'),
        ("is_geriatric_pregnancy", 'CAST("IDADEMAE" AS INTEGER) > 35'),
        # Parity - first pregnancy indicator
        ("is_first_pregnancy", '("QTDGESTANT" = 0 OR "QTDGESTANT" IS NULL)'),
        ("has_previous_normal_delivery", 'CAST("QTDPARTNOR" AS INTEGER) > 0'),
        ("has_previous_cesarean", 'CAST("QTDPARTCES" AS INTEGER) > 0'),
        # Paternity
        ("has_father_registered", '"IDADEPAI" IS NOT NULL'),
        # Geographic displacement
        ("birth_location_differs", '"CODMUNNASC" != "CODMUNRES"'),
        ("is_hospital_birth", "\"LOCNASC\" = '1'"),
        # Neonatal health - APGAR scores
        ("is_low_apgar1", 'CAST("APGAR1" AS INTEGER) < 7'),
        ("is_low_apgar5", 'CAST("APGAR5" AS INTEGER) < 7'),
        ("is_critical_apgar1", 'CAST("APGAR1" AS INTEGER) <= 3'),
        ("is_critical_apgar5", 'CAST("APGAR5" AS INTEGER) <= 3'),
        # APGAR evolution patterns
        ("apgar_normal", 'CAST("APGAR1" AS INTEGER) >= 7 AND CAST("APGAR5" AS INTEGER) >= 7'),
        ("apgar_improved", 'CAST("APGAR1" AS INTEGER) < 7 AND CAST("APGAR5" AS INTEGER) >= 7'),
        ("apgar_deteriorated", 'CAST("APGAR1" AS INTEGER) >= 7 AND CAST("APGAR5" AS INTEGER) < 7'),
        ("apgar_persistent_distress", 'CAST("APGAR1" AS INTEGER) < 7 AND CAST("APGAR5" AS INTEGER) < 7'),
        # Birth weight categories
        ("is_low_birth_weight", 'CAST("PESO" AS INTEGER) < 2500'),
        ("is_very_low_birth_weight", 'CAST("PESO" AS INTEGER) < 1500'),
        ("is_extremely_low_birth_weight", 'CAST("PESO" AS INTEGER) < 1000'),
        ("is_high_birth_weight", 'CAST("PESO" AS INTEGER) >= 4000'),
        # Prenatal care
        ("early_prenatal_care", 'CAST("MESPRENAT" AS INTEGER) <= 3'),
        ("late_prenatal_care", 'CAST("MESPRENAT" AS INTEGER) >= 6'),
        ("is_prenatal_adequate", "\"CONSULTAS\" = '4'"),
    ]
    return features


def engineer_features_optimized(engine: Engine):
    """
    Rebuilds the fact_births table with all computed features in a single pass.
    """
    print("🚀 Starting optimized feature engineering pipeline...")

    features = get_feature_definitions()

    with engine.connect() as connection:
        # Get existing columns from the source table
        inspector = engine.connect()
        columns = inspector.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'fact_births'")).fetchall()
        existing_cols = {col[0] for col in columns}

        # Build the SELECT clause for the new table
        select_clauses = ["source.*"]
        for col_name, formula in features:
            # Skip if the column already exists in the source table (from a previous run)
            if col_name in existing_cols:
                print(f"  ⚠️  Column '{col_name}' already exists in source table, skipping.")
                continue

            # Extract source columns referenced in the formula
            referenced_cols = set(re.findall(r'"([^\"]+)"', formula))

            # Only include the feature if all its source columns exist
            if referenced_cols.issubset(existing_cols):
                select_clauses.append(f"({formula})::BOOLEAN AS {col_name}")
            else:
                print(
                    f"  ⚠️  Skipping feature '{col_name}': missing source columns {referenced_cols - existing_cols}"
                )  # Assemble the final CREATE TABLE statement
        create_sql = f"""
        CREATE TABLE fact_births_engineered AS
        SELECT
            {", ".join(select_clauses)}
        FROM fact_births AS source;
        """

        # Execute the entire process within a single transaction for safety
        tx = connection.begin()
        try:
            print("  Dropping old temporary and backup tables if they exist...")
            connection.execute(text("DROP TABLE IF EXISTS fact_births_engineered;"))
            connection.execute(text("DROP TABLE IF EXISTS fact_births_backup;"))

            print("  Creating new enriched table 'fact_births_engineered'...")
            connection.execute(text(create_sql))
            print("  ✅ New table created.")

            print("  Swapping tables atomically...")
            connection.execute(text("ALTER TABLE fact_births RENAME TO fact_births_backup;"))
            connection.execute(text("ALTER TABLE fact_births_engineered RENAME TO fact_births;"))
            print("  ✅ Tables swapped.")

            connection.execute(text("DROP TABLE IF EXISTS fact_births_backup;"))

            tx.commit()
            print("  Transaction committed.")

        except Exception as e:
            print(f"  ❌ An error occurred: {e}. Rolling back transaction.")
            tx.rollback()
            raise

    print("\n✨ Optimized feature engineering process finished successfully!")


def main():
    """Main execution function."""
    load_dotenv()
    parser = argparse.ArgumentParser(description="Engineer features in the fact_births table using an optimized SQL approach.")
    parser.add_argument(
        "--db_url",
        default=os.getenv("STAGING_DATABASE_URL"),
        help="Database connection URL for the staging environment.",
    )
    args = parser.parse_args()

    if not args.db_url:
        raise ValueError("Database URL not provided. Set STAGING_DATABASE_URL in .env or pass --db_url.")

    engine = create_engine(args.db_url)

    # Check if fact_births exists
    with engine.connect() as connection:
        result = connection.execute(
            text("SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'fact_births')")
        )
        if not result.scalar():
            print("❌ fact_births table does not exist. Run step_02_create.py first. Aborting.")
            return

    engineer_features_optimized(engine)


if __name__ == "__main__":
    main()
