import polars as pl
import pandas as pd
from opsml import (
    ColType,
    ColValType,
    ColumnSplit,
    Data,
    DataSplit,
    IndiceSplit,
    PolarsColumnSplitter,
    StartStopSplit,
    DataSplitter,
    DataType,
    Inequality,
)
import datetime


def test_polars_equal_column_split(polars_dataframe: pl.DataFrame):
    eq_col_split = ColumnSplit(
        column_name="foo",
        column_value=3,
        column_type=ColType.Builtin,
    )

    data_split = DataSplit(label="train", column_split=eq_col_split)
    splitter = DataSplitter()

    split = splitter.split_data(
        split=data_split,
        data=polars_dataframe,
        data_type=DataType.Polars,
        dependent_vars=[],
    )

    assert split is not None
    assert isinstance(split["train"], Data)
    assert list(split.keys())[0] == "train"
    assert split["train"].x.shape == (1, 3)


def test_polars_less_than_column_split(polars_dataframe: pl.DataFrame):
    lessthan_eq_col_split = ColumnSplit(
        column_name="foo",
        column_value=3,
        column_type=ColType.Builtin,
        inequality="<=",
    )

    data_split = DataSplit(label="train", column_split=lessthan_eq_col_split)
    splitter = DataSplitter()

    split = splitter.split_data(
        split=data_split,
        data=polars_dataframe,
        data_type=DataType.Polars,
        dependent_vars=[],
    )

    assert split is not None
    assert isinstance(split["train"], Data)
    assert list(split.keys())[0] == "train"
    assert split["train"].x.shape == (3, 3)

    lessthan_eq_col_split = ColumnSplit(
        column_name="foo",
        column_value=3,
        column_type=ColType.Builtin,
        inequality=Inequality.LesserThan,
    )

    data_split = DataSplit(label="train", column_split=lessthan_eq_col_split)
    splitter = DataSplitter()

    split = splitter.split_data(
        split=data_split,
        data=polars_dataframe,
        data_type=DataType.Polars,
        dependent_vars=[],
    )

    assert split is not None
    assert isinstance(split["train"], Data)
    assert list(split.keys())[0] == "train"
    assert split["train"].x.shape == (2, 3)


def test_polars_greater_than_column_split(polars_dataframe: pl.DataFrame):
    lessthan_eq_col_split = ColumnSplit(
        column_name="foo",
        column_value=4,
        column_type=ColType.Builtin,
        inequality=">=",
    )

    data_split = DataSplit(label="train", column_split=lessthan_eq_col_split)
    splitter = DataSplitter()

    split = splitter.split_data(
        split=data_split,
        data=polars_dataframe,
        data_type=DataType.Polars,
        dependent_vars=[],
    )

    assert split is not None
    assert isinstance(split["train"], Data)
    assert list(split.keys())[0] == "train"
    assert split["train"].x.shape == (3, 3)

    lessthan_eq_col_split = ColumnSplit(
        column_name="foo",
        column_value=4,
        column_type=ColType.Builtin,
        inequality=Inequality.GreaterThan,
    )

    data_split = DataSplit(label="train", column_split=lessthan_eq_col_split)
    splitter = DataSplitter()

    split = splitter.split_data(
        split=data_split,
        data=polars_dataframe,
        data_type=DataType.Polars,
        dependent_vars=["y"],
    )

    assert split is not None
    assert isinstance(split["train"], Data)
    assert list(split.keys())[0] == "train"
    assert split["train"].x.shape == (2, 2)
    assert split["train"].y.shape == (2, 1)


def test_polars_index_split(polars_dataframe: pl.DataFrame):
    data_split = DataSplit(
        label="train",
        indice_split=IndiceSplit(
            indices=[0, 3, 5],
        ),
    )
    splitter = DataSplitter()

    split = splitter.split_data(
        split=data_split,
        data=polars_dataframe,
        data_type=DataType.Polars,
        dependent_vars=[],
    )

    assert split is not None
    assert isinstance(split["train"], Data)
    assert list(split.keys())[0] == "train"
    assert split["train"].x.shape == (3, 3)
    assert split["train"].x["foo"].to_list() == [1, 4, 6]


def test_polars_start_stop_split(polars_dataframe: pl.DataFrame):
    data_split = DataSplit(
        label="train",
        start_stop_split=StartStopSplit(start=3, stop=5),
    )
    splitter = DataSplitter()

    split = splitter.split_data(
        split=data_split,
        data=polars_dataframe,
        data_type=DataType.Polars,
        dependent_vars=[],
    )

    assert split is not None
    assert isinstance(split["train"], Data)
    assert list(split.keys())[0] == "train"
    assert split["train"].x.shape == (2, 3)
    assert split["train"].x["foo"].to_list() == [4, 5]


