from .log_setup.setup import setup, logging
import pandas as pd
import numpy as np
from pandas.core.generic import NDFrame
import pandas.api.types as pd_types
import re


logger = logging.getLogger(__name__)
setup(logger)
logger.handlers[0].setLevel(logging.INFO)


def profile(df):
    assign_column_eda_types(df)
    return df


def assign_column_eda_types(df: pd.DataFrame):
    """
    function that will assign an EDA type to each column, via monkey
    patching, that will profiling to determine the appropriate analysis
    method for each column
    """
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

    logger.debug([col_series.eda_type for _, col_series in df.items()])
    return df


def generate_summary(df: pd.DataFrame):
    """
    Generate a summary dictionary with basic profiling stats for each column
    based on its `eda_type` attribute.

    Parameters:
        df (pd.DataFrame): A DataFrame with `eda_type` metadata on its columns.

    Returns:
        dict: A dictionary where each key is a column name and each value is
              a sub-dictionary of relevant summary statistics.
    """
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
    col_name = col_series.name
    return re.search(
        r"((?:(?<=_)|^)id(?=_))|.*id$", col_name, re.IGNORECASE
    )
