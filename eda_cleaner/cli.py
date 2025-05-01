description = """
    CLI tool that loads tabular data, cleans it, and performs EDA automatically. 
    You can either load a Postgres db, a csv file, or the default dataset:
    1) For Postgres -> 
    python -m eda_cleaner.cli -d 'postgresql://postgres:Password@localhost:5432/db_name 
    2) For CSV -> python -m eda_cleaner.cli -c csv_file.csv
    3) For default -> python -m eda_cleaner.cli and then type 'y'
"""

from argparse import ArgumentParser
from .log_setup.setup import setup, logging
from .loader import pg_load, csv_load
from .cleaner import clean_pipeline
from .profiler import assign_column_eda_types, generate_summary
from .utility import df_print
import json


_URI = "postgresql://postgres:Password21!!!@localhost:5432/pagila"
DEFAULT_DATASET = "data/medical_non_show.csv"

logger = logging.getLogger(__name__)
setup(logger)

# set up argument parsing
parser = ArgumentParser(description=description)
parser.add_argument("path", nargs="?")
parser.add_argument("-d", "--db_connection", action="store_true")
parser.add_argument("-c", "--csv_path", action="store_true")
args = parser.parse_args()

# we now have two documentation sources, cli.py --help, from the
# terminal, and help(cli) from the python console. With the following
# line we are making both the same
__doc__ = parser.format_help()


def main():
    # read arguments, invoke appropriate functions
    # argparse injects a help arguments and populates with some
    # metadata and also passes it the description we provided
    # to the argparse constructor.
    df = None
    if args.db_connection and not args.csv_path and args.path:
        df = pg_load(args.path)
    elif args.csv_path and not args.db_connection and args.path:
        df = csv_load(args.path)
    else:
        logger.warning("Invalid parameters.")
        parser.print_help()
        while True:
            choice = input(
                "Do you wish to load a default dataset? (y or n): "
            )
            if choice.lower() == "y":
                df = csv_load(DEFAULT_DATASET)
                break
            if choice.lower() == "n":
                break

    if df is None:
        logger.info("No data loaded, exiting")
        return

    # print(df.sample(n=5).to_string(index=False))
    # Cleaning
    df_print(df)
    df = clean_pipeline(df)
    df = assign_column_eda_types(df)
    df_print(df)
    summary = generate_summary(df)
    # print(json.dumps(summary, indent=2, default=str))
    # print(df.sample(n=5).to_string(index=False))
    print(summary)

if __name__ == "__main__":
    main()


    
