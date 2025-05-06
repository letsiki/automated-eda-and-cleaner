"""
cli.py

Command-line interface for the eda_cleaner package. This tool loads a tabular dataset,
cleans it, performs automated exploratory data analysis (EDA), and outputs summary reports
and visualizations.

Usage options:
    1) Load from a PostgreSQL database:
       python -m eda_cleaner.cli -d 'postgresql://user:password@host:port/dbname'

    2) Load from a CSV file:
       python -m eda_cleaner.cli -c path/to/file.csv

    3) Load a default dataset:
       python -m eda_cleaner.cli
       (then respond with 'y' when prompted)

Arguments:
    path                A connection string (for -d) or file path (for -c)
    -d, --db_connection Indicates the path argument is a PostgreSQL URI
    -c, --csv_path      Indicates the path argument is a CSV file path

Outputs:
    - Cleaned dataset written to 'output/cleaned_data.csv'
    - EDA summary table written to 'output/summary_table.csv'
    - JSON summary written to 'output/summary.json'
    - Visualizations saved in the 'output/plots/' directory
"""

from argparse import ArgumentParser
from .log_setup.setup import setup, logging
from .loader import pg_load, csv_load
from .cleaner import clean_pipeline
from .profiler import generate_summary
from .writer import write_json, write_summary_table, write_df
from .visualizer import generate_plots

DEFAULT_DATASET = "data/global-air-pollution-dataset.csv"

logger = logging.getLogger(__name__)
setup(logger)

# set up argument parsing
parser = ArgumentParser()
parser.add_argument("path", nargs="?")
parser.add_argument("-d", "--db_connection", action="store_true")
parser.add_argument("-c", "--csv_path", action="store_true")
args = parser.parse_args()


def main():
    """
    Main entry point for the CLI.

    Based on parsed command-line arguments, this function:
    - Loads a dataset from PostgreSQL, CSV, or default file
    - Cleans the data via the cleaning pipeline
    - Assigns EDA types to each column
    - Writes the cleaned dataset and EDA results to disk
    - Generates and saves summary statistics and plots

    If no valid data source is provided, prompts the user
    to optionally load the default dataset.
    """
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

    df = clean_pipeline(df)
    summary = generate_summary(df)
    write_json(summary)
    write_summary_table(summary)
    generate_plots(df)
    write_df(df)


if __name__ == "__main__":
    main()
