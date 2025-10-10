"""
Pipeline Step 05: Create Aggregated Tables.

This script runs SQL queries against the staging database to generate all
the pre-aggregated tables required by the dashboard.

All computation happens in the database for maximum efficiency.
"""

import argparse
import os

from dotenv import load_dotenv
from sqlalchemy import Engine, create_engine, text


def _create_mean_sql(column: str, alias: str | None = None) -> str:
    """Generate SQL snippet to calculate the mean of a numeric column."""
    if not alias:
        alias = f"{column.lower()}_mean"

    return f'AVG(CAST("{column}" AS FLOAT)) as {alias}'


def _count_pct_sql(column: str, alias: str | None = None, raw: bool = False, denom: str = "COUNT(*)") -> str:
    """
    Generate SQL snippet for a count + percent pair for a boolean condition.

    Args:
        column: column name or raw condition (when raw=True)
        alias: base alias for the metric (e.g. 'cesarean')
        raw: if True, `column` is treated as a raw SQL condition (no quoting)
        denom: denominator expression used for percent calculation

    Returns:
        SQL fragment like: "SUM(CASE WHEN <cond> THEN 1 ELSE 0 END) as <alias>_count,
                          (SUM(CASE WHEN <cond> THEN 1 ELSE 0 END) * 100.0 / NULLIF(<denom>,0)) as <alias>_pct"
    """
    if not alias:
        # derive alias from column name
        alias = column.replace('"', "").replace(".", "_").replace(" ", "_").replace("is_", "").lower()

    if raw:
        cond = column
    else:
        cond = f'"{column}"'

    count_expr = f"SUM(CASE WHEN {cond} THEN 1 ELSE 0 END) as {alias}_count"
    pct_expr = f"(SUM(CASE WHEN {cond} THEN 1 ELSE 0 END) * 100.0 / NULLIF({denom},0)) as {alias}_pct"
    return f"{count_expr},\n        {pct_expr}"


def execute_sql(engine: Engine, sql: str, table_name: str):
    """
    Execute a SQL query to create or replace a table.

    Args:
        engine: SQLAlchemy engine connected to the database.
        sql: The SQL query to execute.
        table_name: The name of the table to be created.
    """
    print(f"  Creating table: {table_name}...")
    try:
        with engine.connect() as connection:
            tx = connection.begin()
            connection.execute(text(f"DROP TABLE IF EXISTS {table_name};"))
            connection.execute(text(f"CREATE TABLE {table_name} AS {sql}"))
            tx.commit()

        # Get row count
        with engine.connect() as connection:
            result = connection.execute(text(f"SELECT COUNT(*) FROM {table_name};"))
            count = result.scalar()

        print(f"  ✅ Successfully created {table_name} with {count:,} records.")
    except Exception as e:
        print(f"  ❌ FAILED to create {table_name}. Error: {e}")
        raise


def create_time_aggregates(engine: Engine, interval: str):
    """Create time-based aggregates."""

    print(f"\n📊 Creating {interval} aggregates...")
    if interval == "yearly":
        time_select = 'EXTRACT(YEAR FROM "DTNASC")::INTEGER as year'
        time_group = 'EXTRACT(YEAR FROM "DTNASC")::INTEGER'
        time_order = "year"
    elif interval == "monthly":
        time_select = 'EXTRACT(YEAR FROM "DTNASC")::INTEGER as year, EXTRACT(MONTH FROM "DTNASC")::INTEGER as month'
        time_group = 'EXTRACT(YEAR FROM "DTNASC")::INTEGER, EXTRACT(MONTH FROM "DTNASC")::INTEGER'
        time_order = "year, month"
    else:
        raise ValueError("Invalid interval. Must be 'yearly' or 'monthly'.")

    sql = f"""
    SELECT
        {time_select},
        COUNT(*) as total_births,
        {_create_mean_sql("PESO", "weight_mean")},
        {_create_mean_sql("IDADEMAE", "mother_age_mean")},
        {_create_mean_sql("APGAR5", "apgar5_mean")},
        {_count_pct_sql("is_cesarean", "cesarean")},
        {_count_pct_sql("is_preterm", "preterm")},
        {_count_pct_sql("is_extreme_preterm", "extreme_preterm")},
        {_count_pct_sql("is_adolescent_pregnancy", "adolescent_pregnancy")},
        {_count_pct_sql("is_very_young_pregnancy", "very_young_pregnancy")},
        {_count_pct_sql("is_low_birth_weight", "low_birth_weight")},
        {_count_pct_sql("is_low_apgar5", "low_apgar5")},
        {_count_pct_sql("is_hospital_birth", "hospital_birth")},
        {_count_pct_sql("is_prenatal_adequate", "prenatal_adequate")}
    FROM
        fact_births
    WHERE
        "DTNASC" IS NOT NULL
    GROUP BY
        {time_group}
    ORDER BY
        {time_order};
    """
    execute_sql(engine, sql, f"agg_{interval}")


