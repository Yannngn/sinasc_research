"""
Master Pipeline Orchestrator.

This script runs all pipeline steps in the correct sequence to build
the complete data model from raw SINASC data.

Steps:
1. Select essential columns from raw tables
2. Create fact_births table (with duplicate handling)
3. Create binned dimension tables
4. Engineer features using SQL
5. Create aggregated tables

All steps are SQL-based for maximum memory efficiency.
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

from dotenv import load_dotenv


def run_step(step_name: str, script_path: Path):
    """
    Run a pipeline step script.

    Args:
        step_name: Human-readable name of the step.
        script_path: Path to the Python script to execute.
    """
    print(f"\n{'=' * 70}")
    print(f"🚀 STEP: {step_name}")
    print(f"{'=' * 70}\n")

    result = subprocess.run([sys.executable, str(script_path)], capture_output=False, text=True)

    if result.returncode != 0:
        print(f"\n❌ Step '{step_name}' failed with exit code {result.returncode}")
        sys.exit(1)

    print(f"\n✅ Step '{step_name}' completed successfully!")


def main():
    """Main execution function."""
    load_dotenv()
    parser = argparse.ArgumentParser(description="Run the complete data pipeline to build fact and aggregate tables.")
    parser.add_argument("--skip-select", action="store_true", help="Skip step 01 (column selection) if already done.")
    parser.add_argument("--skip-create", action="store_true", help="Skip step 02 (fact table creation) if already done.")
    parser.add_argument("--skip-dimensions", action="store_true", help="Skip step 03 (binned dimensions) if already done.")
    args = parser.parse_args()

    # Verify database connection
    if not os.getenv("STAGING_DATABASE_URL"):
        print("❌ STAGING_DATABASE_URL not set in .env file. Aborting.")
        sys.exit(1)

    # Get pipeline directory
    pipeline_dir = Path(__file__).parent

    print("\n" + "=" * 70)
    print("🔥 STARTING COMPLETE DATA PIPELINE")
    print("=" * 70)

    # Step 01: Select essential columns
    if not args.skip_select:
        run_step("Select Essential Columns", pipeline_dir / "step_01_select.py")
    else:
        print("\n⏭️  Skipping Step 01: Select Essential Columns")

    # Step 02: Create fact_births table
    if not args.skip_create:
        run_step("Create Fact Births Table", pipeline_dir / "step_02_create.py")
    else:
        print("\n⏭️  Skipping Step 02: Create Fact Births Table")

    # Step 03: Create binned dimension tables
    if not args.skip_dimensions:
        run_step("Create Binned Dimension Tables", pipeline_dir / "step_03_bin.py")
    else:
        print("\n⏭️  Skipping Step 03: Create Binned Dimension Tables")

    # Step 04: Engineer features
    run_step("Engineer Features (SQL)", pipeline_dir / "step_04_engineer.py")

    # Step 05: Create aggregations
    run_step("Create Aggregated Tables", pipeline_dir / "step_05_aggregate.py")

    print("\n" + "=" * 70)
    print("✨ COMPLETE DATA PIPELINE FINISHED SUCCESSFULLY!")
    print("=" * 70)
    print("\nYour staging database now contains:")
    print("  • fact_births - Complete birth records with engineered features")
    print("  • dim_* tables - All dimension tables for lookups")
    print("  • agg_* tables - Pre-aggregated summaries for the dashboard")
    print("\nNext steps:")
    print("  1. Run promote.py to copy data to production database")
    print("  2. Update the dashboard DataLoader to query these tables")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
