import psycopg2
from logging_setup import logging_setup, logging
from argparse import ArgumentParser
from urllib.parse import urlparse
import pandas as pd

logger = logging.getLogger(__name__)
logging_setup(logger)
# logger.info("hi")
# logger.debug("not hi")

# set up argument parsing
parser = ArgumentParser()
parser.add_argument("path", nargs="?")
parser.add_argument("-d", "--db_connection", action="store_true")
parser.add_argument("-c", "--csv_path", action="store_true")
args = parser.parse_args()
# logger.info(args)


def pg_connect_n_load(uri):
    # if db_name := get_db_name(uri):
    #     logger.info(f"Connecting to database {db_name}")
    # else:
    #     logger.info(f'Invalid URI')
    # Sample URI (you can replace this with your actual connection string)
    # uri = "postgresql://postgres:Password21!!!@localhost:5432/pagila"

    try:
        # Parse the URI
        parsed_uri = urlparse(uri)
        # Extract the components
        username = parsed_uri.username
        password = parsed_uri.password
        host = parsed_uri.hostname
        port = parsed_uri.port
        database = parsed_uri.path[1:]  # Remove leading slash
        logger.info(f'Connecting to {database}')
    except Exception as e:
        logger.error("Error: " + str(e))

    # Connect to PostgreSQL
    try:
        connection = psycopg2.connect(
            dbname=database,
            user=username,
            password=password,
            host=host,
            port=port,
        )
        logger.info("Connection established!")

        # Example query
        # cursor = connection.cursor()
        # cursor.execute("SELECT version();")
        # cursor.execute(
        #     """
        #     Select *
        #     from payment

        #     """
        # )
        # result = cursor.fetchmany(10)
        # logger.info('Query results:')
        # for line in result:
        #     print(line)
        # logger.info('End of results')
        logger.info(f'Disconnecting from {database}')
        cursor.close()
        connection.close()
    except Exception as e:
        logger.error(f"Error: {e}")


def csv_load(csv_file):
    logger.info(f"Loading {csv_file}")
    try:
        df = pd.read_csv(csv_file)
        print(df.head())
    except Exception as e:
        logger.error(e)


# def get_db_name(uri):
#     return re.search(r'(?<=/)\w+$', uri).group()

if args.db_connection and args.path:
    df = pg_connect_n_load(args.path)
elif args.csv_path and args.path:
    df = csv_load(args.path)
else:
    logger.warning("Invalid parameters, loading default dataset")
    df = csv_load("data/KaggleV2-May-2016.csv")
