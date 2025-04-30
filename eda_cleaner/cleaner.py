import pandas as pd
from .log_setup.setup import setup, logging
import re
import pandas.api.types as pd_types
import numpy as np

logger = logging.getLogger(__name__)
setup(logger)


def clean_pipeline(df):
    """
    orchestration for all the cleaning procedures
    """
    df = standardize_column_names(df)
    df = remove_duplicates(df)
    df = coerce_data_types(df)
    df = handle_missing_values(df)
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
    logger.info(f'\nInitial dataframe dtypes:\n{df.dtypes}')
    for column in df.columns:
        logger.info(f'processing column {column}')
        # logger.info(f"{df[column].name} is {df[column].dtype} before conv")
        # First convert Float columns to int if they can be converted
        if (
            pd_types.is_float_dtype(df[column])
            and df[column]
            .apply(
                lambda x: (
                    True
                    if (float.is_integer(x) or np.isnan(x))
                    else False
                )
            )
            .all()
        ):
            df[column] = df[column].astype("Int64")
            logger.info(f"Changed {column}'s dtype to int64")
        # pass size-2 object columns to validate_binary_col in order
        # to convert them to bool if they are eligible or categorical
        if (
            pd_types.is_object_dtype(df[column])
            and df[column].dropna().str.lower().unique().size == 2
        ):
            validated_column = _validate_binary_col(df[column])
            df[column] = validated_column
        # This checks for numeric style bools and converts
        # to boolean if eligible  (1, 0)
        elif pd_types.is_integer_dtype(df[column]) and all(
            x in (0, 1) for x in df[column].dropna()
        ):
            df[column] = df[column].astype("boolean")
            logger.info(f"Changed {column}'s dtype to boolean")
        # this one will look for a numeric 'id' column
        # and convert its values to strings
        elif (
            pd_types.is_integer_dtype(df[column])
            and re.search(
                r"((?:(?<=_)|^)id(?=_))|.*id$", df[column].name
            )
            and set(df[column]) == set(df[column].unique())
        ):
            df[column] = df[column].astype("string")
            logger.info(
                f"Changed {df[column].name} from numeric, to string"
            )
        # convert all other columns that have less than eight
        # values into a category type
        # elif df[column].dropna().unique().size < 8:
        #     if pd_types.is_integer_dtype(df[column]):
        #         df[column] = df[column].astype('string')
        #     elif pd_types.is_object_dtype(df[column]):
        #         df[column] = df[column].astype('string')
    logger.info(f'\nFinal dataframe dtypes:\n{df.dtypes}')
    logger.info("Finished handling data types")
    return df


def handle_missing_values(df: pd.DataFrame, drop_thres=0.5):
    logger.info("Handling missing Values")
    for column in df.columns:
        missing_values_prc = df[column].isnull().mean() * 100
        logger.info(
            f"{df[column].name} column has {round(missing_values_prc)}% of its values missing"
        )
        if missing_values_prc == 0:
            continue
        elif missing_values_prc >= 50:
            logger.info(f"Dropping column {df[column].name}")
            df = df.drop(column, axis=1)
        else:
            logger.info("Beginning Imputation")
            df[column] = _impute(df[column])
        logger.info("Moving on")
    logger.info("Finished Handling Missing Values")
    return df


def _impute(column: pd.Series, nmode="median") -> pd.Series:
    """
    Using nmode to impute the values of the provided column
    In case of invalid input the default nmode will be used,
    """
    if pd_types.is_numeric_dtype(column):
        if nmode == "median":
            logger.info("Performing imputation with 'median'")
            column = column.fillna(column.median())
        elif nmode == "mean":
            logger.info("Performing imputation with 'mean'")
            column = column.fillna(column.mean())
        else:
            default_nmode = _impute.__defaults__[0]
            logger.info(f"Performing imputation with '{default_nmode}'")
            func = getattr(pd.Series, default_nmode)
            column = column.fillna(func(column))
    elif pd_types.is_bool_dtype or isinstance(
        column, pd.CategoricalDtype
    ):
        column = column.fillna(column.mode())
    return column


def _validate_binary_col(column: pd.Series):
    """
    Detect boolean-like columns and convert them to columns of bool dtype, otherwise convert them to category
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
    else:
        column = column.astype("category")

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
