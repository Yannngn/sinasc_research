"""
Create optimized data files for the SINASC dashboard.

This script generates lightweight, pre-aggregated files for efficient web deployment:
1. Essential columns subset (reduced memory)
2. Monthly aggregates (time-series analysis)
3. State/municipality aggregates (geographic analysis)
4. Yearly summaries (overview metrics)
5. Metadata (schema, counts, date ranges)

Usage:
    python create_dashboard_data.py --year 2024
    python create_dashboard_data.py --year 2024 --output_dir dashboard_data
    python create_dashboard_data.py --all  # Process all available years
"""

import argparse
import json
import os
from pathlib import Path

import pandas as pd

# Essential columns for dashboard (reduced from 51 to ~25)
ESSENTIAL_COLUMNS = [
    # Temporal
    "DTNASC",  # data de nascimento
    "HORANASC",  # hora de nascimento
    # Geographic
    "CODMUNNASC",  # cod municipio nascimento
    "CODMUNRES",  # cod municipio residencia
    # Demographics
    "IDADEMAE",  # idade mae
    "IDADEPAI",  # idade pai
    "ESTCIVMAE",  # estado civil mae
    "ESCMAE",  # escolaridade mae
    "RACACOR",  # raca/cor rn
    "RACACORMAE",  # raca/cor mae
    "SEXO",  # sexo rn (0=ignorado, 1=masc, 2=fem)
    # Prenatal care
    "CONSULTAS",  # categorical
    "CONSPRENAT",  # qtd consultas
    "MESPRENAT",  # mes do inicio do prenatal
    "KOTELCHUCK",  # indice kotelchuck
    # Pregnancy
    "GRAVIDEZ",  # unica, gemelar, etc
    "QTDGESTANT",  # qtd gestacoes prévias
    "GESTACAO",  # categoria duração da gestação
    "SEMAGESTAC",  # qtd semanas gestacao
    # Delivery
    "LOCNASC",  # categoria loc nasc
    "CODESTAB",  # cod cnes
    "PARTO",  # tipo parto
    "TPROBSON",  # robson
    # Newborn health
    "PESO",
    "APGAR1",
    "APGAR5",
    # Engineered
    "IDADEMAEBIN",  #
    "PESOBIN",
    "DESLOCNASCBOOL",
    "OCUPMAE",
]


def create_essential_subset(df: pd.DataFrame, year: int, output_dir: str) -> str:
    """
    Create essential columns subset for detailed analysis.

    Args:
        df: Input DataFrame
        year: Year of the data
        output_dir: Output directory path

    Returns:
        Path to created file
    """
    print(f"📊 Creating essential columns subset for {year}...")

    # Select available columns
    available_cols = [col for col in ESSENTIAL_COLUMNS if col in df.columns]
    df_essential = df[available_cols].copy()

    # Optimize memory
    for col in df_essential.columns:
        if df_essential[col].dtype == "object":
            df_essential[col] = df_essential[col].astype("string")

    # Save
    output_path = os.path.join(output_dir, "years", f"{year}_essential.parquet")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df_essential.to_parquet(output_path, compression="snappy", index=False)

    file_size = os.path.getsize(output_path) / 1024**2
    print(f"  ✅ Saved {len(df_essential):,} records, {len(available_cols)} columns ({file_size:.1f} MB)")

    return output_path


