"""
utility.py

printing functions for dataframe and EDA types
"""

from tabulate import tabulate
import pandas as pd


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
        f"{col}\n({str(dtype)})" for col, dtype in sample.dtypes.items()
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
