"""
Pipeline Step 01: Select Essential Columns.

This script creates a view or table containing only the essential columns
from optimized_sinasc_* tables. This reduces memory usage for downstream operations.

Uses SQL for efficiency - no data is loaded into Python memory.
"""

import argparse
import os
import sys

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import VARCHAR, Engine, create_engine, text

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, os.pardir))

from data.database import get_staging_db_engine

# Essential columns to keep for analysis
SELECTED_COLUMNS = [
    # Core identifiers
    "CODESTAB",
    "CODMUNNASC",
    "CODMUNRES",
    # Date/Time
    "DTNASC",
    "HORANASC",
    # Maternal characteristics
    "IDADEMAE",
    "ESTCIVMAE",
    "ESCMAE",
    "CODOCUPMAE",
    "QTDFILVIVO",
    "QTDFILMORT",
    "QTDGESTANT",
    "QTDPARTNOR",
    "QTDPARTCES",
    "RACACORMAE",
    # Pregnancy characteristics
    "GESTACAO",
    "SEMAGESTAC",
    "GRAVIDEZ",
    "PARIDADE",
    "CONSULTAS",
    "CONSPRENAT",
    "MESPRENAT",
    "TPAPRESENT",
    "STTRABPART",
    "STCESPARTO",
    "TPROBSON",
    # Delivery
    "LOCNASC",
    "PARTO",
    # Newborn characteristics
    "SEXO",
    "PESO",
    "APGAR1",
    "APGAR5",
    "RACACOR",
    "IDANOMAL",
]


SINASC_MAPPINGS = {
    "LOCNASC": {
        1: "Hospital",
        2: "Outros estabelecimentos de saúde",
        3: "Domicílio",
        4: "Outros",
        5: "Aldeia Indígena",
        9: "Ignorado",
    },
    "ESTCIVMAE": {
        1: "Solteira",
        2: "Casada",
        3: "Viúva",
        4: "Separada judicialmente/divorciada",
        5: "União estável",
        9: "Ignorada",
    },
    "ESCMAE": {
        1: "Nenhuma",
        2: "1 a 3 anos",
        3: "4 a 7 anos",
        4: "8 a 11 anos",
        5: "12 e mais",
        9: "Ignorado",
    },
    "GESTACAO": {
        1: "Menos de 22 semanas",
        2: "22 a 27 semanas",
        3: "28 a 31 semanas",
        4: "32 a 36 semanas",
        5: "37 a 41 semanas",
        6: "42 semanas e mais",
        9: "Ignorado",
    },
    "GRAVIDEZ": {1: "Única", 2: "Dupla", 3: "Tripla ou mais", 9: "Ignorado"},
    "PARTO": {1: "Vaginal", 2: "Cesário", 9: "Ignorado"},
    "CONSULTAS": {
        1: "Nenhuma",
        2: "de 1 a 3",
        3: "de 4 a 6",
        4: "7 e mais",
        9: "Ignorado",
    },
    "SEXO": {0: "Ignorado", 1: "Masculino", 2: "Feminino"},
    "RACACOR": {
        1: "Branca",
        2: "Preta",
        3: "Amarela",
        4: "Parda",
        5: "Indígena",
    },
    "IDANOMAL": {1: "Sim", 2: "Não", 9: "Ignorado"},
    "ORIGEM": {1: "Oracle", 2: "FTP", 3: "SEAD"},
    "RACACORMAE": {
        1: "Branca",
        2: "Preta",
        3: "Amarela",
        4: "Parda",
        5: "Indígena",
    },
    "TPMETESTIM": {1: "Exame físico", 2: "Outro método", 9: "Ignorado"},
    "TPAPRESENT": {
        1: "Cefálico",
        2: "Pélvica ou podálica",
        3: "Transversa",
        9: "Ignorado",
    },
    "STTRABPART": {1: "Sim", 2: "Não", 3: "Não se aplica", 9: "Ignorado"},
    "STCESPARTO": {1: "Sim", 2: "Não", 3: "Não se aplica", 9: "Ignorado"},
    "STDNEPIDEM": {0: "Não", 1: "Sim"},
    "STDNNOVA": {0: "Não", 1: "Sim"},
    "RACACOR_RN": {
        1: "Branca",
        2: "Preta",
        3: "Amarela",
        4: "Parda",
        5: "Indígena",
    },
    "RACACORN": {
        1: "Branca",
        2: "Preta",
        3: "Amarela",
        4: "Parda",
        5: "Indígena",
    },
    "ESCMAE2010": {
        0: "Sem escolaridade",
        1: "Fundamental I (1ª a 4ª série)",
        2: "Fundamental II (5ª a 8ª série)",
        3: "Médio (antigo 2º Grau)",
        4: "Superior incompleto",
        5: "Superior completo",
        9: "Ignorado",
    },
    "TPNASCASSI": {
        1: "Médico",
        2: "Enfermagem ou Obstetriz",
        3: "Parteira",
        4: "Outros",
        9: "Ignorado",
    },
    "ESCMAEAGR1": {
        0: "Sem Escolaridade",
        1: "Fundamental I Incompleto",
        2: "Fundamental I Completo",
        3: "Fundamental II Incompleto",
        4: "Fundamental II Completo",
        5: "Ensino Médio Incompleto",
        6: "Ensino Médio Completo",
        7: "Superior Incompleto",
        8: "Superior Completo",
        9: "Ignorado",
        10: "Fundamental I Incompleto ou Inespecífico",
        11: "Fundamental II Incompleto ou Inespecífico",
        12: "Ensino Médio Incompleto ou Inespecífico",
    },
    "TPFUNCRESP": {
        1: "Médico",
        2: "Enfermeiro",
        3: "Parteira",
        4: "Funcionário do cartório",
        5: "Outros",
        9: "Ignorado",
    },
    "TPDOCRESP": {1: "CNES", 2: "CRM", 3: "COREN", 4: "RG", 5: "CPF", 9: "Ignorado"},
    "PARIDADE": {0: "Nulípara", 1: "Multípara"},
    "KOTELCHUCK": {
        1: "Inadequado",
        2: "Intermediário",
        3: "Adequado",
        4: "Mais que adequado",
        9: "Não se aplica",
    },
    "TPROBSON": {
        1: "Grupo 1: Nulípara, termo, cefálico, TP espontâneo",
        2: "Grupo 2: Nulípara, termo, cefálico, TP induzido/cesárea",
        3: "Grupo 3: Multípara, s/ cesárea, termo, cefálico, TP espontâneo",
        4: "Grupo 4: Multípara, s/ cesárea, termo, cefálico, TP induzido/cesárea",
        5: "Grupo 5: Multípara, c/ cesárea, termo, cefálico",
        6: "Grupo 6: Nulípara, pélvico",
        7: "Grupo 7: Multípara, pélvico",
        8: "Grupo 8: Gestações múltiplas",
        9: "Grupo 9: Situação transversa/oblíqua",
        10: "Grupo 10: Pré-termo, cefálico",
    },
}


