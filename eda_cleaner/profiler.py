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


logger = logging.getLogger(__name__)
setup(logger)


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

        col_summary = {
            "dtype": df[col].dtype.name,
        }

        if df[col].dtype.name in {"object"}:
            summary[col] = col_summary
            continue

        # Safe null count and distinct count
        try:
            col_summary["n_unique"] = int(series.nunique(dropna=True))
        except TypeError:
            col_summary["n_unique"] = None  # Or skip this field

        col_summary["missing"] = int(series.isna().sum())

        if pd_types.is_numeric_dtype(series):
            col_summary["min"] = series.min()
            col_summary["max"] = series.max()
            col_summary["mean"] = series.mean()

        elif pd_types.is_datetime64_any_dtype(series):
            min_val = series.min()
            max_val = series.max()
            col_summary["min_date"] = (
                min_val.isoformat() if pd.notnull(min_val) else None
            )
            col_summary["max_date"] = (
                max_val.isoformat() if pd.notnull(max_val) else None
            )

        elif series.dtype.name in {"boolean", "category"}:
            vc = series.apply(str).value_counts(dropna=False)
            col_summary["value_counts"] = vc.to_dict()

        summary[col] = col_summary
    logger.info("Finished generating summary")
    return summary
