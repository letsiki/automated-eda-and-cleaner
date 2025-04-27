from sqlalchemy import create_engine
from .log_setup.setup import setup, logging
import pandas as pd

logger = logging.getLogger(__name__)
setup(logger)


def pg_load(uri):
    try:
        logger.info("Connecting to database")
        engine = create_engine(uri)
        logger.info("Connected!")
        table_name = ""
        while not table_name:
            table_name = input("Enter a valid table name: ")
        logger.info(f"Retrieving table '{table_name}'")
        with engine.connect() as conn, conn.begin():
            df = pd.read_sql_table(table_name, conn)
    except Exception as e:
        logger.error(e)
        logger.info(_help_redirection)
        return None
    return df


def csv_load(csv_file):
    logger.info(f"Loading {csv_file}")
    try:
        df = pd.read_csv(csv_file)
        return df
    except Exception as e:
        logger.error(e)
        logger.info(_help_redirection)
        return None


_help_redirection = (
    "To get help with this command type python cli.py --help"
)
