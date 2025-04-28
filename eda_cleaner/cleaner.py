import pandas as pd
from .log_setup.setup import setup, logging

logger = logging.getLogger(__name__)
setup(logger)


def clean_pipeline(df):
    df = standardize_column_names(df)
    df = remove_duplicates(df)
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
    # removing rows that match completely
    df = df.drop_duplicates(keep="first")
    # removing rows whose first column contains 'id' and have the same
    # value in that column
    if "id" in df.columns[0]:
        df = df.drop_duplicates(keep="first", subset=[df.columns[0]])
    return df


def handle_missing_values(df):
    pass