def test_pandas_inequality_split(pandas_dataframe: pd.DataFrame):
    eq_col_split = ColumnSplit(
        column_name="animals",
        column_value="Horse",
        column_type=ColType.Builtin,
    )

    data_split = DataSplit(label="train", column_split=eq_col_split)
    splitter = DataSplitter()

    split = splitter.split_data(
        split=data_split,
        data=pandas_dataframe,
        data_type=DataType.Pandas,
        dependent_vars=[],
    )

    assert split is not None
    assert isinstance(split["train"], Data)
    assert list(split.keys())[0] == "train"
    assert split["train"].x.shape == (2, 4)

    lessthan_eq_col_split = ColumnSplit(
        column_name="n_legs",
        column_value=3,
        column_type=ColType.Builtin,
        inequality="<=",
    )

    data_split = DataSplit(label="train", column_split=lessthan_eq_col_split)
    splitter = DataSplitter()

    split = splitter.split_data(
        split=data_split,
        data=pandas_dataframe,
        data_type=DataType.Pandas,
        dependent_vars=[],
    )

    assert split is not None
    assert isinstance(split["train"], Data)
    assert list(split.keys())[0] == "train"
    assert split["train"].x.shape == (2, 4)

    lessthan_eq_col_split = ColumnSplit(
        column_name="n_legs",
        column_value=3,
        column_type=ColType.Builtin,
        inequality="<",
    )

    data_split = DataSplit(label="train", column_split=lessthan_eq_col_split)
    splitter = DataSplitter()

    split = splitter.split_data(
        split=data_split,
        data=pandas_dataframe,
        data_type=DataType.Pandas,
        dependent_vars=[],
    )

    assert split is not None
    assert isinstance(split["train"], Data)
    assert list(split.keys())[0] == "train"
    assert split["train"].x.shape == (2, 4)

    col_split = ColumnSplit(
        column_name="n_legs",
        column_value=5,
        column_type=ColType.Builtin,
        inequality=">=",
    )

    data_split = DataSplit(label="train", column_split=col_split)
    splitter = DataSplitter()

    split = splitter.split_data(
        split=data_split,
        data=pandas_dataframe,
        data_type=DataType.Pandas,
        dependent_vars=[],
    )

    assert split is not None
    assert isinstance(split["train"], Data)
    assert list(split.keys())[0] == "train"
    assert split["train"].x.shape == (4, 4)

    col_split = ColumnSplit(
        column_name="n_legs",
        column_value=5,
        column_type=ColType.Builtin,
        inequality=">",
    )

    data_split = DataSplit(label="train", column_split=col_split)
    splitter = DataSplitter()

    split = splitter.split_data(
        split=data_split,
        data=pandas_dataframe,
        data_type=DataType.Pandas,
        dependent_vars=[],
    )

    assert split is not None
    assert isinstance(split["train"], Data)
    assert list(split.keys())[0] == "train"
    assert split["train"].x.shape == (2, 4)


def test_pandas_timestamp(pandas_dataframe: pd.DataFrame):
    col_split = ColumnSplit(
        column_name="timestamp",
        column_value=datetime.datetime(2022, 1, 1).timestamp(),
        column_type=ColType.Timestamp,
        inequality=">",
    )

    data_split = DataSplit(label="train", column_split=col_split)
    splitter = DataSplitter()

    split = splitter.split_data(
        split=data_split,
        data=pandas_dataframe,
        data_type=DataType.Pandas,
        dependent_vars=["n_legs"],
    )

    assert split is not None
    assert isinstance(split["train"], Data)
    assert list(split.keys())[0] == "train"
    assert split["train"].x.shape == (8, 3)
    assert split["train"].y.shape == (8, 1)


def test_pandas_index_split(pandas_dataframe: pl.DataFrame):
    data_split = DataSplit(
        label="train",
        indice_split=IndiceSplit(
            indices=[0, 3, 5],
        ),
    )
    splitter = DataSplitter()

    split = splitter.split_data(
        split=data_split,
        data=pandas_dataframe,
        data_type=DataType.Pandas,
        dependent_vars=[],
    )

    assert split is not None
    assert isinstance(split["train"], Data)
    assert list(split.keys())[0] == "train"
    assert split["train"].x.shape == (3, 4)
    assert split["train"].x["n_legs"].to_list() == [2, 100, 4]


def test_pandas_start_stop_split(pandas_dataframe: pl.DataFrame):
    data_split = DataSplit(
        label="train",
        start_stop_split=StartStopSplit(start=3, stop=5),
    )
    splitter = DataSplitter()

    split = splitter.split_data(
        split=data_split,
        data=pandas_dataframe,
        data_type=DataType.Pandas,
        dependent_vars=[],
    )

    assert split is not None
    assert isinstance(split["train"], Data)
    assert list(split.keys())[0] == "train"
    assert split["train"].x.shape == (2, 4)
    assert split["train"].x["n_legs"].to_list() == [100, 2]
