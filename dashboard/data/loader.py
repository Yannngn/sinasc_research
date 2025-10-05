"""
Data loading utilities for SINASC Dashboard.
"""

import json
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd
from config.constants import MONTH_NAMES
from config.settings import AGGREGATES_DIR, CACHE_SIZE, METADATA_PATH, YEARS_DIR

# Path to IBGE data directory
IBGE_DATA_DIR = Path(__file__).parent.parent.parent / "data" / "IBGE"


class DataLoader:
    """Efficient data loader with caching for dashboard."""

    def __init__(self):
        """Initialize data loader."""
        self.metadata = self._load_metadata()
        self.available_years = self.metadata.get("years", [])

    def _load_metadata(self) -> Dict:
        """
        Load metadata file.

        Returns:
            Dictionary with metadata information
        """
        with open(METADATA_PATH, "r") as f:
            return json.load(f)

    def get_metadata(self) -> Dict:
        """Get metadata dictionary."""
        return self.metadata

    def get_available_years(self) -> List[int]:
        """Get list of available years."""
        return self.available_years

    def get_year_summary(self, year: int) -> Dict:
        """
        Get summary statistics for a specific year.

        Args:
            year: Year to get summary for

        Returns:
            Dictionary with summary statistics
        """
        for summary in self.metadata.get("yearly_summaries", []):
            if summary["year"] == year:
                return summary
        return {}

    @lru_cache(maxsize=10)
    def load_monthly_aggregates(self, year: int) -> pd.DataFrame:
        """
        Load monthly aggregated data for a specific year.

        Args:
            year: Year to load

        Returns:
            DataFrame with monthly statistics
        """
        file_path = AGGREGATES_DIR / f"monthly_{year}.parquet"
        if not file_path.exists():
            raise FileNotFoundError(f"Monthly aggregates not found for year {year}")
        df = pd.read_parquet(file_path)
        # Convert year_month to datetime for proper plotting
        if "year_month" in df.columns:
            df["year_month"] = pd.to_datetime(df["year_month"])
            df["month"] = df["year_month"].dt.month
            df["month_label"] = df["month"].apply(lambda x: MONTH_NAMES[x - 1])
        return df

    @lru_cache(maxsize=10)
    def load_state_aggregates(self, year: int) -> pd.DataFrame:
        """
        Load state aggregates for a specific year.

        Args:
            year: Year to load

        Returns:
            DataFrame with state aggregates
        """
        file_path = AGGREGATES_DIR / f"state_{year}.parquet"
        return pd.read_parquet(file_path)

    @lru_cache(maxsize=10)
    def load_municipality_aggregates(self, year: int) -> pd.DataFrame:
        """
        Load municipality aggregates for a specific year.

        Args:
            year: Year to load

        Returns:
            DataFrame with municipality aggregates
        """
        file_path = AGGREGATES_DIR / f"municipality_{year}.parquet"
        return pd.read_parquet(file_path)

    @lru_cache(maxsize=1)
    def load_yearly_aggregates(self) -> pd.DataFrame:
        """
        Load yearly aggregates with key indicators per year.

        Returns:
            DataFrame with yearly aggregates
        """
        file_path = AGGREGATES_DIR / "yearly.parquet"

        df = pd.read_parquet(file_path)

        return df

    @lru_cache(maxsize=1)
    def load_combined_yearly(self) -> pd.DataFrame:
        """
        Load combined yearly data for multi-year comparison.

        Returns:
            DataFrame with combined yearly data
        """
        file_path = AGGREGATES_DIR / "combined_yearly.parquet"
        return pd.read_parquet(file_path)

    def load_essential_data(self, year: int, columns: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Load essential columns data for a specific year.

        Args:
            year: Year to load
            columns: Optional list of columns to load (loads all if None)

        Returns:
            DataFrame with essential data
        """
        # Convert list to tuple for caching (tuples are hashable)
        if columns:
            return self._load_essential_data_with_columns(year, tuple(columns))
        else:
            return self._load_essential_data_full(year)

    @lru_cache(maxsize=CACHE_SIZE * 10)
    def _load_essential_data_with_columns(self, year: int, columns: tuple) -> pd.DataFrame:
        """Load essential data with specific columns (internal cached method)."""
        file_path = YEARS_DIR / f"{year}_essential.parquet"
        return pd.read_parquet(file_path, columns=list(columns))

    @lru_cache(maxsize=CACHE_SIZE)
    def _load_essential_data_full(self, year: int) -> pd.DataFrame:
        """Load all essential data (internal cached method)."""
        file_path = YEARS_DIR / f"{year}_essential.parquet"
        return pd.read_parquet(file_path)

    def get_date_range(self, year: int) -> Dict[str, str]:
        """
        Get date range for a specific year.

        Args:
            year: Year to get range for

        Returns:
            Dictionary with 'min' and 'max' dates
        """
        summary = self.get_year_summary(year)
        return summary.get("date_range", {})

    @lru_cache(maxsize=1)
    def load_brazil_geojson(self) -> Dict:
        """
        Load Brazilian states GeoJSON for choropleth maps.

        Returns:
            GeoJSON FeatureCollection with state boundaries
        """
        geojson_path = IBGE_DATA_DIR / "brazil_states.geojson"
        if not geojson_path.exists():
            raise FileNotFoundError(f"GeoJSON not found: {geojson_path}. Run scripts/fetch_geo_data.py first.")

        with open(geojson_path, "r", encoding="utf-8") as f:
            return json.load(f)

    @lru_cache(maxsize=10)
    def load_population_data(self, year: Optional[int] = None) -> pd.DataFrame:
        """
        Load population estimates by state.

        Args:
            year: Optional year to filter (loads all years if None)

        Returns:
            DataFrame with columns: state_code, state_name, year, population
        """
        csv_path = IBGE_DATA_DIR / "state_population_estimates.csv"
        if not csv_path.exists():
            raise FileNotFoundError(f"Population data not found: {csv_path}. Run scripts/fetch_geo_data.py first.")

        df = pd.read_csv(csv_path)

        if year is not None:
            df = df[df["year"] == year].copy()

        return df

    @lru_cache(maxsize=10)
    def load_state_aggregates_with_population(self, year: int) -> pd.DataFrame:
        """
        Load state aggregates merged with population data for per-capita calculations.

        Args:
            year: Year to load

        Returns:
            DataFrame with state aggregates + population column
        """
        # Load state aggregates
        state_df = self.load_state_aggregates(year)

        # Load population data
        pop_df = self.load_population_data(year)

        # Merge on state_code
        merged_df = state_df.merge(pop_df[["state_code", "population"]], on="state_code", how="left")

        # Calculate per-capita rates (births per 10,000 population)
        if "total_births" in merged_df.columns:
            merged_df["births_per_10k"] = (merged_df["total_births"] / merged_df["population"]) * 10000

        return merged_df


# Global data loader instance
data_loader = DataLoader()