def create_monthly_aggregates(df: pd.DataFrame, year: int, output_dir: str) -> str:
    """
    Create monthly aggregated statistics.

    Args:
        df: Input DataFrame with DTNASC column
        year: Year of the data
        output_dir: Output directory path

    Returns:
        Path to created file
    """
    print(f"📅 Creating monthly aggregates for {year}...")

    # Ensure datetime
    if df["DTNASC"].dtype != "datetime64[ns]":
        df["DTNASC"] = pd.to_datetime(df["DTNASC"], format="%d%m%Y", errors="coerce")

    # Create month column
    df["year_month"] = df["DTNASC"].dt.to_period("M").astype(str)

    # Aggregate by month
    monthly = df.groupby("year_month").agg(
        {
            "DTNASC": "count",  # Total births
            "PESO": ["mean", "median", "std"],
            "IDADEMAE": ["mean", "median", "std"],
            "SEMAGESTAC": ["mean", "median", "std"],  # Gestational weeks
            "APGAR1": "mean",
            "APGAR5": "mean",
        }
    )

    # Flatten column names
    monthly.columns = ["_".join(col).strip() for col in monthly.columns.values]
    monthly = monthly.rename(columns={"DTNASC_count": "total_births"})

    # Add categorical aggregates
    if "PARTO" in df.columns:
        # Convert to numeric for comparison
        cesarean_rate = df.groupby("year_month").apply(
            lambda x: (pd.to_numeric(x["PARTO"], errors="coerce") == 2).mean() * 100,  # type: ignore
            include_groups=False,  # type: ignore
        )  # type: ignore
        monthly["cesarean_pct"] = cesarean_rate

    if "GRAVIDEZ" in df.columns:
        # Convert to numeric for comparison
        multiple_rate = df.groupby("year_month").apply(
            lambda x: (pd.to_numeric(x["GRAVIDEZ"], errors="coerce") > 1).mean() * 100,  # type: ignore
            include_groups=False,  # type: ignore
        )  # type: ignore
        monthly["multiple_pregnancy_pct"] = multiple_rate

    if "LOCNASC" in df.columns:
        # Convert to numeric for comparison
        hospital_rate = df.groupby("year_month").apply(
            lambda x: (pd.to_numeric(x["LOCNASC"], errors="coerce") == 1).mean() * 100,  # type: ignore
            include_groups=False,  # type: ignore
        )  # type: ignore
        monthly["hospital_birth_pct"] = hospital_rate

    # Add preterm births (GESTACAO < 5 means < 37 weeks)
    if "GESTACAO" in df.columns:
        preterm_rate = df.groupby("year_month").apply(
            lambda x: (pd.to_numeric(x["GESTACAO"], errors="coerce") < 5).mean() * 100,  # type: ignore
            include_groups=False,  # type: ignore
        )  # type: ignore
        monthly["preterm_birth_pct"] = preterm_rate
        monthly["preterm_birth_count"] = (monthly["total_births"] * monthly["preterm_birth_pct"] / 100).round().astype(int)

        # Add extreme preterm births (GESTACAO < 3 means < 32 weeks)
        extreme_preterm_rate = df.groupby("year_month").apply(
            lambda x: (pd.to_numeric(x["GESTACAO"], errors="coerce") < 3).mean() * 100,  # type: ignore
            include_groups=False,  # type: ignore
        )  # type: ignore
        monthly["extreme_preterm_birth_pct"] = extreme_preterm_rate
        monthly["extreme_preterm_birth_count"] = (monthly["total_births"] * monthly["extreme_preterm_birth_pct"] / 100).round().astype(int)

    # Add adolescent pregnancies (IDADEMAE < 20)
    if "IDADEMAE" in df.columns:
        adolescent_rate = df.groupby("year_month").apply(
            lambda x: (pd.to_numeric(x["IDADEMAE"], errors="coerce") < 20).mean() * 100,  # type: ignore
            include_groups=False,  # type: ignore
        )  # type: ignore
        monthly["adolescent_pregnancy_pct"] = adolescent_rate
        monthly["adolescent_pregnancy_count"] = (monthly["total_births"] * monthly["adolescent_pregnancy_pct"] / 100).round().astype(int)

        # Add very young pregnancies (IDADEMAE < 15)
        very_young_rate = df.groupby("year_month").apply(
            lambda x: (pd.to_numeric(x["IDADEMAE"], errors="coerce") < 15).mean() * 100,  # type: ignore
            include_groups=False,  # type: ignore
        )  # type: ignore
        monthly["very_young_pregnancy_pct"] = very_young_rate
        monthly["very_young_pregnancy_count"] = (monthly["total_births"] * monthly["very_young_pregnancy_pct"] / 100).round().astype(int)

    # Add low birth weight (PESO < 2500g)
    if "PESO" in df.columns:
        low_weight_rate = df.groupby("year_month").apply(
            lambda x: (pd.to_numeric(x["PESO"], errors="coerce") < 2500).mean() * 100,  # type: ignore
            include_groups=False,  # type: ignore
        )  # type: ignore
        monthly["low_birth_weight_pct"] = low_weight_rate
        monthly["low_birth_weight_count"] = (monthly["total_births"] * monthly["low_birth_weight_pct"] / 100).round().astype(int)

    # Add low APGAR5 (APGAR5 < 7)
    if "APGAR5" in df.columns:
        low_apgar_rate = df.groupby("year_month").apply(
            lambda x: (pd.to_numeric(x["APGAR5"], errors="coerce") < 7).mean() * 100,  # type: ignore
            include_groups=False,  # type: ignore
        )  # type: ignore
        monthly["low_apgar5_pct"] = low_apgar_rate
        monthly["low_apgar5_count"] = (monthly["total_births"] * monthly["low_apgar5_pct"] / 100).round().astype(int)

    # Reset index
    monthly = monthly.reset_index()

    # Save
    output_path = os.path.join(output_dir, "aggregates", f"monthly_{year}.parquet")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    monthly.to_parquet(output_path, compression="snappy", index=False)

    file_size = os.path.getsize(output_path) / 1024**2
    print(f"  ✅ Saved {len(monthly)} months of aggregates ({file_size:.2f} MB)")

    return output_path


