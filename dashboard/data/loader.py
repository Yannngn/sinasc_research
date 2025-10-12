"""
Data loading utilities for SINASC Dashboard.

This module provides database-backed data loading for the dashboard,
replacing the previous Parquet file-based approach.
"""

from functools import lru_cache
from typing import Any

import geopandas as gpd
import pandas as pd
from config.constants import MONTH_NAMES
from shapely import wkb
from shapely.ops import orient

from data.database import get_local_db_engine, get_prod_db_engine, get_staging_db_engine


class DataLoader:
    """
    Database-backed data loader with caching for dashboard.

    Loads data directly from PostgreSQL aggregate tables instead of Parquet files.
    """

    def __init__(self):
        """
        Initialize data loader.

        Args:
            use_staging: If True, connect to staging DB; otherwise production DB
            use_local: If True, connect to local DB; otherwise remote DB
            use_onrender: If True, connect to OnRender DB; otherwise remote DB
        """

        # Attempt connections in order: local -> prod internal -> staging
        try:
            self.engine = get_local_db_engine()
        except ValueError as e_local:
            try:
                self.engine = get_prod_db_engine()
            except ValueError as e_prod:
                try:
                    self.engine = get_staging_db_engine()
                except ValueError as e_staging:
                    raise ValueError(
                        f"Failed to connect to any database. Local error: {e_local}; Prod internal error: {e_prod}; Staging error: {e_staging}"
                    )

        self.metadata = self._load_metadata_from_db()
        self.available_years = self.metadata.get("years", [])
        self.geojson_cache = {}

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

        # Read monthly aggregates and ensure ordered by year, month
        df_monthly = pd.read_sql_table("agg_monthly", self.engine).sort_values(["year", "month"])

        monthly_summaries = []
        for _, row in df_monthly.iterrows():
            year = int(row["year"])
            month = int(row["month"])
            month_label = MONTH_NAMES[month - 1] if 1 <= month <= 12 else ""

            monthly_summaries.append(
                {
                    "year": year,
                    "month": month,
                    "month_label": month_label,
                    "total_births": int(row["total_births"]),
                    "adolescent_pregnancy_pct": float(row["adolescent_pregnancy_pct"]),
                    "very_young_pregnancy_pct": float(row["very_young_pregnancy_pct"]),
                    "preterm_pct": float(row["preterm_pct"]),
                    "extreme_preterm_pct": float(row["extreme_preterm_pct"]),
                    "cesarean_pct": float(row["cesarean_pct"]),
                    "low_birth_weight_pct": float(row["low_birth_weight_pct"]),
                    "low_apgar5_pct": float(row["low_apgar5_pct"]),
                    "hospital_birth_pct": float(row["hospital_birth_pct"]),
                }
            )

        return {
            "years": sorted([s["year"] for s in yearly_summaries]),
            "yearly_summaries": yearly_summaries,
            "monthly_summaries": monthly_summaries,
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

    def _add_per_1k_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add _per_1k columns computed from _count columns and population.

        Args:
            df: DataFrame with _count columns and population
        """
        if "population" not in df.columns:
            return df

        count_to_per_1k_mapping = {
            "cesarean_count": "cesarean_per_1k",
            "preterm_count": "preterm_per_1k",
            "extreme_preterm_count": "extreme_preterm_per_1k",
            "adolescent_pregnancy_count": "adolescent_pregnancy_per_1k",
            "very_young_pregnancy_count": "very_young_pregnancy_per_1k",
            "low_birth_weight_count": "low_birth_weight_per_1k",
            "low_apgar5_count": "low_apgar5_per_1k",
            "total_births": "births_per_1k",
        }

        for count_col, per_1k_col in count_to_per_1k_mapping.items():
            if per_1k_col in df.columns:
                continue
            if count_col in df.columns:
                # Avoid division by zero or by NA
                df[per_1k_col] = (df[count_col] / df["population"]) * 1000

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

    ### GENERAL LOADERS

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

    ### POPULATION HELPER

    @lru_cache(maxsize=3)
    def load_population_data(self, level: str = "state", limiter: str | None = None) -> pd.DataFrame:
        """
        Load population estimates by geographic level from the database.

        Args:
            level: Geographic level to load. Must be one of: 'region', 'state', 'municipality'.
            limiter: Optional prefix filter for the geographic id (e.g., '25' to filter states/municipalities
                     whose codes start with '25').

        Returns:
            pd.DataFrame: DataFrame with columns depending on level:
                - region:  ['region_code', 'region_name', 'population']
                - state:   ['state_code', 'state_name', 'population']
                - municipality: ['municipality_code', 'municipality_name', 'population']

        Raises:
            ValueError: If `level` is not one of 'region', 'state', or 'municipality'.
        """
        params = None
        if level == "region":
            query = "SELECT id as region_code, name as region_name, count as population FROM dim_ibge_population_regions WHERE 1=1"
            if limiter:
                query += " AND id LIKE %(limiter)s"
                params = {"limiter": f"{limiter}%"}

        elif level == "state":
            query = "SELECT id as state_code, name as state_name, count as population FROM dim_ibge_population_states WHERE 1=1"
            if limiter:
                query += " AND id LIKE %(limiter)s"
                params = {"limiter": f"{limiter}%"}

        elif level == "municipality":
            query = "SELECT id as municipality_code, name as municipality_name, count as population FROM dim_ibge_population_municipalities WHERE 1=1"
            if limiter:
                query += " AND id LIKE %(limiter)s"
                params = {"limiter": f"{limiter}%"}

        elif level == "brazil":
            query = "SELECT count as population FROM dim_ibge_population_brazil"
            params = None

        else:
            raise ValueError(f"Invalid level '{level}'. Must be one of: 'region', 'state', 'municipality'.")

        df = pd.read_sql(query, self.engine, params=params)

        if df.empty:
            return pd.DataFrame()

        return df

    ### AGG HELPER

    def load_yearly_aggregates_with_params(
        self, year: int | None = None, level: str = "brazil", limiter: str | None = None, population: bool = False
    ) -> pd.DataFrame:
        """
        Load yearly aggregates for a specific level from the database.

        Args:
            year: Year to load
            level: Geographic level ("brazil", "state", "municipality")
            limiter: Optional limiter filter (e.g., state code prefix)
            population: Whether to include population data

        Returns:
            DataFrame with yearly aggregates
        """
        table = f"agg_{level}_yearly"
        limiter_col = f"{level}_code" if level != "brazil" else None

        query, params = self._generate_query(table=table, year=year, limiter_col=limiter_col, limiter=limiter)
        df = pd.read_sql(query, self.engine, params=params)

        if df.empty:
            return pd.DataFrame()

        # Add _count columns computed from _pct columns
        df = self._add_count_columns(df)

        if population:
            # Load and merge population data
            df_population = self.load_population_data(level=level, limiter=limiter)
            code_col = f"{level}_code"

            if level == "brazil":
                df["population"] = df_population["population"].item() if not df_population.empty else pd.NA
            elif level in ["region", "state"]:
                df[code_col] = df[code_col].astype(str)
                df_population[code_col] = df_population[code_col].astype(str)
                df = df.merge(df_population[[code_col, "population"]], on=code_col, how="left")

                if level == "state":
                    state_map = self.load_state_id_mapping()
                    df["state_name"] = df[code_col].map(state_map)
            elif level == "municipality":
                df[code_col] = df[code_col].astype(str)
                df_population[code_col] = df_population[code_col].astype(str)
                df = df.merge(df_population[[code_col, "population"]], on=code_col, how="left")

                # Add municipality names
                mun_map = self.load_municipality_id_mapping()
                df["municipality_name"] = df[code_col].map(mun_map)
            else:
                raise ValueError(f"Invalid level '{level}' for population merge.")

            df = self._add_per_1k_columns(df)

        return df

    def load_monthly_aggregates_with_params(
        self, year: int | None = None, month: int | None = None, level: str = "brazil", limiter: str | None = None, population: bool = False
    ) -> pd.DataFrame:
        """
        Load municipality aggregates for a specific year from database.

        Args:
            level: Geographic level ("state" or "municipality")
            year: Year to load
            limiter: 1-digit region code or 2-digit state code (e.g., '25' for Paraíba)

        Returns:
            DataFrame with municipality aggregates
        """
        if level == "brazil":
            query, params = self._generate_query(table="agg_monthly", year=year)
        else:
            table = f"agg_{level}_monthly"
            limiter_col = f"{level}_code"

            query, params = self._generate_query(table=table, year=year, month=month, limiter_col=limiter_col, limiter=limiter)

        df = pd.read_sql(query, self.engine, params=params)

        if df.empty:
            return pd.DataFrame()

        # Add _count columns computed from _pct columns
        df = self._add_count_columns(df)

        if population:
            # Load and merge population data

            df_population = self.load_population_data(level=level, limiter=limiter)

            if level == "brazil":
                df["population"] = df_population["population"].iloc[0] if not df_population.empty else pd.NA
            else:
                # Ensure codes are zero-padded strings for merging
                code_col = f"{level}_code"
                df[code_col] = df[code_col].astype(str)
                df_population[code_col] = df_population[code_col].astype(str)

                df = df.merge(df_population[[code_col, "population"]], on=code_col, how="left")

            df = self._add_per_1k_columns(df)

        return df

    ### STATE-LEVEL LOADERS

    @lru_cache(maxsize=1)
    def load_yearly_state_aggregates(self, population: bool = False) -> pd.DataFrame:
        """
        Load yearly state-level aggregates from the production database.

        Args:
            year: The year to load data for.

        Returns:
            A DataFrame with aggregated data for all states for the given year.
        """
        return self.load_yearly_aggregates_with_params(year=None, level="state", population=population)

    @lru_cache(maxsize=10)
    def load_monthly_state_aggregates(self, year: int, population: bool = False) -> pd.DataFrame:
        """
        Load monthly state-level aggregates from the production database.

        Args:
            year: The year to load data
        """
        return self.load_monthly_aggregates_with_params(year=year, level="state", population=population)

    ### MUNICIPALITY-LEVEL LOADERS

    @lru_cache(maxsize=100)
    def load_yearly_municipality_aggregates(self, year: int, limiter: str = "25", population: bool = False) -> pd.DataFrame:
        """
        Load yearly municipality aggregates from the production database.

        Args:
            year: The year to load data for.

        Returns:
            A DataFrame with aggregated data for all municipalities for the given year.
        """
        return self.load_yearly_aggregates_with_params(year=year, level="municipality", limiter=limiter, population=population)

    @lru_cache(maxsize=100)
    def load_monthly_municipality_aggregates(self, year: int, month: int, limiter: str = "25", population: bool = False) -> pd.DataFrame:
        """
        Load monthly municipality aggregates from the production database.

        Args:
            year: The year to load data for.
            month: The month to load data for.

        Returns:
            A DataFrame with aggregated data for all municipalities for the given year and month.
        """
        return self.load_monthly_aggregates_with_params(year=year, month=month, level="municipality", limiter=limiter, population=population)

    # helper
    @lru_cache(maxsize=1)
    def load_municipality_id_mapping(self) -> dict[str, str]:
        """
        Load municipality code -> name mapping from available sources (cached).

        Returns:
            Dictionary mapping id to name
        """
        try:
            query = "SELECT id, name FROM dim_ibge_id_municipalities"
            df_db = pd.read_sql(query, self.engine, dtype={"id": str})
            df_db["id"] = df_db["id"].astype(str)
            if not df_db.empty:
                return dict(zip(df_db["id"], df_db["name"]))
        except Exception:
            pass

        # If all fails, return empty dict
        return {}

    @lru_cache(maxsize=1)
    def load_state_id_mapping(self) -> dict[str, str]:
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

    def load_geojson_states(self, limiter: str | None = None) -> dict[str, Any]:
        return self._load_geojson(level="states", limiter=limiter)

    def load_geojson_municipalities(self, limiter: str | None = None) -> dict[str, Any]:
        df = self._load_geojson(level="municipalities", limiter=limiter)

        return df

    @lru_cache(maxsize=12)
    def _load_geojson(self, level: str = "states", limiter: str | None = None) -> dict[str, Any]:
        """
        Load Brazil states GeoJSON from DB.

        The geometry column is stored as WKB (Well-Known Binary) encoded as hex strings
        in the database. We parse it to Shapely geometries, fix validity/orientation,
        and export a GeoJSON FeatureCollection.

        Args:
            level: Geographic level ("states" or "municipalities")
            limiter: Optional filter string. If provided, only select geometries where id starts with this string
                    (e.g., '1' for region 1, '21' for state 21)

        Returns:
            GeoJSON-like dict (gdf.__geo_interface__) or empty dict on failure
        """
        query = f"SELECT id, geometry FROM dim_ibge_geojson_{level}"
        params = {}

        if limiter is not None:
            query += " WHERE id LIKE %(limiter)s"
            params["limiter"] = f"{limiter}%"

        try:
            # Read the data as plain SQL (geometry is stored as WKT text)
            df = pd.read_sql(query, self.engine, params=params, dtype={"id": str})

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

            if level == "municipalities":
                df["id"] = df["id"].astype(str)

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

    def _generate_query(
        self, table: str, year: int | None = None, month: int | None = None, limiter_col: str | None = None, limiter: str | None = None
    ) -> tuple[str, tuple]:
        """
        Generate SQL query with optional filters.

        Args:
            table: Table name to query
            year: Optional year filter
            month: Optional month filter
            limiter_col: Optional column name for limiter filter
            limiter: Optional limiter filter (e.g., state code prefix)

        Returns:
            Tuple of SQL query string and parameters tuple
        """
        if month is not None and year is None:
            raise ValueError("Month filter requires year to be specified")

        query = f"SELECT * FROM {table} WHERE 1=1"
        params = []

        if year is not None:
            query += " AND year = %s"
            params.append(year)
        if month is not None:
            query += " AND month = %s"
            params.append(month)
        if limiter is not None and limiter_col is not None:
            query += f" AND {limiter_col} LIKE %s"
            params.append(f"{limiter}%")

        query += f" ORDER BY year DESC{', month DESC' if month is not None else ''}, total_births DESC"

        return query, tuple(params)


data_loader = DataLoader()
