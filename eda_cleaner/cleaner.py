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
    # print("\n*********Summary*********")
    # print("Final Tables:\n" + str(df.dtypes))
    return df


def standardize_column_names(df: pd.DataFrame):
    logger.info("Standardizing column names")

    # Pandas sometimes injects an index columns at the start
    # In case it is there, we remove it.
    if df.iloc[:, 0].name.startswith("Unnamed"):
        logger.info("Removing pandas index column")
        df = df.iloc[:, 1:]
        logger.info("Index column removed")

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
    try:
        no_dup_df = df.drop_duplicates(keep="first")
    except TypeError:
        logger.error(
            "Dataset contains unhashable type columns, cannot remove rows based on full row duplication."
        )
        no_dup_df = df
    logger.info("Now checking for duplicates by first column id")
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


def coerce_data_types(df: pd.DataFrame) -> pd.DataFrame:
    """
    Function that fixes column datatypes based on the following rules:
    - If a column contains only 'yes' - 'no' or 'true' - 'false' both
    case insensitive, the column will change its type to 'bool'
    - If a column contains the word 'id' in its name (regex validation),
    it will be converted to object.
    """
    logger.info("Handling data types")
    for col_name in df.columns:
        logger.info(f"Processing column {col_name}")
        col_series = df[col_name]
        df[col_name] = _coerce_series(col_series)
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


def _coerce_series(col_series: pd.Series) -> pd.Series:
    col_name = col_series.name  # Extracting column name from the series

    if _is_float_that_can_be_int(col_series):
        col_series = col_series.astype("Int64")
        logger.info(f"Changed {col_name}'s dtype to Int64")

    if _is_id_column(col_series):
        col_series = col_series.astype("string")
        logger.info(f"Changed {col_name} from numeric to string")

    elif _is_binary_string(col_series):
        col_series = _validate_binary_col(col_series)

    elif _is_numeric_binary(col_series):
        col_series = col_series.astype("boolean")
        logger.info(f"Changed {col_name}'s dtype to boolean")

    col_series = _convert_dates(col_series)
    return col_series


def _is_float_that_can_be_int(col_series: pd.Series) -> bool:
    return (
        pd_types.is_float_dtype(col_series)
        and col_series.apply(
            lambda x: pd.isna(x) or float(x).is_integer()
        ).all()
    )


def _is_binary_string(col_series: pd.Series) -> bool:
    return (
        pd_types.is_object_dtype(col_series)
        and col_series.dropna().str.lower().nunique() == 2
    )


def _is_numeric_binary(col_series: pd.Series) -> bool:
    return pd_types.is_integer_dtype(col_series) and set(
        col_series.dropna().unique()
    ).issubset({0, 1})


def _is_id_column(col_series: pd.Series) -> bool:
    col_name = col_series.name
    return pd_types.is_numeric_dtype(col_series) and re.search(
        r"((?:(?<=_)|^)id(?=_))|.*id$", col_name, re.IGNORECASE
    )


def _convert_dates(col_series: pd.Series) -> pd.Series:
    if pd_types.is_object_dtype(col_series) or pd_types.is_string_dtype(
        col_series
    ):
        converted = pd.to_datetime(
            col_series, errors="coerce", utc=True
        )
        if converted.notna().mean() > 0.8:
            logger.info(f"Converted {col_series.name} to datetime")
            return converted
    return col_series


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
    Detect boolean-like columns and convert them to columns of bool dtype, otherwise convert them to string
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
        column = column.astype("string")

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