def create_state_aggregates(df: pd.DataFrame, year: int, output_dir: str) -> str:
    """
    Create state-level aggregated statistics.

    Args:
        df: Input DataFrame with CODMUNNASC column
        year: Year of the data
        output_dir: Output directory path

    Returns:
        Path to created file
    """
    print(f"🗺️  Creating state aggregates for {year}...")

    # Extract state code from municipality code (first 2 digits)
    df["state_code"] = df["CODMUNNASC"].astype(str).str[:2]

    # Aggregate by state
    state_agg = df.groupby("state_code").agg(
        {
            "CODMUNNASC": "count",  # Total births
            "PESO": ["mean", "median", "std"],
            "IDADEMAE": ["mean", "median"],
            "SEMAGESTAC": ["mean", "median"],  # Gestational weeks
            "APGAR1": "mean",
            "APGAR5": "mean",
        }
    )

    # Flatten column names
    state_agg.columns = ["_".join(col).strip() for col in state_agg.columns.values]
    state_agg = state_agg.rename(columns={"CODMUNNASC_count": "total_births"})

    # Add categorical aggregates
    if "PARTO" in df.columns:
        cesarean_rate = df.groupby("state_code").apply(
            lambda x: (pd.to_numeric(x["PARTO"], errors="coerce") == 2).mean() * 100,  # type: ignore
            include_groups=False,  # type: ignore
        )  # type: ignore
        state_agg["cesarean_pct"] = cesarean_rate

    if "GRAVIDEZ" in df.columns:
        multiple_rate = df.groupby("state_code").apply(
            lambda x: (pd.to_numeric(x["GRAVIDEZ"], errors="coerce") > 1).mean() * 100,  # type: ignore
            include_groups=False,  # type: ignore
        )  # type: ignore
        state_agg["multiple_pregnancy_pct"] = multiple_rate

    if "LOCNASC" in df.columns:
        hospital_rate = df.groupby("state_code").apply(
            lambda x: (pd.to_numeric(x["LOCNASC"], errors="coerce") == 1).mean() * 100,  # type: ignore
            include_groups=False,  # type: ignore
        )  # type: ignore
        state_agg["hospital_birth_pct"] = hospital_rate

    if "GESTACAO" in df.columns:
        preterm_rate = df.groupby("state_code").apply(
            lambda x: (pd.to_numeric(x["GESTACAO"], errors="coerce") < 5).mean() * 100,  # type: ignore
            include_groups=False,  # type: ignore
        )  # type: ignore
        state_agg["preterm_rate_pct"] = preterm_rate
        state_agg["preterm_rate_count"] = (state_agg["total_births"] * state_agg["preterm_rate_pct"] / 100).round().astype(int)

        extreme_preterm_rate = df.groupby("state_code").apply(
            lambda x: (pd.to_numeric(x["GESTACAO"], errors="coerce") < 3).mean() * 100,  # type: ignore
            include_groups=False,  # type: ignore
        )  # type: ignore
        state_agg["extreme_preterm_rate_pct"] = extreme_preterm_rate
        state_agg["extreme_preterm_rate_count"] = (state_agg["total_births"] * state_agg["extreme_preterm_rate_pct"] / 100).round().astype(int)

    # Add low birth weight (PESO < 2500g)
    if "PESO" in df.columns:
        low_weight_rate = df.groupby("state_code").apply(
            lambda x: (pd.to_numeric(x["PESO"], errors="coerce") < 2500).mean() * 100,  # type: ignore
            include_groups=False,  # type: ignore
        )  # type: ignore
        state_agg["low_birth_weight_pct"] = low_weight_rate
        state_agg["low_birth_weight_count"] = (state_agg["total_births"] * state_agg["low_birth_weight_pct"] / 100).round().astype(int)

    # Add low APGAR5 (APGAR5 < 7)
    if "APGAR5" in df.columns:
        low_apgar_rate = df.groupby("state_code").apply(
            lambda x: (pd.to_numeric(x["APGAR5"], errors="coerce") < 7).mean() * 100,  # type: ignore
            include_groups=False,  # type: ignore
        )  # type: ignore
        state_agg["low_apgar5_pct"] = low_apgar_rate
        state_agg["low_apgar5_count"] = (state_agg["total_births"] * state_agg["low_apgar5_pct"] / 100).round().astype(int)

    # Reset index
    state_agg = state_agg.reset_index()

    # Save
    output_path = os.path.join(output_dir, "aggregates", f"state_{year}.parquet")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    state_agg.to_parquet(output_path, compression="snappy", index=False)

    file_size = os.path.getsize(output_path) / 1024**2
    print(f"  ✅ Saved {len(state_agg)} states with aggregates ({file_size:.2f} MB)")

    return output_path


