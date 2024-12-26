import polars as pl
import pytest


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
