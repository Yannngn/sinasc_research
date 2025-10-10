"""
Database connection management for the SINASC dashboard.

Provides SQLAlchemy engine instances for connecting to the staging and
production PostgreSQL databases.
"""

import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, ".env"))

# Load URLs from environment variables
STAGING_DB_URL = os.getenv("STAGING_DATABASE_URL")
PROD_DB_URL = os.getenv("POSTGRES_INTERNAL_DATABASE_URL")
LOCAL_DB_URL = os.getenv("PROD_LOCAL_DATABASE_URL")

# Create singleton engine instances
_staging_engine = None
_prod_engine = None
_local_engine = None

if STAGING_DB_URL:
    _staging_engine = create_engine(STAGING_DB_URL)

if PROD_DB_URL:
    _prod_engine = create_engine(PROD_DB_URL)

if LOCAL_DB_URL:
    _local_engine = create_engine(LOCAL_DB_URL)


def get_staging_db_engine() -> Engine:
    """
    Returns the SQLAlchemy engine for the staging database.

    Raises:
        ValueError: If the STAGING_DATABASE_URL is not set.

    Returns:
        SQLAlchemy Engine for the staging database.
    """
    if _staging_engine is None:
        raise ValueError("STAGING_DATABASE_URL environment variable is not set.")
    return _staging_engine


def get_local_db_engine() -> Engine:
    """
    Returns the SQLAlchemy engine for the local production database.

    Raises:
        ValueError: If the PROD_LOCAL_DATABASE_URL is not set.
    """
    if _local_engine is None:
        raise ValueError("PROD_LOCAL_DATABASE_URL environment variable is not set.")
    return _local_engine


def get_prod_db_engine() -> Engine:
    """
    Returns the SQLAlchemy engine for the production database.

    Raises:
        ValueError: If the PRODUCTION_DATABASE_URL is not set.

    Returns:
        SQLAlchemy Engine for the production database.
    """
    if _prod_engine is None:
        raise ValueError("POSTGRES_INTERNAL_DATABASE_URL environment variable is not set.")
    return _prod_engine