def create_municipality_aggregates(df: pd.DataFrame, year: int, output_dir: str, top_n: int = 500) -> str:
    """
    Create municipality-level aggregated statistics (top N by birth count).

    Args:
        df: Input DataFrame with CODMUNNASC column
        year: Year of the data
        output_dir: Output directory path
        top_n: Number of top municipalities to include

    Returns:
        Path to created file
    """
    print(f"🏙️  Creating municipality aggregates for {year} (top {top_n})...")

    # Aggregate by municipality
    mun_agg = df.groupby("CODMUNNASC").agg(
        {
            "CODMUNNASC": "count",  # Total births
            "PESO": ["mean", "median"],
            "IDADEMAE": "mean",
            "APGAR5": "mean",
        }
    )

    # Flatten column names
    mun_agg.columns = ["_".join(col).strip() for col in mun_agg.columns.values]
    mun_agg = mun_agg.rename(columns={"CODMUNNASC_count": "total_births"})

    # Add cesarean rate if available
    if "PARTO" in df.columns:
        cesarean_rate = df.groupby("CODMUNNASC").apply(
            lambda x: (pd.to_numeric(x["PARTO"], errors="coerce") == 2).mean() * 100,  # type: ignore
            include_groups=False,  # type: ignore
        )
        mun_agg["cesarean_pct"] = cesarean_rate

    # Sort by birth count and take top N
    mun_agg = mun_agg.sort_values("total_births", ascending=False).head(top_n)

    # Reset index
    mun_agg = mun_agg.reset_index()

    # Save
    output_path = os.path.join(output_dir, "aggregates", f"municipality_{year}.parquet")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    mun_agg.to_parquet(output_path, compression="snappy", index=False)

    file_size = os.path.getsize(output_path) / 1024**2
    print(f"  ✅ Saved {len(mun_agg)} municipalities with aggregates ({file_size:.2f} MB)")

    return output_path


