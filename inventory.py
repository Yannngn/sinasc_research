"""
Connects to the staging database and lists all available tables.
"""

import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect


def run_inventory():
    """Connects to the DB and lists all tables."""
    load_dotenv()
    db_url = os.getenv("STAGING_DATABASE_URL")

    if not db_url:
        print("❌ STAGING_DATABASE_URL not found in .env file.")
        return

    print(f"Connecting to database: {db_url.split('@')[-1]}")
    try:
        engine = create_engine(db_url)
        inspector = inspect(engine)
        tables = inspector.get_table_names()

        if not tables:
            print("No tables found in the database.")
            return

        print("\n--- Database Table Inventory ---")
        for table in sorted(tables):
            print(f"- {table}")
        print("------------------------------")

    except Exception as e:
        print(f"❌ Failed to connect or inspect the database. Error: {e}")


if __name__ == "__main__":
    run_inventory()
