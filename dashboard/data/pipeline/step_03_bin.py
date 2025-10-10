"""
Pipeline Step 03: Create binned dimension tables.

This script creates dimension tables for continuous variables that have been
binned into categories, such as maternal age and birth weight.

Uses pure SQL for consistency with other pipeline steps and minimal memory usage.
"""

import argparse
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text


def create_binned_dimensions(engine):
    """
    Creates and populates dimension tables for binned categories using pure SQL.

    This approach uses SQL INSERT statements instead of Pandas to maintain
    consistency with the SQL-centric pipeline design.
    """
    print("🚀 Creating binned dimension tables...")

    with engine.begin() as conn:
        # --- Maternal Age Group Dimension ---
        print("  Creating dim_maternal_age_group...")

        # Drop and recreate table
        conn.execute(text("DROP TABLE IF EXISTS dim_maternal_age_group"))

        create_age_sql = """
        CREATE TABLE dim_maternal_age_group (
            id INTEGER PRIMARY KEY,
            min_age INTEGER NOT NULL,
            max_age INTEGER NOT NULL,
            label VARCHAR(20) NOT NULL
        )
        """
        conn.execute(text(create_age_sql))

        # Insert age group data
        insert_age_sql = """
        INSERT INTO dim_maternal_age_group (id, min_age, max_age, label) VALUES
            (1, 0, 14, '<15'),
            (2, 15, 19, '15-19'),
            (3, 20, 34, '20-34'),
            (4, 35, 39, '35-39'),
            (5, 40, 99, '40+')
        """
        conn.execute(text(insert_age_sql))

        print("  ✅ Successfully created `dim_maternal_age_group` with 5 categories.")

        # --- Birth Weight Category Dimension ---
        print("  Creating dim_birth_weight_category...")

        # Drop and recreate table
        conn.execute(text("DROP TABLE IF EXISTS dim_birth_weight_category"))

        create_weight_sql = """
        CREATE TABLE dim_birth_weight_category (
            id INTEGER PRIMARY KEY,
            min_weight_g INTEGER NOT NULL,
            max_weight_g INTEGER NOT NULL,
            label VARCHAR(20) NOT NULL
        )
        """
        conn.execute(text(create_weight_sql))

        # Insert weight category data
        insert_weight_sql = """
        INSERT INTO dim_birth_weight_category (id, min_weight_g, max_weight_g, label) VALUES
            (1, 0, 999, '<1000g'),
            (2, 1000, 1499, '1000-1499g'),
            (3, 1500, 2499, '1500-2499g'),
            (4, 2500, 3999, '2500-3999g'),
            (5, 4000, 9999, '4000g+')
        """
        conn.execute(text(insert_weight_sql))

        print("  ✅ Successfully created `dim_birth_weight_category` with 5 categories.")

        # --- Maternal Occupation Category Dimension ---
        print("  Creating dim_maternal_occupation...")

        # Drop and recreate table
        conn.execute(text("DROP TABLE IF EXISTS dim_maternal_occupation"))

        create_occupation_sql = """
        CREATE TABLE dim_maternal_occupation (
            id INTEGER PRIMARY KEY,
            label VARCHAR(100) NOT NULL
        )
        """
        conn.execute(text(create_occupation_sql))

        # Insert occupation category data
        insert_occupation_sql = """
        INSERT INTO dim_maternal_occupation (id, label) VALUES
            (1, 'Estudante'),
            (2, 'Trabalhadora do Lar'),
            (3, 'Trabalhadora Rural'),
            (4, 'Profissionais das Ciências e das Artes'),
            (5, 'Técnicos e Profissionais de Nível Médio'),
            (6, 'Trabalhadores de Serviços Administrativos'),
            (7, 'Trabalhadores dos Serviços e Vendedores'),
            (8, 'Outros'),
            (9, 'Ignorado')
        """
        conn.execute(text(insert_occupation_sql))

        print("  ✅ Successfully created `dim_maternal_occupation` with 9 categories.")

    print("\n✨ Binned dimension creation process finished successfully!")


def add_occupation_column(engine):
    """
    Add maternal occupation category column to fact_births table.

    This categorizes CODOCUPMAE into simplified occupation groups.
    """
    print("🔨 Adding maternal occupation category to fact_births...")

    with engine.begin() as conn:
        # Check if column already exists
        result = conn.execute(
            text(
                "SELECT column_name FROM information_schema.columns WHERE table_name = 'fact_births' AND column_name = 'maternal_occupation_category'"
            )
        )
        if result.scalar():
            print("  ⚠️  Column maternal_occupation_category already exists, skipping.")
            return

        # Add the column
        print("  Adding maternal_occupation_category column...")
        conn.execute(text("ALTER TABLE fact_births ADD COLUMN maternal_occupation_category INTEGER;"))

        # Update with categorized values
        print("  Categorizing occupations...")
        update_sql = """
        UPDATE fact_births 
        SET maternal_occupation_category = CASE
            WHEN "CODOCUPMAE" LIKE '999991%' THEN 1  -- Estudante
            WHEN "CODOCUPMAE" LIKE '999992%' THEN 2  -- Trabalhadora do Lar
            WHEN "CODOCUPMAE" LIKE '6%' THEN 3       -- Trabalhadora Rural
            WHEN "CODOCUPMAE" LIKE '2%' THEN 4       -- Profissionais das Ciências e das Artes
            WHEN "CODOCUPMAE" LIKE '3%' THEN 5       -- Técnicos e Profissionais de Nível Médio
            WHEN "CODOCUPMAE" LIKE '4%' THEN 6       -- Trabalhadores de Serviços Administrativos
            WHEN "CODOCUPMAE" LIKE '5%' THEN 7       -- Trabalhadores dos Serviços e Vendedores
            WHEN "CODOCUPMAE" IS NULL THEN 9         -- Ignorado
            ELSE 8                                  -- Outros
        END
        """
        conn.execute(text(update_sql))

        print("  ✅ Successfully added and populated maternal_occupation_category.")


def main():
    """Main execution function."""
    load_dotenv()
    parser = argparse.ArgumentParser(description="Create binned dimension tables in the staging database.")
    parser.add_argument(
        "--db_url",
        default=os.getenv("STAGING_DATABASE_URL"),
        help="Database connection URL for the staging environment.",
    )
    args = parser.parse_args()

    if not args.db_url:
        raise ValueError("Database URL not provided. Set STAGING_DATABASE_URL in .env or pass --db_url.")

    engine = create_engine(args.db_url)

    # Create dimension tables
    create_binned_dimensions(engine)

    # Add occupation category column to fact_births (requires fact_births to exist)
    with engine.connect() as connection:
        result = connection.execute(
            text("SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'fact_births')")
        )
        if result.scalar():
            add_occupation_column(engine)
        else:
            print("\n⚠️  fact_births table does not exist yet. Run step_02_create.py first, then re-run this step to add occupation categories.")


if __name__ == "__main__":
    main()
