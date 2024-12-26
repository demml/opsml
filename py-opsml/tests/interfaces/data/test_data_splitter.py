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
)


def test_data_split(polars_dataframe: pl.DataFrame):
    col_split = ColumnSplit(
        column_name="foo",
        column_value=3,
        column_type=ColType.Builtin,
    )

    DataSplit(label="label", column_split=col_split)

    splitter = PolarsColumnSplitter("train", col_split)

    split = splitter.create_split(polars_dataframe)

    assert split is not None
    assert isinstance(split["train"], Data)
    assert list(split.keys())[0] == "train"
    assert split["train"].x.shape == (1, 3)
