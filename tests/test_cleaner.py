import pytest
import pandas as pd
import numpy as np
from eda_cleaner.cleaner import (
    standardize_column_names,
    handle_missing_values,
    remove_duplicates,
    coerce_data_types,
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
    assert (
        standardize_column_names(pd.DataFrame(dic)).columns.to_list()
        == pd.DataFrame(expected).columns.to_list()
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
        # DEPRECATED
        # (
        #     {
        #         # Test that identical columns,
        #         # different id's are removed
        #         "some_id": [1, 2, 3, 4],
        #         "name": ["Alice", "Bob", "Bob", "Charlie"],
        #         "age": [25, 30, 30, 35],
        #         "city": [
        #             "New York",
        #             "Los Angeles",
        #             "Los Angeles",
        #             "Chicago",
        #         ],
        #     },
        #     {
        #         "some_id": [1, 2, 4],
        #         "name": ["Alice", "Bob", "Charlie"],
        #         "age": [25, 30, 35],
        #         "city": ["New York", "Los Angeles", "Chicago"],
        #     },
        # ),
    ],
)
def test_remove_duplicates(dic, expected):
    assert (
        remove_duplicates(pd.DataFrame(dic)).to_dict(orient="list")
        == expected
    )


@pytest.mark.parametrize(
    "dic, expected",
    [
        (
            {
                # Test yes or no becomes bool
                "num": [1, 2, 3],
                "name": ["yEs", "No", "YeS"],
                "age": [25, 30, 35],
                "city": ["New York", "Los Angeles", "Chicago"],
            },
            {
                "num": [1, 2, 3],
                "name": [True, False, True],
                "age": [25, 30, 35],
                "city": ["New York", "Los Angeles", "Chicago"],
            },
        ),
        (
            {
                #
                "num": [1, 2, 3],
                "name": ["truE", "FalSe", "True"],
                "age": [25, 30, 35],
                "city": ["New York", "Los Angeles", "Chicago"],
            },
            {
                "num": [1, 2, 3],
                "name": [True, False, True],
                "age": [25, 30, 35],
                "city": ["New York", "Los Angeles", "Chicago"],
            },
        ),
        (
            {
                #
                "num": [1, 0, None],
                "name": ["True", "Yes", "True"],
                "age": [25, 30, 35],
                "city": ["New York", "Los Angeles", "Chicago"],
            },
            {
                "num": [1, 0, pd.NA],
                "name": ["True", "Yes", "True"],
                "age": [25, 30, 35],
                "city": ["New York", "Los Angeles", "Chicago"],
            },
        ),
        (
            {
                #
                "num": [1, 2, 3, 4],
                "name": ["True", "False", "True", None],
                "age": [25, 30, 35, 40],
                "city": ["New York", "Los Angeles", "Chicago", None],
            },
            {
                "num": [1, 2, 3, 4],
                "name": [True, False, True, pd.NA],
                "age": [25, 30, 35, 40],
                "city": ["New York", "Los Angeles", "Chicago", None],
            },
        ),
        (
            {
                #
                "num": [1, 2, 3, 5],
                "name": ["no", "Yes", "no", None],
                "age": [25, 30, 35, None],
                "city": ["New York", "Los Angeles", "Chicago", None],
            },
            {
                "num": [1, 2, 3, 5],
                "name": [False, True, False, pd.NA],
                "age": [25, 30, 35, pd.NA],
                "city": ["New York", "Los Angeles", "Chicago", None],
            },
        ),
        (
            {
                #
                "num": [1, 2, 3, 5],
                "name": [0, 1, 0, None],
                "age": [25, 30, 35, 6],
                "city": ["New York", "Los Angeles", "Chicago", None],
            },
            {
                "num": [1, 2, 3, 5],
                "name": [False, True, False, pd.NA],
                "age": [25, 30, 35, 6],
                "city": ["New York", "Los Angeles", "Chicago", None],
            },
        ),
    ],
)
def test_coerce_data_types(dic, expected):
    assert (
        coerce_data_types(pd.DataFrame(dic)).to_dict(orient="list")
        == expected
    )