def create_yearly_summary(df: pd.DataFrame, year: int, output_dir: str) -> dict:
    """
    Create yearly summary statistics.

    Args:
        df: Input DataFrame
        year: Year of the data
        output_dir: Output directory path

    Returns:
        dictionary with summary statistics
    """
    print(f"📈 Creating yearly summary for {year}...")

    # Ensure datetime
    if "DTNASC" in df.columns and df["DTNASC"].dtype != "datetime64[ns]":
        df["DTNASC"] = pd.to_datetime(df["DTNASC"], format="%d%m%Y", errors="coerce")

    summary = {
        "year": year,
        "total_births": int(len(df)),
        "date_range": {
            "min": df["DTNASC"].min().isoformat() if "DTNASC" in df.columns else None,
            "max": df["DTNASC"].max().isoformat() if "DTNASC" in df.columns else None,
        },
        "maternal_age": {
            "mean": float(df["IDADEMAE"].mean()) if "IDADEMAE" in df.columns else None,
            "median": float(df["IDADEMAE"].median()) if "IDADEMAE" in df.columns else None,
            "std": float(df["IDADEMAE"].std()) if "IDADEMAE" in df.columns else None,
        },
        "birth_weight": {
            "mean": float(df["PESO"].mean()) if "PESO" in df.columns else None,
            "median": float(df["PESO"].median()) if "PESO" in df.columns else None,
            "std": float(df["PESO"].std()) if "PESO" in df.columns else None,
        },
        "apgar_scores": {
            "apgar1_mean": float(df["APGAR1"].mean()) if "APGAR1" in df.columns else None,
            "apgar5_mean": float(df["APGAR5"].mean()) if "APGAR5" in df.columns else None,
        },
        "delivery_type": {
            "cesarean_pct": float((pd.to_numeric(df["PARTO"], errors="coerce") == 2).mean() * 100) if "PARTO" in df.columns else None,
            "vaginal_pct": float((pd.to_numeric(df["PARTO"], errors="coerce") == 1).mean() * 100) if "PARTO" in df.columns else None,
        },
        "location": {
            "hospital_birth_pct": float((pd.to_numeric(df["LOCNASC"], errors="coerce") == 1).mean() * 100) if "LOCNASC" in df.columns else None,
            "unique_municipalities": int(df["CODMUNNASC"].nunique()) if "CODMUNNASC" in df.columns else None,
        },
        "pregnancy": {
            "multiple_pregnancy_pct": float((pd.to_numeric(df["GRAVIDEZ"], errors="coerce") > 1).mean() * 100)
            if "GRAVIDEZ" in df.columns
            else None,
            "preterm_birth_pct": float((pd.to_numeric(df["GESTACAO"], errors="coerce") < 5).mean() * 100) if "GESTACAO" in df.columns else None,
            "extreme_preterm_birth_pct": float((pd.to_numeric(df["GESTACAO"], errors="coerce") < 3).mean() * 100)
            if "GESTACAO" in df.columns
            else None,
            "adolescent_pregnancy_pct": float((pd.to_numeric(df["IDADEMAE"], errors="coerce") < 20).mean() * 100)
            if "IDADEMAE" in df.columns
            else None,
            "very_young_pregnancy_pct": float((pd.to_numeric(df["IDADEMAE"], errors="coerce") < 15).mean() * 100)
            if "IDADEMAE" in df.columns
            else None,
            "gestational_weeks_mean": float(df["SEMAGESTAC"].mean()) if "SEMAGESTAC" in df.columns else None,
            "gestational_weeks_median": float(df["SEMAGESTAC"].median()) if "SEMAGESTAC" in df.columns else None,
        },
        "health_indicators": {
            "low_birth_weight_pct": float((pd.to_numeric(df["PESO"], errors="coerce") < 2500).mean() * 100) if "PESO" in df.columns else None,
            "low_apgar5_pct": float((pd.to_numeric(df["APGAR5"], errors="coerce") < 7).mean() * 100) if "APGAR5" in df.columns else None,
        },
    }

    # Maternal occupation counts (OCUPMAE)
    # Map the known occupation group codes to human labels and count occurrences.
    # We include codes 1..7 plus 9 (Ignorado) as requested.
    if "OCUPMAE" in df.columns:
        summary["maternal_occupation"] = {}
        ocup_labels = {
            1: "Trabalhadora do Lar",
            2: "Estudante",
            3: "Trabalhadora Rural",
            4: "Profissionais das Ciências e das Artes",
            5: "Técnicos e Profissionais de Nível Médio",
            6: "Trabalhadores de Serviços Administrativos",
            7: "Trabalhadores dos Serviços, Vendedores do Comércio em Lojas e Mercados",
            9: "Ignorado",
        }

        # Coerce to numeric to allow safe comparison; missing/invalid become NaN
        df_ocup = pd.to_numeric(df["OCUPMAE"], errors="coerce")

        for code, label in ocup_labels.items():
            count = int(df_ocup.eq(code).sum())
            # store both label and raw count for clarity
            summary["maternal_occupation"][label] = count

    else:
        summary["maternal_occupation"] = None

    print("  ✅ Summary statistics computed")
    print(f"     Total births: {summary['total_births']:,}")
    print(f"     Avg maternal age: {summary['maternal_age']['mean']:.1f} years")
    print(f"     Avg birth weight: {summary['birth_weight']['mean']:.0f} grams")
    print(f"     Cesarean rate: {summary['delivery_type']['cesarean_pct']:.1f}%")
    print(f"     Low birth weight rate: {summary['health_indicators']['low_birth_weight_pct']:.1f}%")
    print(f"     Low APGAR5 rate: {summary['health_indicators']['low_apgar5_pct']:.1f}%")
    print(f"     Adolescent pregnancy rate: {summary['pregnancy']['adolescent_pregnancy_pct']:.1f}%")
    print(f"     Preterm birth rate: {summary['pregnancy']['preterm_birth_pct']:.1f}%")

    return summary


