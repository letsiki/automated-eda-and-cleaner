import pandas as pd
from .log_setup.setup import setup, logging

logger = logging.getLogger(__name__)
setup(logger)


def clean_pipeline(df):
    df = standardize_column_names(df)
    df = remove_duplicates(df)
    df = handle_missing_values(df)
    return df


def standardize_column_names(df):
    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"Received {df} expect a pandas DataFrame")
    print(df.head())
    print(f"dataset contains {df.isna().sum().sum()} null cells")
    df.info()
    print(df["No-show"].sample(10))
    df["No-show"] = df["No-show"].map({"Yes": True, "No": False})
    print(df["No-show"].sample(10))


def remove_duplicates(df):
    pass


def handle_missing_values(df):
    pass
