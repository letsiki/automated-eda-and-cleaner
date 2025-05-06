"""
utility.py

printing functions for dataframe and EDA types
"""

from tabulate import tabulate
import pandas as pd
from pandas.core.generic import NDFrame


def df_print(df: pd.DataFrame) -> None:
    # Sample N rows
    try:
        sample = (
            df.iloc[:, :7]
            .sample(n=5, random_state=1)
            .reset_index(drop=True)
        )
    except ValueError:
        sample = df
    # Construct headers with dtype shown below each column name
    headers = [
        f"{col}\n({dtype.name})" for col, dtype in sample.dtypes.items()
    ]

    # Print using tabulate
    print(
        tabulate(
            sample,
            headers=headers,
            tablefmt="psql",
            showindex=False,
        )
    )


def print_eda_types(df: pd.DataFrame) -> None:
    for col_name, col_series in df.items():
        if eda_type := getattr(col_series, "eda_type", None):
            print(f"column {col_name}, has eda type of {eda_type}")


def repatch_eda_type(
    old_df: pd.DataFrame, new_df: pd.DataFrame
) -> None:
    NDFrame._metadata += ["eda_type"]
    try:
        new_df.eda_type = old_df.eda_type
    except KeyError:
        print("Unsuccessful assignment of EDA type")
        raise


def load_csv_with_nullable_types(filepath, **kwargs):
    df = pd.read_csv(filepath, **kwargs)
    nullable_df = pd.DataFrame()

    for col in df.columns:
        series = df[col]
        non_null_series = series.dropna()

        if non_null_series.empty:
            # default to object if there's nothing to infer
            nullable_df[col] = series.astype("object")
            continue

        inferred_dtype = pd.api.types.infer_dtype(non_null_series, skipna=True)

        # Map inferred dtype to a pandas nullable type
        if inferred_dtype in {"integer"}:
            nullable_df[col] = series.astype("Int64")
        elif inferred_dtype in {"floating"}:
            try:
                nullable_df[col] = series.astype("Int64")
            except:
                nullable_df[col] = series.astype("Float64")
        elif inferred_dtype in {"boolean"}:
            nullable_df[col] = series.astype("boolean")
        elif inferred_dtype in {"string", "unicode", "datetime"}:
            try:
                nullable_df[col] = pd.to_datetime(nullable_df)
            except:    
                nullable_df[col] = series.astype("string")
        else:
            nullable_df[col] = series.astype("object")

    return nullable_df


def load_dict_with_nullable_types(dic, **kwargs):
    df = pd.DataFrame(dic)
    nullable_df = pd.DataFrame()

    for col in df.columns:
        series = df[col]
        non_null_series = series.dropna()

        if non_null_series.empty:
            # default to object if there's nothing to infer
            nullable_df[col] = series.astype("object")
            continue

        inferred_dtype = pd.api.types.infer_dtype(non_null_series, skipna=True)

        # Map inferred dtype to a pandas nullable type
        if inferred_dtype in {"integer"}:
            nullable_df[col] = series.astype("Int64")
        elif inferred_dtype in {"floating"}:
            try:
                nullable_df[col] = series.astype("Int64")
            except:
                nullable_df[col] = series.astype("Float64")
        elif inferred_dtype in {"boolean"}:
            nullable_df[col] = series.astype("boolean")
        elif inferred_dtype in {"string", "unicode", "datetime"}:
            try:
                nullable_df[col] = pd.to_datetime(nullable_df)
            except:    
                nullable_df[col] = series.astype("string")
        else:
            nullable_df[col] = series.astype("object")

    return nullable_df