def create_dimension_tables():
    """
    Iterate through SINASC value mappings and create a dimension table for each.
    """
    engine = get_staging_db_engine()
    print("🚀 Starting creation of dimension tables...")
    created_count = 0

    for table_name, mappings in SINASC_MAPPINGS.items():
        if table_name not in SELECTED_COLUMNS:
            continue  # Skip non-essential columns
        dim_table_name = f"dim_{table_name.lower()}"
        print(f"  Creating table: {dim_table_name}")

        # Convert mapping dictionary to a DataFrame
        df = pd.DataFrame(list(mappings.items()), columns=["id", "name"])

        # Ensure the 'id' column is of a compatible type (integer or string)
        # We'll use string to be safe with mixed types like in 'SEXO' ('M', 'F')
        df["id"] = df["id"].astype(str)
        # Write to the database, replacing the table if it already exists
        df.to_sql(
            dim_table_name,
            con=engine,
            if_exists="replace",
            index=False,
            dtype={"id": VARCHAR, "name": VARCHAR},
        )
        created_count += 1
        created_count += 1

    print(f"\n✅ Successfully created {created_count} dimension tables.")


def get_sinasc_tables(engine: Engine) -> list[str]:
    """Get a list of all optimized SINASC tables from the database."""
    with engine.connect() as connection:
        result = connection.execute(
            text(
                "SELECT table_name FROM information_schema.tables "
                "WHERE table_schema = 'public' AND table_name LIKE 'optimized_sinasc_%' "
                "ORDER BY table_name"
            )
        )
        tables = [row[0] for row in result]
    print(f"Found {len(tables)} SINASC tables: {tables}")
    return tables


def create_selected_table(engine: Engine, source_table: str, dest_table: str):
    """
    Create a new table with only essential columns using SQL.

    Args:
        engine: SQLAlchemy engine connected to the staging database.
        source_table: Name of the optimized SINASC table.
        dest_table: Name of the destination table with selected columns.
    """
    print(f"  Creating {dest_table} from {source_table}...")

    # Build the column list for the SELECT statement with proper quoting for case-sensitive names
    columns_str = ", ".join([f'"{col}"' for col in SELECTED_COLUMNS])

    sql = f"""
    CREATE TABLE {dest_table} AS
    SELECT {columns_str}
    FROM {source_table};
    """

    try:
        with engine.connect() as connection:
            tx = connection.begin()
            # Drop the destination table if it exists
            connection.execute(text(f"DROP TABLE IF EXISTS {dest_table};"))
            # Create the new table
            connection.execute(text(sql))
            tx.commit()

        # Get row count
        with engine.connect() as connection:
            result = connection.execute(text(f"SELECT COUNT(*) FROM {dest_table};"))
            count = result.scalar()

        print(f"  ✅ Successfully created {dest_table} with {count:,} records.")
    except Exception as e:
        print(f"  ❌ FAILED to create {dest_table}. Error: {e}")
        raise


def main():
    """Main execution function."""
    load_dotenv()
    parser = argparse.ArgumentParser(description="Select essential columns from optimized SINASC tables.")
    parser.add_argument(
        "--db_url",
        default=os.getenv("STAGING_DATABASE_URL"),
        help="Database connection URL for the staging environment.",
    )
    args = parser.parse_args()

    if not args.db_url:
        raise ValueError("Database URL not provided. Set STAGING_DATABASE_URL in .env or pass --db_url.")

    print("🚀 Starting column selection pipeline...")
    engine = create_engine(args.db_url)

    sinasc_tables = get_sinasc_tables(engine)
    if not sinasc_tables:
        print("❌ No `optimized_sinasc_*` tables found. Aborting.")
        return

    for table in sinasc_tables:
        # Extract year from table name (e.g., optimized_sinasc_2024 -> 2024)
        year = table.replace("optimized_sinasc_", "")
        dest_table = f"selected_sinasc_{year}"
        create_selected_table(engine, table, dest_table)

    print("\n🚀 Creating dimension tables for selected categorical columns...")

    create_dimension_tables()

    print("\n✨ Column selection process finished successfully!")


if __name__ == "__main__":
    main()
