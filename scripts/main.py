"""
Main entry point for SINASC data processing.

This script orchestrates the complete data pipeline:
1. Downloads and processes raw SINASC data
2. Creates optimized dashboard files
3. Can process single year or all years

Usage:
    python main.py 2024
    python main.py 2024 --overwrite
    python main.py --all  # Process all available years
    python main.py --all --data_dir data/SINASC
"""

from run_one_year import run_one_year

# Default configuration
DIR = "data/SINASC"
YEAR = 2024


def main():
    """Main execution function."""
    import argparse
    import subprocess

    parser = argparse.ArgumentParser(description="Complete SINASC data processing and dashboard data creation")
    parser.add_argument("year", type=int, default=YEAR, nargs="?", help="Year to process (default: 2024)")
    parser.add_argument("--all", action="store_true", help="Process all available years (2019-2024)")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing data")
    parser.add_argument("--data_dir", default=DIR, help="Data directory")
    args = parser.parse_args()

    print(f"\n{'=' * 60}")
    print("SINASC Data Processing Pipeline")
    print(f"{'=' * 60}\n")

    if args.all:
        years = [2019, 2020, 2021, 2022, 2023, 2024]
        for year in years:
            run_one_year(year, args.data_dir, overwrite=args.overwrite)
    else:
        run_one_year(args.year if args.year else YEAR, args.data_dir, overwrite=args.overwrite)

    # Create dashboard files
    print(f"\n{'=' * 60}")
    print("Creating Dashboard Data Files")
    print(f"{'=' * 60}\n")
    subprocess.run(["python", "-m", "scripts.create_dashboard_data", "--all"])
    
    print(f"\n{'=' * 60}")
    print("✨ Complete Pipeline Finished!")
    print(f"{'=' * 60}\n")


if __name__ == "__main__":
    main()
