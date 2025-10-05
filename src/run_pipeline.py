"""
Main entry point for the SINASC data processing pipeline.

This script orchestrates the complete data workflow, from raw data download
to the creation of optimized files for the dashboard.

Pipeline Steps:
1. Read Raw Data: Downloads raw .csv files from the DATASUS source.
2. Clean Data: Optimizes types and handles missing values.
3. Select Features: Subsets the data to only essential columns.
4. Engineer Features: Creates new categorical and boolean features.
5. Calculate Weight Stats: Computes birth weight z-scores and percentiles.
6. Create Dashboard Data: Generates pre-aggregated files for the web app.

Usage:
    # Process a single year
    python scripts/run_pipeline.py --year 2024

    # Process a range of years
    python scripts/run_pipeline.py --years 2022 2023 2024

    # Process all available years and overwrite existing files
    python scripts/run_pipeline.py --all --overwrite
"""

import argparse
import subprocess
from pathlib import Path

# --- Configuration ---
DATA_DIR = Path("data/SINASC")
PIPELINE_SCRIPTS_DIR = Path(__file__).parent / "pipeline"


def run_step(script_name: str, year: int, data_dir: Path, overwrite: bool = False):
    """Executes a single step in the data pipeline."""
    script_path = PIPELINE_SCRIPTS_DIR / script_name
    command = ["python", str(script_path), str(year), "--data_dir", str(data_dir)]

    if script_name in ["01_read_raw_data.py"]:
        command.extend(["--input_name", "raw.parquet", "--output_name", "temp.parquet"])

    elif script_name in ["04_engineer_features.py"]:
        command.extend(["--input_name", "temp.parquet", "--output_name", "complete.parquet"])

    else:
        command.extend(["--input_name", "temp.parquet", "--output_name", "temp.parquet"])

    if overwrite:
        command.append("--overwrite")

    print(f"\n{'=' * 60}")
    print(f"🚀 Running Step: {script_name} for Year: {year}")
    print(f"{'=' * 60}")

    result = subprocess.run(command, check=True)
    if result.returncode != 0:
        print(f"❌ Error in script: {script_name}")
        exit(1)
    print(f"✅ Step Complete: {script_name}\n")


def main():
    """Main execution function to run the full pipeline."""
    parser = argparse.ArgumentParser(description="SINASC data processing pipeline orchestrator.")
    parser.add_argument("--year", type=int, help="A single year to process.")
    parser.add_argument("--years", type=int, nargs="+", help="A list of years to process.")
    parser.add_argument("--all", action="store_true", help="Process all available years (2019-2024).")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing raw data files.")
    parser.add_argument("--data_dir", default=str(DATA_DIR), help="Root data directory.")
    parser.add_argument("--dashboard_only", action="store_true", help="Only run the dashboard data creation step.")
    args = parser.parse_args()

    data_dir = Path(args.data_dir)

    if not args.dashboard_only:
        if args.all:
            years_to_process = list(range(2015, 2025))
        elif args.years:
            years_to_process = sorted(args.years)
        elif args.year:
            years_to_process = [args.year]
        else:
            parser.error("You must specify --year, --years, or --all.")
            return

        print(f"🔧 Processing years: {years_to_process}")

        pipeline_steps = [
            "01_read_raw_data.py",
            "02_clean_data.py",
            "03_select_features.py",
            "04_engineer_features.py",
        ]

        for year in years_to_process:
            for step_script in pipeline_steps:
                run_step(step_script, year, data_dir, args.overwrite)

    # Final step: create dashboard data for all processed years
    print(f"\n{'=' * 60}")
    print("🚀 Running Step: 05_create_dashboard_data.py for All Years")
    print(f"{'=' * 60}")
    dashboard_script = PIPELINE_SCRIPTS_DIR / "05_create_dashboard_data.py"
    subprocess.run(["python", str(dashboard_script), "--all", "--data_dir", str(data_dir), "--input_name", "complete.parquet"], check=True)
    print("✅ Step Complete: 05_create_dashboard_data.py\n")

    print(f"\n{'✨' * 20}")
    print("✨  Complete Data Pipeline Finished Successfully!  ✨")
    print(f"{'✨' * 20}\n")


if __name__ == "__main__":
    main()