def create_yearly_aggregates(output_dir: str) -> str:
    """
    Create yearly aggregates file with key indicators per year.

    This creates a consolidated file similar to monthly aggregates but for years.

    Args:
        output_dir: Output directory path

    Returns:
        Path to created file
    """
    print("📊 Creating yearly aggregates...")

    aggregates_dir = os.path.join(output_dir, "aggregates")

    # Find all monthly aggregate files
    monthly_files = sorted(Path(aggregates_dir).glob("monthly_*.parquet"))

    if not monthly_files:
        print("  ⚠️  No monthly aggregate files found. Skipping yearly aggregates.")
        return None  # type: ignore

    # Load and aggregate by year
    yearly_data = []

    for file in monthly_files:
        year = int(file.stem.split("_")[1])
        df_monthly = pd.read_parquet(file)

        # Aggregate monthly data to yearly
        yearly_row = {
            "year": year,
            "total_births": df_monthly["total_births"].sum(),
            "birth_weight_mean": df_monthly["PESO_mean"].mean(),
            "birth_weight_median": df_monthly["PESO_median"].mean(),
            "birth_weight_std": df_monthly["PESO_std"].mean(),
            "mother_age_mean": df_monthly["IDADEMAE_mean"].mean(),
            "mother_age_median": df_monthly["IDADEMAE_median"].mean(),
            "gestational_age_mean": df_monthly["SEMAGESTAC_mean"].mean() if "SEMAGESTAC_mean" in df_monthly.columns else None,
            "gestational_age_median": df_monthly["SEMAGESTAC_median"].mean() if "SEMAGESTAC_median" in df_monthly.columns else None,
            "APGAR1_mean": df_monthly["APGAR1_mean"].mean(),
            "APGAR5_mean": df_monthly["APGAR5_mean"].mean(),
            "cesarean_pct": df_monthly["cesarean_pct"].mean(),
            "multiple_pregnancy_pct": df_monthly["multiple_pregnancy_pct"].mean(),
            "hospital_birth_pct": df_monthly["hospital_birth_pct"].mean(),
        }

        # Add preterm births if available
        if "preterm_birth_pct" in df_monthly.columns:
            yearly_row["preterm_birth_pct"] = df_monthly["preterm_birth_pct"].mean()
            yearly_row["preterm_birth_count"] = (yearly_row["total_births"] * yearly_row["preterm_birth_pct"] / 100).round().astype(int)

        # Add extreme preterm births if available
        if "extreme_preterm_birth_pct" in df_monthly.columns:
            yearly_row["extreme_preterm_birth_pct"] = df_monthly["extreme_preterm_birth_pct"].mean()
            yearly_row["extreme_preterm_birth_count"] = (
                (yearly_row["total_births"] * yearly_row["extreme_preterm_birth_pct"] / 100).round().astype(int)
            )

        # Add adolescent pregnancy if available
        if "adolescent_pregnancy_pct" in df_monthly.columns:
            yearly_row["adolescent_pregnancy_pct"] = df_monthly["adolescent_pregnancy_pct"].mean()
            yearly_row["adolescent_pregnancy_count"] = (
                (yearly_row["total_births"] * yearly_row["adolescent_pregnancy_pct"] / 100).round().astype(int)
            )

        # Add very young pregnancy if available
        if "very_young_pregnancy_pct" in df_monthly.columns:
            yearly_row["very_young_pregnancy_pct"] = df_monthly["very_young_pregnancy_pct"].mean()
            yearly_row["very_young_pregnancy_count"] = (
                (yearly_row["total_births"] * yearly_row["very_young_pregnancy_pct"] / 100).round().astype(int)
            )

        # Add low birth weight if available
        if "low_birth_weight_pct" in df_monthly.columns:
            yearly_row["low_birth_weight_pct"] = df_monthly["low_birth_weight_pct"].mean()
            yearly_row["low_birth_weight_count"] = (yearly_row["total_births"] * yearly_row["low_birth_weight_pct"] / 100).round().astype(int)

        # Add low APGAR5 if available
        if "low_apgar5_pct" in df_monthly.columns:
            yearly_row["low_apgar5_pct"] = df_monthly["low_apgar5_pct"].mean()
            yearly_row["low_apgar5_count"] = (yearly_row["total_births"] * yearly_row["low_apgar5_pct"] / 100).round().astype(int)

        yearly_data.append(yearly_row)

    # Create DataFrame
    df_yearly = pd.DataFrame(yearly_data)
    df_yearly = df_yearly.sort_values("year")

    if "gestational_age_mean" in df_yearly.columns:
        df_yearly["gestational_weeks_mean"] = df_yearly["gestational_age_mean"]

    df_yearly["cesarean_count"] = (df_yearly["total_births"] * df_yearly["cesarean_pct"] / 100).round().astype(int)
    df_yearly["vaginal_pct"] = 100 - df_yearly["cesarean_pct"]
    df_yearly["vaginal_count"] = (df_yearly["total_births"] * df_yearly["vaginal_pct"] / 100).round().astype(int)

    # Save
    output_path = os.path.join(aggregates_dir, "yearly.parquet")
    df_yearly.to_parquet(output_path, compression="snappy", index=False)

    file_size = os.path.getsize(output_path) / 1024
    print(f"  ✅ Saved yearly aggregates for {len(df_yearly)} years ({file_size:.1f} KB)")
    print(f"     Years: {df_yearly['year'].tolist()}")
    print(f"     Total births: {df_yearly['total_births'].sum():,}")

    return output_path


