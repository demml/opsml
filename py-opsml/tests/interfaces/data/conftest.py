import polars as pl
import pyarrow as pa  # type: ignore
import pytest
import pandas as pd
import numpy as np
from numpy.typing import NDArray
from datetime import datetime, timedelta


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
        data={
            # int8
            "int8": [1, 2, 3],
            # int16
            "int16": [1, 2, 3],
            # int32
            "int32": [1, 2, 3],
            # int64
            "int64": [1, 2, 3],
            # uint8
            "uint8": [1, 2, 3],
            # uint16
            "uint16": [1, 2, 3],
            # uint32
            "uint32": [1, 2, 3],
            # uint64
            "uint64": [1, 2, 3],
            # float32
            "float32": [1.0, 2.0, 3.0],
            # float64
            "float64": [1.0, 2.0, 3.0],
            # decimal
            "decimal": [1.0, 2.0, 3.0],
            # boolean
            "bool": [True, False, True],
            # String
            "string": ["a", "b", "c"],
            # Utf8
            "utf8": ["a", "b", "c"],
            # binary
            "binary": [b"a", b"b", b"c"],
            # date
            "date": ["2021-01-01", "2021-01-02", "2021-01-03"],
            # time
            "time": [43200000000000, 43200000000000, 43200000000000],
            # datetime
            "datetime": [
                datetime(2021, 1, 1, 12, 0, 0),
                datetime(2021, 1, 2, 12, 0, 0),
                datetime(2021, 1, 3, 12, 0, 0),
            ],
            # duration
            "duration": [
                timedelta(days=1),  # 1 day in nanoseconds
                timedelta(days=2),  # 2 days in nanoseconds
                timedelta(days=3),  # 3 days in nanoseconds
            ],
            # categorical
            "categorical": ["a", "b", "c"],
            # enum
            "enum": ["a", "b", "c"],
            # object
            "object": [1, "a", 1.0],
            # null
            "null": [None, None, None],
            # list
            "list": [
                [1, 2, 3],
                [1, 2, 3],
                [1, 2, 3],
            ],
            # array
            "array": [
                [1, 2, 3],
                [1, 2, 3],
                [1, 2, 3],
            ],
            # array2
            "array2": [
                [[1, 2, 3], [1, 2, 3]],
                [[1, 2, 3], [1, 2, 3]],
                [[1, 2, 3], [1, 2, 3]],
            ],
            # struct column
            "struct": [
                {"a": 1, "b": [1, 2, 3]},
                {"a": 1, "b": [1, 2, 3]},
                {"a": 1, "b": [1, 2, 3]},
            ],
        },
        schema={
            "int8": pl.Int8,
            "int16": pl.Int16,
            "int32": pl.Int32,
            "int64": pl.Int64,
            "uint8": pl.UInt8,
            "uint16": pl.UInt16,
            "uint32": pl.UInt32,
            "uint64": pl.UInt64,
            "float32": pl.Float32,
            "float64": pl.Float64,
            "decimal": pl.Decimal(5, 2),
            "bool": pl.Boolean,
            "string": pl.String,
            "utf8": pl.Utf8,
            "binary": pl.Binary,
            "date": pl.Date,
            "time": pl.Time,
            "datetime": pl.Datetime("ms", "UTC"),
            "duration": pl.Duration("ns"),
            "categorical": pl.Categorical,
            "enum": pl.Enum(["a", "b", "c"]),
            "object": pl.Object,
            "null": pl.Null,
            "list": pl.List(pl.Int64),
            "array": pl.Array(pl.Int64, shape=(3,)),
            "array2": pl.Array(pl.Int64, shape=(2, 3)),
            "struct": pl.Struct({"a": pl.Int64, "b": pl.List(pl.Int64)}),
        },
    )

    return df


@pytest.fixture
def multi_type_polars_dataframe2(
    multi_type_polars_dataframe: pl.DataFrame,
) -> pl.DataFrame:
    # pop struct, array2, and object columns
    new_df = multi_type_polars_dataframe = multi_type_polars_dataframe.drop(
        ["struct", "array2", "object"]
    )

    return new_df


@pytest.fixture
def pandas_mixed_type_dataframe() -> pd.DataFrame:
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
    df["category"] = pd.Categorical(["a", "b", "c", "d", "e", "f", "g", "h"])

    return df
