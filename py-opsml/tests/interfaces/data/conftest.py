import polars as pl
import pyarrow as pa  # type: ignore
import pytest
import pandas as pd
import numpy as np
from numpy.typing import NDArray


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


@pytest.fixture
def arrow_dataframe() -> pa.Table:
    n_legs = pa.array([2, 4, 5, 100])
    animals = pa.array(["Flamingo", "Horse", "Brittle stars", "Centipede"])
    names = ["n_legs", "animals"]
    table = pa.Table.from_arrays([n_legs, animals], names=names)

    return table


@pytest.fixture
def numpy_array() -> NDArray[np.float64]:
    array = np.random.rand(10, 100)
    return array


# create a multi-type polars dataframe
@pytest.fixture
def multi_type_polars_dataframe() -> pl.DataFrame:
    df = pl.DataFrame(
        {
            # int
            "foo": [1, 2, 3],
            # float
            "bar": [6.0, 7.0, 8.0],
            # str
            "ham": ["a", "b", "c"],
        }
    )
    return df
