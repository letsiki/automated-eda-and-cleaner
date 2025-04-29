import pandas as pd
from .log_setup.setup import setup, logging
import re

logger = logging.getLogger(__name__)
setup(logger)


def clean_pipeline(df):
    df = standardize_column_names(df)
    df = remove_duplicates(df)
    df = coerce_data_types(df)
    # df = handle_missing_values(df)
    return df


def standardize_column_names(df):
    logger.info("Standardizing column names")
    columns_nr = df.shape[1]
    logger.info(f"Found {columns_nr} columns")
    logger.info(
        "replacing whitespaces with '_', lowering case, and removing invalid characters"
    )
    logger.info(f"Columns before operation {df.columns.to_list()}")
    df.columns = (
        df.columns.str.strip()
        .str.lower()
        .str.replace(r"[ -]", "_", regex=True)
        .str.replace(r"[^\w]", "", regex=True)
    )
    logger.info(f"Columns after operation {df.columns.to_list()}")
    logger.info("Finished standardizing columns")
    return df


def remove_duplicates(df):
    """
    Function that removes duplicate rows, but also removes a row if
    both of the following conditions apply:
    1) Column 1 contains the word 'id' in its name (regex validation)
    2) Column 1 has duplicate values
    In any case we are removing duplicates with the 'keep-first' strategy
    """
    logger.info("Removing duplicate rows")
    logger.info(f"{df.shape[0]} rows before operation")
    logger.info("Removing...")
    no_dup_df = df.drop_duplicates(keep="first")
    if match := re.search(r"(?:(?<=_)|^)id(?:(?=_)|$)", no_dup_df.columns[0]):
        logger.debug(no_dup_df.columns[0])
        logger.debug(match.group() if match else match)
        no_dup_df = no_dup_df.drop_duplicates(
            keep="first", subset=[no_dup_df.columns[0]]
        )
    logger.info(f"{df.shape[0] - no_dup_df.shape[0]} rows removed")
    logger.info(f"{no_dup_df.shape[0]} rows remaining.")

    return no_dup_df


def coerce_data_types(df):
    """
    Function that fixes column datatypes based on the following rules:
    - If a column contains only 'yes' - 'no' or 'true' - 'false' both
    case insensitive, the column will change its type to 'bool'
    - If a column contains the word 'id' in its name (regex validation),
    it will be converted to object.
    """


def handle_missing_values(df):
    pass
