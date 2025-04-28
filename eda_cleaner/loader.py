from sqlalchemy import create_engine
from .log_setup.setup import setup, logging
import pandas as pd

logger = logging.getLogger(__name__)
setup(logger)


def pg_load(uri, table_name=None):
    """
    Function that establishes connection to a pg database
    using a provided URI, an if successful, either uses 
    provided table name, or prompts the user for one, and 
    loads it into a pandas DataFrame. 
    Returns None, if unsuccessful.
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


def csv_load(csv_file):
    logger.info(f"Loading {csv_file}")
    try:
        df = pd.read_csv(csv_file)
        return df
    except Exception as e:
        logger.error(e)
        return None
