import polars as pl
import pytest
import pandas as pd


@pytest.fixture
def polars_dataframe() -> pl.DataFrame:
    df = pl.DataFrame(
        {
            "foo": [1, 2, 3, 4, 5, 6],
            "bar": ["a", "b", "c", "d", "e", "f"],
            "y": [1, 2, 3, 4, 5, 6],
        }
    )

    return df


@pytest.fixture
def pandas_dataframe() -> pd.DataFrame:
    df = pd.DataFrame(
        {
            "year": [2020, 2022, 2019, 2020, 2020, 2022, 2019, 2021],
            "n_legs": [2, 4, 5, 100, 2, 4, 5, 100],
            "animals": [
                "Flamingo",
                "Horse",
                "Brittle stars",
                "Centipede",
                "Flamingo",
                "Horse",
                "Brittle stars",
                "Centipede",
            ],
        }
    )

    # create timestamp column
    df["timestamp"] = pd.Timestamp.today()

    return df