def create_combined_yearly(output_dir: str) -> str:
    """
    Create combined yearly summary from all processed years.

    Args:
        output_dir: Output directory path

    Returns:
        Path to created file
    """
    print("🔄 Creating combined yearly summary...")

    aggregates_dir = os.path.join(output_dir, "aggregates")

    # Find all state aggregate files
    state_files = sorted(Path(aggregates_dir).glob("state_*.parquet"))

    if not state_files:
        print("  ⚠️  No state aggregate files found. Skipping combined summary.")
        return None  # type: ignore

    # Load and combine
    dfs = []
    for file in state_files:
        year = file.stem.split("_")[1]
        df = pd.read_parquet(file)
        df["year"] = int(year)
        dfs.append(df)

    combined = pd.concat(dfs, ignore_index=True)

    # Save
    output_path = os.path.join(aggregates_dir, "combined_yearly.parquet")
    combined.to_parquet(output_path, compression="snappy", index=False)

    file_size = os.path.getsize(output_path) / 1024**2
    print(f"  ✅ Saved combined data for {len(state_files)} years ({file_size:.2f} MB)")

    return output_path


def create_metadata(summaries: list[dict], output_dir: str) -> str:
    """
    Create metadata file with information about all processed years.

    Args:
        summaries: list of yearly summary dictionaries
        output_dir: Output directory path

    Returns:
        Path to created file
    """
    print("📋 Creating metadata file...")

    metadata = {
        "generated_at": pd.Timestamp.now().isoformat(),
        "total_years": len(summaries),
        "years": sorted([s["year"] for s in summaries]),
        "total_records": sum(s["total_births"] for s in summaries),
        "date_range": {
            "min": min(s["date_range"]["min"] for s in summaries if s["date_range"]["min"]),
            "max": max(s["date_range"]["max"] for s in summaries if s["date_range"]["max"]),
        },
        "yearly_summaries": summaries,
        "schema": {
            "essential_columns": ESSENTIAL_COLUMNS,
            "aggregate_metrics": [
                "total_births",
                "PESO_mean",
                "PESO_median",
                "IDADEMAE_mean",
                "cesarean_pct",
                "hospital_birth_pct",
            ],
        },
    }

    output_path = os.path.join(output_dir, "metadata.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    file_size = os.path.getsize(output_path) / 1024
    print(f"  ✅ Saved metadata ({file_size:.1f} KB)")
    print(f"     Years: {metadata['years']}")
    print(f"     Total records: {metadata['total_records']:,}")

    return output_path


def process_year(year: int, data_dir: str, output_dir: str, dataset: str = "complete") -> dict:
    """
    Process a single year and create all dashboard files.

    Args:
        year: Year to process
        data_dir: Data directory path
        output_dir: Output directory path
        dataset: Dataset name (default: complete)

    Returns:
        dictionary with summary statistics
    """
    print(f"\n{'=' * 60}")
    print(f"Processing Year: {year}")
    print(f"{'=' * 60}\n")

    # Load data
    input_path = os.path.join(data_dir, str(year), f"{dataset}.parquet")

    if not os.path.exists(input_path):
        print(f"  ⚠️  File not found: {input_path}")
        print(f"  Skipping year {year}")
        return None  # type: ignore

    print(f"📥 Loading data from {input_path}...")
    df = pd.read_parquet(input_path)
    print(f"  ✅ Loaded {len(df):,} records with {len(df.columns)} columns\n")

    # Create all optimized files
    # create_essential_subset(df, year, output_dir)
    create_monthly_aggregates(df, year, output_dir)
    create_state_aggregates(df, year, output_dir)
    create_municipality_aggregates(df, year, output_dir, top_n=500)
    summary = create_yearly_summary(df, year, output_dir)

    print(f"\n✅ Year {year} processing complete!")

    return summary


def main():
    parser = argparse.ArgumentParser(description="Create optimized dashboard data files")
    parser.add_argument("--year", type=int, help="Year to process")
    parser.add_argument("--all", action="store_true", help="Process all available years")
    parser.add_argument("--data_dir", default="data/SINASC", help="Data directory")
    parser.add_argument("--output_dir", default="dashboard_data", help="Output directory")
    parser.add_argument("--dataset", default="complete", help="Dataset name (default: complete)")

    args = parser.parse_args()

    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)

    # Determine years to process
    if args.all:
        # Find all years with complete.parquet
        years = []
        for item in os.listdir(args.data_dir):
            year_path = os.path.join(args.data_dir, item)
            if os.path.isdir(year_path) and item.isdigit():
                complete_path = os.path.join(year_path, f"{args.dataset}.parquet")
                if os.path.exists(complete_path):
                    years.append(int(item))
        years = sorted(years)
        print(f"Found {len(years)} years to process: {years}")
    elif args.year:
        years = [args.year]
    else:
        print("Error: Must specify either --year or --all")
        return

    # Process each year
    summaries = []
    for year in years:
        summary = process_year(year, args.data_dir, args.output_dir, args.dataset)
        if summary:
            summaries.append(summary)

    # Create combined files
    if len(summaries) > 0:
        print(f"\n{'=' * 60}")
        print("Creating Combined Files")
        print(f"{'=' * 60}\n")

        create_yearly_aggregates(args.output_dir)
        create_combined_yearly(args.output_dir)
        create_metadata(summaries, args.output_dir)

    # Final summary
    print(f"\n{'=' * 60}")
    print("Dashboard Data Creation Complete!")
    print(f"{'=' * 60}\n")

    # Calculate total size
    total_size = 0
    for root, _dirs, files in os.walk(args.output_dir):
        for file in files:
            total_size += os.path.getsize(os.path.join(root, file))

    print(f"📦 Output directory: {args.output_dir}")
    print(f"📊 Total size: {total_size / 1024**2:.1f} MB")
    print(f"📅 Years processed: {len(summaries)}")
    print(f"📝 Total records: {sum(s['total_births'] for s in summaries):,}")
    print("\n✨ Ready for dashboard deployment!")


if __name__ == "__main__":
    main()
