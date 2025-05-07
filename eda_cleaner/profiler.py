"""
profiler.py

Provides a function for generating summary statistics for exploratory
data analysis.

Public Functions:
- generate_summary(df): Produces a summary dictionary based on the data type.
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
    print("*" * 90)
    logger.info("Beginning generating statistical summary")

    summary = {}

    summary["_dataset_"] = {}
    df_summary = summary["_dataset_"]
    df_summary.update(
        rows=df.shape[0],
        columns=df.shape[1],
        total_nr_of_cells=df.size,
        total_missing_values=df.isna().sum().sum(),
        column_names=[col for col in df.columns],
        dtypes=[dtype.name for dtype in df.dtypes],
        memory_usage=str(round(df.memory_usage().sum() / 10**6, 2))
        + " MB's",
    )

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
            col_summary["mean"] = round(series.mean(), 4)

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
