"""
Data loading utilities for SINASC Dashboard.

This module provides database-backed data loading for the dashboard,
replacing the previous Parquet file-based approach.
"""

import os
from functools import lru_cache
from pathlib import Path
from typing import Any

import geopandas as gpd
import pandas as pd
from config.constants import MONTH_NAMES
from shapely import wkb
from shapely.ops import orient

from data.database import get_local_db_engine, get_prod_db_engine, get_staging_db_engine

# Path to IBGE data directory
IBGE_DATA_DIR = Path(__file__).parent.parent.parent / "data" / "IBGE"


class DataLoader:
    """
    Database-backed data loader with caching for dashboard.

    Loads data directly from PostgreSQL aggregate tables instead of Parquet files.
    """

    def __init__(self, use_staging: bool = False, use_local: bool = False):
        """
        Initialize data loader.

        Args:
            use_staging: If True, connect to staging DB; otherwise production DB
            use_local: If True, connect to local DB; otherwise remote DB
        """
        self.engine = get_staging_db_engine() if use_staging else (get_prod_db_engine() if not use_local else get_local_db_engine())
        self.metadata = self._load_metadata_from_db()
        self.available_years = self.metadata.get("years", [])

    def _load_metadata_from_db(self) -> dict:
        """
        Generate metadata from database aggregate tables.

        Returns:
            Dictionary with metadata information
        """
        # Load yearly aggregates to generate metadata
        df_yearly = pd.read_sql_table("agg_yearly", self.engine)

        # Load occupation aggregates
        df_occupation = pd.read_sql_table("agg_occupation_yearly", self.engine)

        yearly_summaries = []
        for _, row in df_yearly.iterrows():
            year = int(row["year"])

            # Get occupation data for this year
            occ_year = df_occupation[df_occupation["year"] == year]
            maternal_occupation = {}
            for _, occ_row in occ_year.iterrows():
                code = str(int(occ_row["occupation_code"]))
                maternal_occupation[code] = {"label": occ_row["occupation_label"], "count": int(occ_row["total_births"])}

            yearly_summaries.append(
                {
                    "year": year,
                    "total_births": int(row["total_births"]),
                    "pregnancy": {
                        "adolescent_pregnancy_pct": float(row["adolescent_pregnancy_pct"]),
                        "very_young_pregnancy_pct": float(row["very_young_pregnancy_pct"]),
                        "preterm_pct": float(row["preterm_pct"]),
                        "extreme_preterm_pct": float(row["extreme_preterm_pct"]),
                    },
                    "delivery_type": {
                        "cesarean_pct": float(row["cesarean_pct"]),
                    },
                    "health_indicators": {
                        "low_birth_weight_pct": float(row["low_birth_weight_pct"]),
                        "low_apgar5_pct": float(row["low_apgar5_pct"]),
                    },
                    "location": {
                        "hospital_birth_pct": float(row["hospital_birth_pct"]),
                    },
                    "maternal_occupation": maternal_occupation,
                }
            )

        return {
            "years": sorted([s["year"] for s in yearly_summaries]),
            "yearly_summaries": yearly_summaries,
            "generated_at": pd.Timestamp.now().isoformat(),
            "source": "database",
        }

    def get_metadata(self) -> dict:
        """Get metadata dictionary."""
        return self.metadata

    def get_available_years(self) -> list[int]:
        """Get list of available years."""
        return self.available_years

    def _add_count_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add _count columns computed from _pct columns.

        Dashboard expects absolute count columns but database only has percentages.
        This computes: count = (total_births * pct / 100).round()

        Args:
            df: DataFrame with _pct columns and total_births

        Returns:
            DataFrame with added _count columns
        """
        if "total_births" not in df.columns:
            return df

        pct_to_count_mapping = {
            "cesarean_pct": "cesarean_count",
            "preterm_pct": "preterm_count",
            "extreme_preterm_pct": "extreme_preterm_count",
            "adolescent_pregnancy_pct": "adolescent_pregnancy_count",
            "very_young_pregnancy_pct": "very_young_pregnancy_count",
            "low_birth_weight_pct": "low_birth_weight_count",
            "low_apgar5_pct": "low_apgar5_count",
        }

        for pct_col, count_col in pct_to_count_mapping.items():
            if count_col in df.columns:
                continue
            if pct_col in df.columns:
                df[count_col] = (df["total_births"] * df[pct_col] / 100).round().astype(int)

        return df

    def get_year_summary(self, year: int) -> dict:
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
        Load monthly aggregated data for a specific year from database.

        Args:
            year: Year to load

        Returns:
            DataFrame with monthly statistics
        """
        query = "SELECT * FROM agg_monthly WHERE year = %(year)s ORDER BY month"
        df = pd.read_sql(query, self.engine, params={"year": year})

        if df.empty:
            raise ValueError(f"No monthly aggregates found for year {year}")

        # Add computed columns expected by dashboard
        df["year_month"] = pd.to_datetime(df["year"].astype(str) + "-" + df["month"].astype(str).str.zfill(2) + "-01")
        df["month_label"] = df["month"].apply(lambda x: MONTH_NAMES[x - 1])

        # Add _count columns computed from _pct columns (dashboard expects these)
        df = self._add_count_columns(df)

        return df

    @lru_cache(maxsize=10)
    def load_municipality_aggregates(self, year: int) -> pd.DataFrame:
        """
        Load municipality aggregates for a specific year from database.

        Args:
            year: Year to load

        Returns:
            DataFrame with municipality aggregates
        """
        query = "SELECT * FROM agg_municipality_yearly WHERE year = %(year)s ORDER BY total_births DESC"
        df = pd.read_sql(query, self.engine, params={"year": year})

        if df.empty:
            raise ValueError(f"No municipality aggregates found for year {year}")

        # Add _count columns computed from _pct columns
        df = self._add_count_columns(df)

        return df

    @lru_cache(maxsize=1)
    def load_yearly_aggregates(self) -> pd.DataFrame:
        """
        Load yearly aggregates with key indicators per year from database.

        Returns:
            DataFrame with yearly aggregates
        """
        df = pd.read_sql_table("agg_yearly", self.engine)
        # Add _count columns computed from _pct columns
        df = self._add_count_columns(df)
        return df

    @lru_cache(maxsize=10)
    def load_yearly_state_aggregates(self, year: int) -> pd.DataFrame:
        """
        Load yearly state-level aggregates from the production database.

        Args:
            year: The year to load data for.

        Returns:
            A DataFrame with aggregated data for all states for the given year.
        """
        # The table name is based on the pipeline script `step_05_aggregate.py`
        table_name = "agg_state_yearly"
        sql = f"SELECT * FROM {table_name} WHERE year = {year};"

        try:
            return pd.read_sql(sql, self.engine)
        except Exception as e:
            print(f"Error loading data from {table_name}: {e}")
            return pd.DataFrame()

    @lru_cache(maxsize=10)
    def load_occupation_aggregates(self, year: int) -> pd.DataFrame:
        """
        Load maternal occupation aggregates for a specific year from database.

        Args:
            year: Year to load

        Returns:
            DataFrame with occupation aggregates
        """
        query = "SELECT * FROM agg_occupation_yearly WHERE year = %(year)s ORDER BY total_births DESC"
        df = pd.read_sql(query, self.engine, params={"year": year})

        if df.empty:
            raise ValueError(f"No occupation aggregates found for year {year}")

        return df

    @lru_cache(maxsize=1)
    def load_combined_yearly(self) -> pd.DataFrame:
        """
        Load combined yearly data for multi-year comparison.

        Note: This is now the same as load_yearly_aggregates() since all
        yearly data is in the agg_yearly table.

        Returns:
            DataFrame with combined yearly data
        """
        return self.load_yearly_aggregates()

    def load_essential_data(self, year: int, columns: None | list[str] = None) -> pd.DataFrame:
        """
        Load essential columns data for a specific year.

        WARNING: This method loads individual birth records from the fact table
        and can be very slow for large years (2M+ records). Only use for specific
        analysis; prefer pre-aggregated tables for dashboard visualizations.

        Args:
            year: Year to load
            columns: Optional list of columns to load (loads all if None)

        Returns:
            DataFrame with essential data from fact_births table
        """
        raise NotImplementedError(
            "Loading individual records from fact_births is not recommended for dashboard use. "
            "This can be extremely slow for years with millions of records. "
            "Please use pre-aggregated tables: load_yearly_aggregates(), load_monthly_aggregates(), "
            "load_state_aggregates(), or load_municipality_aggregates() instead."
        )

    def get_date_range(self, year: int) -> dict[str, str]:
        """
        Get date range for a specific year.

        Args:
            year: Year to get range for

        Returns:
            Dictionary with 'min' and 'max' dates
        """
        summary = self.get_year_summary(year)
        return summary.get("date_range", {})

    @lru_cache(maxsize=10)
    def load_population_data(self, level: str = "states") -> pd.DataFrame:
        """
        Load population estimates by state from the database.

        Args:
            year: Optional year to filter (loads all years if None)

        Returns:
            DataFrame with columns: state_code, state_name, year, population
        """
        if level == "regions":
            query = f"SELECT id as region_code, name as region_name, count as population FROM dim_ibge_population_{level}"

        elif level == "states":
            query = f"SELECT id as state_code, name as state_name, count as population FROM dim_ibge_population_{level}"

        elif level == "municipalities":
            query = f"SELECT id as municipality_code, name as municipality_name, count as population FROM dim_ibge_population_{level}"
        else:
            raise ValueError(f"Invalid level '{level}'. Must be one of: 'regions', 'states', 'municipalities'.")

        df = pd.read_sql(query, self.engine)

        if df.empty:
            raise ValueError("No population data found.")

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
        state_df = self.load_yearly_state_aggregates(year)

        # Load population data
        pop_df = self.load_population_data("states")

        # Ensure 'state_code' columns have the same data type
        state_df["state_code"] = state_df["state_code"].astype(str)
        pop_df["state_code"] = pop_df["state_code"].astype(str)

        # Merge on state_code
        merged_df = state_df.merge(pop_df[["state_code", "population"]], on="state_code", how="left")

        # Calculate per-capita rates (births per 1,000 population)
        if "total_births" in merged_df.columns:
            merged_df["births_per_1k"] = (merged_df["total_births"] / merged_df["population"]) * 1000

        return merged_df

    # helper
    @lru_cache(maxsize=1)
    def _load_municipality_mapping(self) -> dict[str, str]:
        """
        Load municipality code -> name mapping from available sources (cached).

        Returns:
            Dictionary mapping id to name
        """
        try:
            query = "SELECT id, name FROM dim_ibge_id_municipalities"
            df_db = pd.read_sql(query, self.engine, dtype={"id": str})
            if not df_db.empty:
                return dict(zip(df_db["id"], df_db["name"]))
        except Exception:
            pass

        # If all fails, return empty dict
        return {}

    @lru_cache(maxsize=1)
    def _load_state_mapping(self) -> dict[str, str]:
        """
        Load state code -> name mapping from available sources (cached).

        Returns:
            Dictionary mapping id to name
        """
        try:
            query = "SELECT id, name FROM dim_ibge_id_states"
            df_db = pd.read_sql(query, self.engine, dtype={"id": str})
            if not df_db.empty:
                return dict(zip(df_db["id"], df_db["name"]))
        except Exception:
            pass

        # If all fails, return empty dict
        return {}

    @lru_cache(maxsize=1)
    def _load_brazil_states_geojson(self) -> dict[str, Any]:
        """
        Load Brazil states GeoJSON from DB.

        The geometry column is stored as WKB (Well-Known Binary) encoded as hex strings
        in the database. We parse it to Shapely geometries, fix validity/orientation,
        and export a GeoJSON FeatureCollection.

        Returns:
            GeoJSON-like dict (gdf.__geo_interface__) or empty dict on failure
        """
        query = "SELECT id, geometry FROM dim_ibge_geojson_states"
        try:
            # Read the data as plain SQL (geometry is stored as WKT text)
            df = pd.read_sql(query, self.engine, dtype={"id": str})

            if df.empty:
                return {}

            if "geometry" not in df.columns:
                return {}

            def parse_geometry(geom_str):
                if not geom_str or not isinstance(geom_str, str):
                    return None
                try:
                    # Convert hex string to bytes, then parse as WKB
                    return wkb.loads(bytes.fromhex(geom_str))
                except Exception:
                    return None

            df["geometry"] = df["geometry"].apply(parse_geometry)  # type: ignore

            # Remove rows with invalid geometries
            df = df[df["geometry"].notna()].copy()

            # Normalize state ids to 2-digit strings matching IBGE UF codes
            if "id" in df.columns:
                df["id"] = df["id"].astype(str).str.zfill(2)

            if df.empty:
                return {}

            # Create GeoDataFrame
            gdf = gpd.GeoDataFrame(df, geometry="geometry", crs="EPSG:4326")

            # Enforce polygon ring orientation (exterior CW for sign=-1) to avoid outside fill issues
            gdf["geometry"] = gdf["geometry"].apply(lambda g: orient(g, sign=-1) if g is not None else None)
            # Drop empty geometries if any
            gdf = gdf[~gdf.geometry.is_empty]

            return gdf.__geo_interface__

        except Exception as e:
            print(f"Error loading Brazil GeoJSON from database: {e}")
            import traceback

            traceback.print_exc()
            return {}


# Global data loader instance
# Uses staging DB if PROD_POSTGRES_INTERNAL_DATABASE_URL is not set
try:
    _use_staging = os.getenv("PROD_LOCAL_DATABASE_URL") is None
except ValueError:
    _use_staging = False
try:
    _use_local = os.getenv("PROD_POSTGRES_INTERNAL_DATABASE_URL") is not None
except ValueError:
    _use_local = False

data_loader = DataLoader(use_staging=_use_staging, use_local=_use_local)
