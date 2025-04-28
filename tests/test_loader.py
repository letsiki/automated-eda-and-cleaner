import pytest
import pandas as pd
from eda_cleaner.loader import pg_load, csv_load


@pytest.mark.xfail(
    reason="""
    This is only meant to be tested locally. You may create a PG database adhering to the URI below and remove this mark: postgresql://postgres:Password21!!!@localhost:5432/pagila
    """
)
@pytest.mark.parametrize(
    "uri, table_name, expected",
    [
        (
            "postgresql://postgres:Password21!!!@localhost:5432/pagila",
            "payment",
            pd.DataFrame,
        ),
        (
            "postgresql://postgres:Password21!!!@localhost:5432/pagila",
            "paymentssss",
            type(None),
        ),
        (
            "postgresql://postgres:Plocalhost:5432/pagila",
            "payment",
            type(None),
        ),
    ],
)
def test_pg_load(uri, table_name, expected):
    """
    assumes an online pg database
    - Test that valid URI's are correctly loaded into the dataframe
    - Test that invalid URI or table names are successfully returning None
    """
    assert type(pg_load(uri, table_name)) == expected


@pytest.mark.parametrize(
    "csv_file, expected",
    [
        (
            "data/global air pollution dataset.csv",
            pd.DataFrame,
        ),
        (
            "data/KaggleV2-May-2016.csv",
            pd.DataFrame,
        ),
        (
            "non-existent.csv",
            type(None),
        ),
    ],
)
def test_csv_load(csv_file, expected):
    """
    - Test that valid csv paths are correctly loaded into the dataframe
    - Test that invalid csv_paths are successfully returning None
    """
    assert type(csv_load(csv_file)) == expected