def create_location_aggregates(
    engine: Engine,
    location: str,
    interval: str = "yearly",
    extra_processing: str | None = None,
):
    """Create location-based aggregates.

    Args:
        engine: SQLAlchemy engine.
        location: One of 'state', 'municipality', or 'cnes'.
        interval: Time interval for aggregation: 'daily', 'monthly', or 'yearly'.
        extra_processing: Optional SQL snippet to inject into the SELECT for additional processing (e.g. window functions).
    """
    print(f"\n📊 Creating {location} aggregates ({interval})...")

    # determine time grouping expression
    interval = interval.lower()
    if interval == "daily":
        time_select = 'DATE(fb."DTNASC") as day'
        time_group = 'DATE(fb."DTNASC")'
        time_order = "day"
    elif interval == "monthly":
        time_select = 'EXTRACT(YEAR FROM fb."DTNASC")::INTEGER as year, EXTRACT(MONTH FROM fb."DTNASC")::INTEGER as month'
        time_group = 'EXTRACT(YEAR FROM fb."DTNASC")::INTEGER, EXTRACT(MONTH FROM fb."DTNASC")::INTEGER'
        time_order = "year, month"
    else:
        # default yearly
        time_select = 'EXTRACT(YEAR FROM fb."DTNASC")::INTEGER as year'
        time_group = 'EXTRACT(YEAR FROM fb."DTNASC")::INTEGER'
        time_order = "year"

    # location specific clauses
    # Brazilian municipality codes:
    # - fact_births.CODMUNNASC: 6 digits (without check digit)
    # - dim_ibge_id_municipalities.id: 7 digits (6 digits + 1 check digit)
    # - First 2 digits = state code (UF)
    # - First digit = region code
    if location == "region":
        # Extract first 1 digits from CODMUNNASC to get region from region dim
        join_clause = 'JOIN dim_ibge_id_regions dm ON CAST(SUBSTR(fb."CODMUNNASC", 1, 1) AS BIGINT) = dm.id'
        group_by = "dm.name"
        select_location = "dm.name as name"
        having_clause = ""
        table_suffix = "region"
    elif location == "state":
        # Extract first 2 digits from CODMUNNASC (6-digit code) to match state id (2-digit)
        join_clause = 'JOIN dim_ibge_id_states dm ON CAST(SUBSTR(fb."CODMUNNASC", 1, 2) AS BIGINT) = dm.id'
        group_by = "dm.id"
        select_location = "dm.id as state_code"
        having_clause = ""
        table_suffix = "state"
    elif location == "municipality":
        # CODMUNNASC (6 digits) = first 6 digits of dim municipality id (7 digits, last is check digit)
        join_clause = 'JOIN dim_ibge_id_municipalities dm ON fb."CODMUNNASC" = SUBSTRING(CAST(dm.id AS TEXT), 1, 6)'
        group_by = "dm.id"
        select_location = "CAST(dm.id AS TEXT) as municipality_code"
        having_clause = ""  # "HAVING COUNT(fb.id) >= 10"  # Filter out municipalities with very few births
        table_suffix = "municipality"
    elif location == "cnes":
        # Use dim_health_facility created by the optimize pipeline
        join_clause = 'JOIN dim_health_facility dhf ON fb."CODESTAB" = dhf.cnes_code'
        group_by = "dhf.cnes_code, dhf.municipality_code"
        select_location = "dhf.cnes_code as cnes_code, dhf.municipality_code as municipality_code"
        having_clause = ""  # "HAVING COUNT(fb.id) >= 10"  # Filter out cnes with very few births
        table_suffix = "cnes"
    else:
        raise ValueError("Invalid location type. Must be 'region', 'state', 'municipality' or 'cnes'.")

    # build extra processing if provided
    extra_sql = f",\n        {extra_processing}" if extra_processing else ""

    sql = f"""
    SELECT
        {select_location},
        {time_select},
        COUNT(fb.id) as total_births,
        AVG(CAST(fb."PESO" AS FLOAT)) as peso_mean,
        AVG(CAST(fb."IDADEMAE" AS FLOAT)) as idademae_mean,
        AVG(CAST(fb."APGAR5" AS FLOAT)) as apgar5_mean,
        {_count_pct_sql("fb.is_cesarean", "cesarean", raw=True, denom="COUNT(fb.id)")},
        {_count_pct_sql("fb.is_preterm", "preterm", raw=True, denom="COUNT(fb.id)")},
        {_count_pct_sql("fb.is_extreme_preterm", "extreme_preterm", raw=True, denom="COUNT(fb.id)")},
        {_count_pct_sql("fb.is_adolescent_pregnancy", "adolescent_pregnancy", raw=True, denom="COUNT(fb.id)")},
        {_count_pct_sql("fb.is_low_birth_weight", "low_birth_weight", raw=True, denom="COUNT(fb.id)")},
        {_count_pct_sql("fb.is_low_apgar5", "low_apgar5", raw=True, denom="COUNT(fb.id)")},
        {_count_pct_sql("fb.\"LOCNASC\" = '1'", "hospital_birth", raw=True, denom="COUNT(fb.id)")}{extra_sql}
    FROM
        fact_births fb
    {join_clause}
    WHERE
        fb."DTNASC" IS NOT NULL AND fb."CODMUNNASC" IS NOT NULL
    GROUP BY
        {group_by}, {time_group}
    {having_clause}
    ORDER BY
        {time_order}, {group_by};
    """

    suffix = f"{table_suffix}_{interval}"
    execute_sql(engine, sql, f"agg_{suffix}")


