import polars as pl
import pandas as pd
import pyarrow as pa  # type: ignore
from opsml.data import (
    ColType,
    ColumnSplit,
    Data,
    DataSplit,
    IndiceSplit,
    StartStopSplit,
    DataSplitter,
    Inequality,
    DependentVars,
)
from opsml.types import DataType
import datetime
import numpy as np
from numpy.typing import NDArray


def test_polars_equal_column_split(polars_dataframe: pl.DataFrame):
    eq_col_split = ColumnSplit(
        column_name="foo",
        column_value=3,
        column_type=ColType.Builtin,
    )

    data_split = DataSplit(label="train", column_split=eq_col_split)

    split = DataSplitter.split_data(
        split=data_split,
        data=polars_dataframe,
        data_type=DataType.Polars,
        dependent_vars=DependentVars(),
    )

    assert split is not None
    assert isinstance(split, Data)
    assert split.x.shape == (1, 3)


def test_polars_less_than_column_split(polars_dataframe: pl.DataFrame):
    lessthan_eq_col_split = ColumnSplit(
        column_name="foo",
        column_value=3,
        column_type=ColType.Builtin,
        inequality="<=",
    )

    data_split = DataSplit(label="train", column_split=lessthan_eq_col_split)

    split = DataSplitter.split_data(
        split=data_split,
        data=polars_dataframe,
        data_type=DataType.Polars,
        dependent_vars=DependentVars(),
    )

    assert split is not None
    assert isinstance(split, Data)
    assert split.x.shape == (3, 3)

    lessthan_eq_col_split = ColumnSplit(
        column_name="foo",
        column_value=3,
        column_type=ColType.Builtin,
        inequality=Inequality.LesserThan,
    )

    data_split = DataSplit(label="train", column_split=lessthan_eq_col_split)

    split = DataSplitter.split_data(
        split=data_split,
        data=polars_dataframe,
        data_type=DataType.Polars,
        dependent_vars=DependentVars(),
    )

    assert split is not None
    assert isinstance(split, Data)
    assert split.x.shape == (2, 3)


def test_polars_greater_than_column_split(polars_dataframe: pl.DataFrame):
    lessthan_eq_col_split = ColumnSplit(
        column_name="foo",
        column_value=4,
        column_type=ColType.Builtin,
        inequality=">=",
    )

    data_split = DataSplit(label="train", column_split=lessthan_eq_col_split)

    split = DataSplitter.split_data(
        split=data_split,
        data=polars_dataframe,
        data_type=DataType.Polars,
        dependent_vars=DependentVars(),
    )

    assert split is not None
    assert isinstance(split, Data)
    assert split.x.shape == (3, 3)

    lessthan_eq_col_split = ColumnSplit(
        column_name="foo",
        column_value=4,
        column_type=ColType.Builtin,
        inequality=Inequality.GreaterThan,
    )

    data_split = DataSplit(label="train", column_split=lessthan_eq_col_split)

    split = DataSplitter.split_data(
        split=data_split,
        data=polars_dataframe,
        data_type=DataType.Polars,
        dependent_vars=DependentVars(column_names=["y"]),
    )

    assert split is not None
    assert isinstance(split, Data)
    assert split.x.shape == (2, 2)
    assert split.y.shape == (2, 1)


def test_polars_index_split(polars_dataframe: pl.DataFrame):
    data_split = DataSplit(
        label="train",
        indice_split=IndiceSplit(
            indices=[0, 3, 5],
        ),
    )

    split = DataSplitter.split_data(
        split=data_split,
        data=polars_dataframe,
        data_type=DataType.Polars,
        dependent_vars=DependentVars(),
    )

    assert split is not None
    assert isinstance(split, Data)
    assert split.x.shape == (3, 3)
    assert split.x["foo"].to_list() == [1, 4, 6]


def test_polars_start_stop_split(polars_dataframe: pl.DataFrame):
    data_split = DataSplit(
        label="train",
        start_stop_split=StartStopSplit(start=3, stop=5),
    )

    split = DataSplitter.split_data(
        split=data_split,
        data=polars_dataframe,
        data_type=DataType.Polars,
        dependent_vars=DependentVars(),
    )

    assert split is not None
    assert isinstance(split, Data)
    assert split.x.shape == (2, 3)
    assert split.x["foo"].to_list() == [4, 5]


