"""
profiler.py

Provides functions for assigning EDA-type tags to DataFrame columns and generating
summary statistics for exploratory data analysis.

Public Functions:
- profile(df): Orchestrates tagging columns with EDA types.
- assign_column_eda_types(df): Tags each column with an `eda_type` metadata attribute.
- generate_summary(df): Produces a summary dictionary based on `eda_type`.

Private Functions:
- _is_id_column(col_series): Detects whether a column name suggests it's an ID.
"""

from .log_setup.setup import setup, logging
import pandas as pd
from pandas.core.generic import NDFrame
import pandas.api.types as pd_types
import re


logger = logging.getLogger(__name__)
setup(logger)


def assign_column_eda_types(df: pd.DataFrame) -> pd.DataFrame:
    """Assigns a custom `eda_type` attribute to each column in the DataFrame.

    EDA types help downstream processing determine how to summarize or visualize a column.
    Supported `eda_type` values include: 'unhashable', 'boolean', 'date',
    'primary id', 'foreign_id', 'category', 'numeric', 'other'.

    Args:
        df (pd.DataFrame): The DataFrame whose columns will be tagged.

    Returns:
        pd.DataFrame: The modified DataFrame with EDA types assigned as metadata.
    """
    logger.info("Assigning EDA types to columns:")
    NDFrame._metadata += ["eda_type"]
    for col_name in df.columns:
        if not all(map(pd_types.is_hashable, df[col_name])):
            df[col_name].eda_type = "unhashable"
        elif pd_types.is_bool_dtype(df[col_name]):
            df[col_name].eda_type = "boolean"
        elif pd_types.is_datetime64_any_dtype(df[col_name]):
            df[col_name].eda_type = "date"
        elif _is_id_column(df[col_name]):
            # if col_name == df.columns[0]:
            if df[col_name].nunique(dropna=True) == df.shape[0]:
                df[col_name].eda_type = "primary id"
            else:
                df[col_name].eda_type = "foreign_id"
        elif df[col_name].nunique(dropna=True) < 13:
            df[col_name].eda_type = "category"
        elif pd_types.is_numeric_dtype(df[col_name]):
            df[col_name].eda_type = "numeric"
        else:
            df[col_name].eda_type = "other"
        logger.info(f"Assigned '{df[col_name].eda_type}' to {col_name}")
    logger.info("Finished assigning EDA types")

    return df


def generate_summary(df: pd.DataFrame) -> dict:
    """Generates a summary dictionary for the DataFrame using its EDA-tagged columns.

    Args:
        df (pd.DataFrame): A DataFrame with `eda_type` metadata on each column.

    Returns:
        dict: A dictionary with column names as keys and dictionaries of summary
        statistics as values.
    """
    logger.info("Beginning generating statistical summary")

    summary = {}

    for col in df.columns:
        series = df[col]
        eda_type = getattr(series, "eda_type", "unknown")
        col_summary = {
            "eda_type": eda_type,
            "dtype": df[col].dtype.name,
        }

        if eda_type in {"unhashable"}:
            summary[col] = col_summary
            continue

        # Safe null count and distinct count
        try:
            col_summary["n_unique"] = int(series.nunique(dropna=True))
        except TypeError:
            col_summary["n_unique"] = None  # Or skip this field

        col_summary["missing"] = int(series.isna().sum())

        if eda_type == "numeric":
            col_summary["min"] = series.min()
            col_summary["max"] = series.max()
            col_summary["mean"] = series.mean()

        elif eda_type == "date":
            min_val = series.min()
            max_val = series.max()
            col_summary["min_date"] = (
                min_val.isoformat() if pd.notnull(min_val) else None
            )
            col_summary["max_date"] = (
                max_val.isoformat() if pd.notnull(max_val) else None
            )

        elif eda_type in {"boolean", "category"}:
            vc = series.apply(str).value_counts(dropna=False)
            col_summary["value_counts"] = vc.to_dict()

        summary[col] = col_summary
    logger.info("Finished generating summary")
    return summary

    # ---------------The alternative returns-----------------------
    # return json.dumps(summary, indent=4, default=str)

    # below will also list
    # unrelated metrics for each column with the
    # value of null
    # -------------------------------------------
    # return pd.DataFrame.from_dict(summary).to_json(
    #     indent=4,
    # )  # , orient="index" would reverse the outer-keys of the dict
    # --------------------------------------------------------------


def _is_id_column(col_series: pd.Series) -> bool:
    """Detects whether a column name likely refers to an ID.
    Args:
        col_series (pd.Series): The column to test.

    Returns:
        bool: True if the name looks like an ID field, else False.

    Examples:
        >>> _is_id_column(pd.Series(name='user_id'))  # True
        >>> _is_id_column(pd.Series(name='created_at'))  # False
    """
    col_name = col_series.name
    return re.search(
        r"((?:(?<=_)|^)id(?=_))|.*id$", col_name, re.IGNORECASE
    )