def create_yearly_aggregates(engine: Engine):
    """Create overall yearly aggregates."""
    create_time_aggregates(engine, "yearly")


def create_monthly_aggregates(engine: Engine):
    """Create monthly aggregates by year."""
    create_time_aggregates(engine, "monthly")


def create_state_aggregates(engine: Engine):
    """Create state-level yearly aggregates."""
    # Wrapper kept for backward compatibility; use the generalized function
    create_location_aggregates(engine, "state", interval="yearly")


def create_municipality_aggregates(engine: Engine):
    """Create municipality-level yearly aggregates."""
    # Wrapper kept for backward compatibility; use the generalized function
    create_location_aggregates(engine, "municipality", interval="yearly")


def create_occupation_aggregates(engine: Engine):
    """Create maternal occupation yearly aggregates."""
    print("\n📊 Creating maternal occupation aggregates...")
    sql = """
    SELECT
        EXTRACT(YEAR FROM fb."DTNASC")::INTEGER as year,
        fb.maternal_occupation_category as occupation_code,
        dmo.label as occupation_label,
        COUNT(fb.id) as total_births,
        (COUNT(fb.id) * 100.0 / SUM(COUNT(fb.id)) OVER (PARTITION BY EXTRACT(YEAR FROM fb."DTNASC"))) as percentage
    FROM
        fact_births fb
    LEFT JOIN
        dim_maternal_occupation dmo ON fb.maternal_occupation_category = dmo.id
    WHERE
        fb."DTNASC" IS NOT NULL 
        AND fb.maternal_occupation_category IS NOT NULL 
    GROUP BY
        EXTRACT(YEAR FROM fb."DTNASC"), fb.maternal_occupation_category, dmo.label
    ORDER BY
        year, total_births DESC;
    """
    execute_sql(engine, sql, "agg_occupation_yearly")


def main():
    """Main execution function to run the aggregation pipeline."""
    load_dotenv()
    parser = argparse.ArgumentParser(description="Create aggregated tables in the staging database.")
    parser.add_argument(
        "--db_url",
        default=os.getenv("STAGING_DATABASE_URL"),
        help="Database connection URL for the staging environment.",
    )
    args = parser.parse_args()

    if not args.db_url:
        raise ValueError("Database URL not provided. Set STAGING_DATABASE_URL in .env or pass --db_url.")

    print("🚀 Starting SQL-based aggregation pipeline...")
    engine = create_engine(args.db_url)

    # Check if fact_births exists
    with engine.connect() as connection:
        result = connection.execute(
            text("SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'fact_births')")
        )
        if not result.scalar():
            print("❌ fact_births table does not exist. Run previous steps first. Aborting.")
            return

    create_time_aggregates(engine, "yearly")
    create_time_aggregates(engine, "monthly")

    create_location_aggregates(engine, "region", "yearly")
    create_location_aggregates(engine, "state", "yearly")
    create_location_aggregates(engine, "municipality", "yearly")
    create_location_aggregates(engine, "cnes", "yearly")

    create_location_aggregates(engine, "region", "monthly")
    create_location_aggregates(engine, "state", "monthly")
    create_location_aggregates(engine, "municipality", "monthly")
    create_location_aggregates(engine, "cnes", "monthly")

    create_location_aggregates(engine, "region", "daily")
    create_location_aggregates(engine, "state", "daily")

    create_occupation_aggregates(engine)

    print("\n✨ Aggregation pipeline finished successfully!")


if __name__ == "__main__":
    main()