def test_pandas_inequality_split(pandas_dataframe: pd.DataFrame):
    eq_col_split = ColumnSplit(
        column_name="animals",
        column_value="Horse",
        column_type=ColType.Builtin,
    )

    data_split = DataSplit(label="train", column_split=eq_col_split)

    split = DataSplitter.split_data(
        split=data_split,
        data=pandas_dataframe,
        data_type=DataType.Pandas,
        dependent_vars=DependentVars(),
    )

    assert split is not None
    assert isinstance(split, Data)
    assert split.x.shape == (2, 4)

    lessthan_eq_col_split = ColumnSplit(
        column_name="n_legs",
        column_value=3,
        column_type=ColType.Builtin,
        inequality="<=",
    )

    data_split = DataSplit(label="train", column_split=lessthan_eq_col_split)

    split = DataSplitter.split_data(
        split=data_split,
        data=pandas_dataframe,
        data_type=DataType.Pandas,
        dependent_vars=DependentVars(),
    )

    assert split is not None
    assert isinstance(split, Data)
    assert split.x.shape == (2, 4)

    lessthan_eq_col_split = ColumnSplit(
        column_name="n_legs",
        column_value=3,
        column_type=ColType.Builtin,
        inequality="<",
    )

    data_split = DataSplit(label="train", column_split=lessthan_eq_col_split)

    split = DataSplitter.split_data(
        split=data_split,
        data=pandas_dataframe,
        data_type=DataType.Pandas,
        dependent_vars=DependentVars(),
    )

    assert split is not None
    assert isinstance(split, Data)
    assert split.x.shape == (2, 4)

    col_split = ColumnSplit(
        column_name="n_legs",
        column_value=5,
        column_type=ColType.Builtin,
        inequality=">=",
    )

    data_split = DataSplit(label="train", column_split=col_split)

    split = DataSplitter.split_data(
        split=data_split,
        data=pandas_dataframe,
        data_type=DataType.Pandas,
        dependent_vars=DependentVars(),
    )

    assert split is not None
    assert isinstance(split, Data)
    assert split.x.shape == (4, 4)

    col_split = ColumnSplit(
        column_name="n_legs",
        column_value=5,
        column_type=ColType.Builtin,
        inequality=">",
    )

    data_split = DataSplit(label="train", column_split=col_split)

    split = DataSplitter.split_data(
        split=data_split,
        data=pandas_dataframe,
        data_type=DataType.Pandas,
        dependent_vars=DependentVars(),
    )

    assert split is not None
    assert isinstance(split, Data)
    assert split.x.shape == (2, 4)


def test_pandas_timestamp(pandas_dataframe: pd.DataFrame):
    col_split = ColumnSplit(
        column_name="timestamp",
        column_value=datetime.datetime(2022, 1, 1).timestamp(),
        column_type=ColType.Timestamp,
        inequality=">",
    )

    data_split = DataSplit(label="train", column_split=col_split)

    split = DataSplitter.split_data(
        split=data_split,
        data=pandas_dataframe,
        data_type=DataType.Pandas,
        dependent_vars=DependentVars(column_names=["n_legs"]),
    )

    assert split is not None
    assert isinstance(split, Data)
    assert split.x.shape == (8, 3)
    assert split.y.shape == (8, 1)


def test_pandas_index_split(pandas_dataframe: pl.DataFrame):
    data_split = DataSplit(
        label="train",
        indice_split=IndiceSplit(
            indices=[0, 3, 5],
        ),
    )

    split = DataSplitter.split_data(
        split=data_split,
        data=pandas_dataframe,
        data_type=DataType.Pandas,
        dependent_vars=DependentVars(),
    )

    assert split is not None
    assert isinstance(split, Data)

    assert split.x.shape == (3, 4)
    assert split.x["n_legs"].to_list() == [2, 100, 4]


def test_pandas_start_stop_split(pandas_dataframe: pl.DataFrame):
    data_split = DataSplit(
        label="train",
        start_stop_split=StartStopSplit(start=3, stop=5),
    )

    split = DataSplitter.split_data(
        split=data_split,
        data=pandas_dataframe,
        data_type=DataType.Pandas,
        dependent_vars=DependentVars(),
    )

    assert split is not None
    assert isinstance(split, Data)

    assert split.x.shape == (2, 4)
    assert split.x["n_legs"].to_list() == [100, 2]


def test_pyarrow_index_split(arrow_dataframe: pa.Table):
    data_split = DataSplit(
        label="train",
        indice_split=IndiceSplit(
            indices=[0, 3],
        ),
    )

    split = DataSplitter.split_data(
        split=data_split,
        data=arrow_dataframe,
        data_type=DataType.Arrow,
        dependent_vars=DependentVars(),
    )

    assert split is not None
    assert isinstance(split, Data)

    assert split.x.shape == (2, 2)
    assert split.x["n_legs"].to_pylist() == [2, 100]


def test_pyarrow_start_stop_split(arrow_dataframe: pa.Table):
    data_split = DataSplit(
        label="train",
        start_stop_split=StartStopSplit(start=0, stop=3),
    )

    split = DataSplitter.split_data(
        split=data_split,
        data=arrow_dataframe,
        data_type=DataType.Arrow,
        dependent_vars=DependentVars(column_names=["n_legs"]),
    )

    assert split is not None
    assert isinstance(split, Data)
    assert split.x.shape == (3, 1)
    assert split.y["n_legs"].to_pylist() == [2, 4, 5]

    split = DataSplitter.split_data(
        split=data_split,
        data=arrow_dataframe,
        data_type=DataType.Arrow,
        dependent_vars=DependentVars(column_indices=[0]),
    )

    assert split is not None
    assert isinstance(split, Data)
    assert split.x.shape == (3, 1)
    assert split.y["n_legs"].to_pylist() == [2, 4, 5]


def test_numpy_index_split(numpy_array: NDArray[np.float64]):
    data_split = DataSplit(
        label="train",
        indice_split=IndiceSplit(
            indices=[0, 5, 9],
        ),
    )

    split = DataSplitter.split_data(
        split=data_split,
        data=numpy_array,
        data_type=DataType.Numpy,
        dependent_vars=DependentVars(column_indices=[5]),
    )

    assert split is not None
    assert isinstance(split, Data)
    assert split.x.shape == (3, 99)
    assert split.y.shape == (3, 1)


def test_numpy_start_stop_split(numpy_array: NDArray[np.float64]):
    data_split = DataSplit(
        label="train",
        start_stop_split=StartStopSplit(start=0, stop=5),
    )

    split = DataSplitter.split_data(
        split=data_split,
        data=numpy_array,
        data_type=DataType.Numpy,
        dependent_vars=DependentVars(),
    )

    assert split is not None
    assert isinstance(split, Data)

    assert split.x.shape == (5, 100)
