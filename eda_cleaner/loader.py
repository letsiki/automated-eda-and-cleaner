"""
loader.py

This module provides utility functions to load datasets into pandas DataFrames
from either PostgreSQL databases or CSV files. It uses SQLAlchemy for database
connectivity and includes logging for tracing and error diagnostics.

Functions:
    - pg_load(uri, table_name=None): Load a PostgreSQL table into a DataFrame.
    - csv_load(csv_file): Load a CSV file into a DataFrame.
"""

from sqlalchemy import create_engine
from .log_setup.setup import setup, logging
import pandas as pd

logger = logging.getLogger(__name__)
setup(logger)


def pg_load(uri: str, table_name: str = None) -> pd.DataFrame:
    """
    Connects to a PostgreSQL database using the given SQLAlchemy URI and loads a table into a DataFrame.

    If `table_name` is not provided, the user will be prompted to enter it interactively.
    Returns `None` if the connection fails or the table cannot be retrieved.

    Parameters:
        uri (str): SQLAlchemy-compatible PostgreSQL URI (e.g., 'postgresql://user:pass@host:port/dbname').
        table_name (str, optional): Name of the table to load. If None, prompts the user.

    Returns:
        pd.DataFrame or None: A DataFrame containing the table's data, or None if loading failed.
    """
    try:
        logger.info("Connecting to database")
        engine = create_engine(uri)
        logger.info("Connected!")
        if not table_name:
            while not table_name:
                table_name = input("Enter a valid table name: ")
        logger.info(f"Retrieving table '{table_name}'")
        with engine.connect() as conn, conn.begin():
            df = pd.read_sql_table(table_name, conn)
    except Exception as e:
        logger.error(e)
        return None
    return df


def csv_load(csv_file: str) -> pd.DataFrame:
    """
    Loads a CSV file into a pandas DataFrame.

    Parameters:
        csv_file (str or Path): Path to the CSV file.

    Returns:
        pd.DataFrame or None: A DataFrame containing the CSV data, or None if reading failed.
    """
    logger.info(f"Loading {csv_file}")
    try:
        df = pd.read_csv(csv_file)
        return df
    except Exception as e:
        logger.error(e)
        return None
