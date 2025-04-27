from logging_setup import logging_setup, logging
from argparse import ArgumentParser
import pandas as pd
from sqlalchemy import create_engine, text

logger = logging.getLogger(__name__)
logging_setup(logger)

# set up argument parsing
parser = ArgumentParser()
parser.add_argument("path", nargs="?")
parser.add_argument("-d", "--db_connection", action="store_true")
parser.add_argument("-c", "--csv_path", action="store_true")
args = parser.parse_args()
# logger.info(args)


def pg_connect_n_load(uri):
    engine = create_engine(uri)
    with engine.connect() as conn, conn.begin():
        df = pd.read_sql_table("payment", conn)
    return df


def csv_load(csv_file):
    logger.info(f"Loading {csv_file}")
    try:
        df = pd.read_csv(csv_file)
        print(df.head())
    except Exception as e:
        logger.error(e)


if args.db_connection and args.path:
    df = pg_connect_n_load(args.path)
elif args.csv_path and args.path:
    df = csv_load(args.path)
else:
    logger.warning("Invalid parameters, loading default dataset")
    df = csv_load("data/KaggleV2-May-2016.csv")

print(df.head())
