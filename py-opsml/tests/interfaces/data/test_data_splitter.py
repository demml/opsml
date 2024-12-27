import polars as pl
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
