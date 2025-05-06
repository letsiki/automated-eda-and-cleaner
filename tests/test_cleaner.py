import pytest
import pandas as pd
import numpy as np
from eda_cleaner.cleaner import (
    standardize_column_names,
    handle_missing_values,
    remove_duplicates,
    coerce_nullable_data_types,
)


@pytest.mark.parametrize(
    "dic, expected",
    [
        (
            {
                # test whitespace
                "  id": [1, 2, 3],
                "nam e": ["Alice", "Bob", "Charlie"],
                "age  ": [25, 30, 35],
                "ci   ty": ["New York", "Los Angeles", "Chicago"],
            },
            {
                "id": [1, 2, 3],
                "nam_e": ["Alice", "Bob", "Charlie"],
                "age": [25, 30, 35],
                "ci___ty": ["New York", "Los Angeles", "Chicago"],
            },
        ),
        (
            {
                # test lowercasing
                "iD": [1, 2, 3],
                "nAme": ["Alice", "Bob", "Charlie"],
                "aGe": [25, 30, 35],
                "citY": ["New York", "Los Angeles", "Chicago"],
            },
            {
                "id": [1, 2, 3],
                "name": ["Alice", "Bob", "Charlie"],
                "age": [25, 30, 35],
                "city": ["New York", "Los Angeles", "Chicago"],
            },
        ),
        (
            {
                # test dashes
                "id-": [1, 2, 3],
                "-name": ["Alice", "Bob", "Charlie"],
                "a-ge": [25, 30, 35],
                "cit--y": ["New York", "Los Angeles", "Chicago"],
            },
            {
                "id_": [1, 2, 3],
                "_name": ["Alice", "Bob", "Charlie"],
                "a_ge": [25, 30, 35],
                "cit__y": ["New York", "Los Angeles", "Chicago"],
            },
        ),
        (
            {
                # test special characters
                "i$d": [1, 2, 3],
                "nam^*e": ["Alice", "Bob", "Charlie"],
                "age))": [25, 30, 35],
                "#$city": ["New York", "Los Angeles", "Chicago"],
            },
            {
                "id": [1, 2, 3],
                "name": ["Alice", "Bob", "Charlie"],
                "age": [25, 30, 35],
                "city": ["New York", "Los Angeles", "Chicago"],
            },
        ),
    ],
)
def test_standardize_column_names(dic, expected):
    pd.testing.assert_index_equal(
        standardize_column_names(pd.DataFrame(dic)).columns,
        pd.DataFrame(expected).columns,
    )


@pytest.mark.parametrize(
    "dic, expected",
    [
        (
            {
                # Test entire duplicate rows
                "num": [1, 1, 2, 3],
                "name": ["Alice", "Alice", "Bob", "Charlie"],
                "age": [25, 25, 30, 35],
                "city": [
                    "New York",
                    "New York",
                    "Los Angeles",
                    "Chicago",
                ],
            },
            {
                "num": [1, 2, 3],
                "name": ["Alice", "Bob", "Charlie"],
                "age": [25, 30, 35],
                "city": ["New York", "Los Angeles", "Chicago"],
            },
        ),
    ],
)
def test_remove_duplicates(dic, expected):
    pd.testing.assert_frame_equal(
        remove_duplicates(pd.DataFrame(dic))
        .reset_index(drop=True)
        .sort_index(),
        pd.DataFrame(expected),
        check_dtype=True,
    )


@pytest.mark.parametrize(
    "dic, expected",
    [
        # basic verification
        (
            {"num": [1, 2, 3, None]},
            pd.DataFrame(
                {
                    "num": pd.Series((1, 2, 3, None)).astype("Int64"),
                }
            ),
        ),
        (
            {"cost": [1.2, 1.4, 1.5, None]},
            pd.DataFrame(
                {
                    "cost": pd.Series((1.2, 1.4, 1.5, None)).astype(
                        "Float64"
                    )
                }
            ),
        ),
        (
            {"married": [True, False, True, None]},
            pd.DataFrame(
                {
                    "married": pd.Series(
                        (True, False, True, None)
                    ).astype("boolean")
                }
            ),
        ),
        (
            {"name": ["Alex", "John", "Eric", None]},
            pd.DataFrame(
                {
                    "name": pd.Series(
                        ("Alex", "John", "Eric", None)
                    ).astype("string")
                }
            ),
        ),
        (
            {
                "date": [
                    "22-05-23",
                    "24-04-15T17:00",
                    "2000-01-01",
                    None,
                ]
            },
            pd.DataFrame(
                {
                    "date": pd.Series(
                        [
                            "22-05-23",
                            "24-04-15T17:00",
                            "2000-01-01",
                            None,
                        ]
                    ).astype("datetime64[ns]")
                }
            ),
        ),
        (
            {"mixed": [1, "alex", True, None]},
            pd.DataFrame({"mixed": pd.Series((1, "alex", True, None))}),
        ),
        (
            {
                "wrong_date": [
                    "2345-220-11",
                    "23-11-05",
                    "2024-05-01",
                    None,
                ]
            },
            pd.DataFrame(
                {
                    "wrong_date": pd.Series(
                        ("2345-220-11", "23-11-05", "2024-05-01", None)
                    ).astype("string")
                }
            ),
        ),
    ],
)
def test_coerce_data_types(dic, expected):
    pd.testing.assert_frame_equal(
        coerce_nullable_data_types(pd.DataFrame(dic)),
        expected,
        check_dtype=True,
    )
