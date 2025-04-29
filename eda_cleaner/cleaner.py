import pandas as pd
from .log_setup.setup import setup, logging
import re
import pandas.api.types as pd_types

logger = logging.getLogger(__name__)
setup(logger)


def clean_pipeline(df):
    """
    orchestration for all the cleaning procedures
    """
    df = standardize_column_names(df)
    df = remove_duplicates(df)
    df = coerce_data_types(df)
    # df = handle_missing_values(df)
    print("\n*********Summary*********")
    print("Final Tables:\n" + str(df.dtypes))
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
    if match := re.search(
        r"((?:(?<=_)|^)id(?=_))|.*id$", no_dup_df.columns[0]
    ):
        logger.debug(no_dup_df.columns[0])
        logger.debug(match.group() if match else match)
        no_dup_df = no_dup_df.drop_duplicates(
            keep="first", subset=[no_dup_df.columns[0]]
        )
    logger.info(f"{df.shape[0] - no_dup_df.shape[0]} rows removed")
    logger.info(f"{no_dup_df.shape[0]} rows remaining.")
    logger.info(f"Finished removing duplicate rows")
    return no_dup_df


def coerce_data_types(df: pd.DataFrame):
    """
    Function that fixes column datatypes based on the following rules:
    - If a column contains only 'yes' - 'no' or 'true' - 'false' both
    case insensitive, the column will change its type to 'bool'
    - If a column contains the word 'id' in its name (regex validation),
    it will be converted to object.
    """
    logger.info("Handling data types")
    for column in df.columns:
        # pass object columns to validate_bool_col in order to convert
        # them to bool if they are eligible
        if pd_types.is_object_dtype(df[column]):
            validated_column = _validate_bool_col(df[column])
            df[column] = validated_column
        elif (
            # This checks for numeric style bools and converts
            # to boolean if eligible  (1, 0)
            pd_types.is_numeric_dtype(df[column])
            and df[column].dropna().unique().size == 2
        ):
            df[column] = (
                df[column]
                .replace({0: False, 1: True})
                .astype("boolean")
            )
            logger.info(f"Changed {column}'s dtype to boolean")
        elif (
            # this one will look for a numeric 'id' column
            # and convert its values to strings
            pd_types.is_numeric_dtype(df[column])
            and re.search(
                r"((?:(?<=_)|^)id(?=_))|.*id$", df[column].name
            )
            and set(df[column]) == set(df[column].unique())
        ):
            df[column] = df[column].astype("str")
            logger.info(
                f"Changed {df[column].name} from numeric, to string"
            )
        logger.info("Finished handling data types")

    return df


def handle_missing_values(df):
    pass


def _validate_bool_col(column: pd.Series):
    """
    Detect boolean-like columns and convert them to columns of bool dtype
    """
    # Check if all non-null rows are 'true' or 'false'
    if all(
        map(
            lambda x: (
                True
                if not x or x.lower() in ("true", "false")
                else False
            ),
            column,
        )
    ):
        # if they are convert them to boolean
        column = column.map(_true_false_to_bool).astype("boolean")
        logger.info(f"Changed {column.name}'s dtype to boolean")
    # Check if all non-null rows are 'yes' or 'no'
    elif all(
        map(
            lambda x: (
                True if not x or x.lower() in ("yes", "no") else False
            ),
            column,
        )
    ):
        # if they are convert them to boolean
        column = column.map(_yes_no_to_bool).astype("boolean")
        logger.info(f"Changed {column.name}'s dtype to boolean")

    return column


def _yes_no_to_bool(x):
    "Converts a value to True if it is 'yes', False otherwise"
    if x is None:
        return pd.NA
    else:
        func = lambda x: True if x.lower() == "yes" else False
        return func(x)


def _true_false_to_bool(x):
    "Converts a value to True if it is 'true', False otherwise"
    if x is None:
        return pd.NA
    else:
        func = lambda x: True if x.lower() == "true" else False
        return func(x)
