import numpy as np
import pandas as pd
import polars as pl
import pytest

from opsml.cards import CardInfo, DataCard, DataSplit
from opsml.data import NumpyData, PandasData, PolarsData
from opsml.registry import CardRegistries, CardRegistry

card_info = CardInfo(name="test-data", repository="opsml", contact="@opsml.com")


def test_data_card_splits_column_pandas(pandas_data: PandasData):

    data_card = DataCard(interface=pandas_data, info=card_info)
    assert data_card.interface.data_splits[0].column_name == "year"
    assert data_card.interface.data_splits[0].column_value == 2020

    splits = data_card.split_data()

    assert splits.train.X.shape[0] == 3
    assert splits.test.X.shape[0] == 1

    data_card = DataCard(interface=pandas_data, info=card_info)
    assert data_card.data_splits[0].column_name == "year"
    assert data_card.data_splits[0].column_value == 2020

    splits = data_card.split_data()

    assert splits.train.y.shape[0] == 3
    assert splits.test.y.shape[0] == 1
    assert isinstance(splits.train.X, pd.DataFrame)


def test_data_splits_pandas_inequalities(iris_data: PandasData, pandas_timestamp_df: PandasData):
    data = iris_data
    data_splits = [
        DataSplit(
            label="train",
            column_name="sepal_width_cm",
            column_value=3.0,
            inequality=">=",
        ),
        DataSplit(
            label="test",
            column_name="sepal_width_cm",
            column_value=3.0,
            inequality="<",
        ),
    ]
    data.data_splits = data_splits

    # test ">= and <"
    data_card = DataCard(interface=data, info=card_info)

    data_splits = data_card.split_data()
    assert data_splits.train.X.shape[0] == 93
    assert data_splits.train.y.shape[0] == 93
    assert data_splits.test.X.shape[0] == 57
    assert data_splits.test.y.shape[0] == 57

    data_splits = [
        DataSplit(
            label="train",
            column_name="sepal_width_cm",
            column_value=3.0,
            inequality=">",
        ),
        DataSplit(
            label="test",
            column_name="sepal_width_cm",
            column_value=3.0,
            inequality="<=",
        ),
    ]
    data.data_splits = data_splits

    # test "> and <="
    data_card = DataCard(interface=data, info=card_info)

    data_splits = data_card.split_data()
    assert data_splits.train.X is not None
    assert data_splits.train.y is not None
    assert data_splits.test.X is not None
    assert data_splits.test.y is not None

    data_splits = [
        DataSplit(
            label="train",
            column_name="sepal_width_cm",
            column_value=3.0,
        ),
        DataSplit(
            label="test",
            column_name="sepal_width_cm",
            column_value=2.0,
        ),
    ]
    data.data_splits = data_splits

    # test "=="
    data_card = DataCard(interface=data, info=card_info)

    data_splits = data_card.split_data()
    assert data_splits.train.X is not None
    assert data_splits.train.y is not None
    assert data_splits.test.X is not None
    assert data_splits.test.y is not None

    ### test timestamp
    date_split = pd.to_datetime("2019-01-01").floor("D")
    data_splits = [
        DataSplit(
            label="train",
            column_name="date",
            column_value=date_split,
            inequality=">",
        ),
    ]
    pandas_timestamp_df.data_splits = data_splits

    data_card = DataCard(interface=pandas_timestamp_df, info=card_info)

    data_splits = data_card.split_data()
    assert data_splits.train.X.shape[0] == 1


def test_data_card_splits_row_pandas(pandas_data: PandasData):
    data_split = [
        DataSplit(label="train", start=0, stop=2),
        DataSplit(label="test", start=3, stop=4),
    ]

    pandas_data.data_splits = data_split

    data_card = DataCard(interface=pandas_data, info=card_info)

    assert data_card.data_splits[0].start == 0
    assert data_card.data_splits[0].stop == 2

    splits = data_card.split_data()
    assert splits.train.X.shape[0] == 2
    assert splits.test.X.shape[0] == 1

    # use interface
    pandas_data.dependent_vars = ["n_legs"]
    splits = pandas_data.split_data()
    assert splits.train.y.shape[0] == 2
    assert splits.test.y.shape[0] == 1


def test_data_card_splits_index_pandas(pandas_data: PandasData):
    data_split = [DataSplit(label="train", indices=[0, 1, 2])]
    pandas_data.data_splits = data_split
    pandas_data.dependent_vars = ["n_legs"]

    splits = pandas_data.split_data()
    assert splits.train.X.shape[0] == 3
    assert splits.train.y.shape[0] == 3


########## Numpy
def test_numpy_splits_index(numpy_data: NumpyData):

    data_split = [DataSplit(label="train", indices=[0, 1, 2])]
    numpy_data.data_splits = data_split
    splits = numpy_data.split_data()
    assert splits.train.X.shape[0] == 3
    assert isinstance(splits.train.X, np.ndarray)


def test_numpy_splits_row(numpy_data: NumpyData):

    data_split = [DataSplit(label="train", start=0, stop=3)]
    numpy_data.data_splits = data_split
    splits = numpy_data.split_data()
    assert splits.train.X.shape[0] == 3


########## Polars
def test_data_splits_polars_column_value(polars_data: PolarsData):
    data_splits = [
        DataSplit(
            label="train",
            column_name="foo",
            column_value=3,
            inequality=">=",
        ),
        DataSplit(
            label="test",
            column_name="foo",
            column_value=3,
            inequality="<",
        ),
    ]

    polars_data.data_splits = data_splits
    data_splits = polars_data.split_data()

    assert data_splits.train.X.shape[0] == 4
    assert data_splits.train.y.shape[0] == 4
    assert data_splits.test.X.shape[0] == 2
    assert data_splits.test.y.shape[0] == 2

    # test "> and <="
    data_splits = [
        DataSplit(
            label="train",
            column_name="foo",
            column_value=3.0,
            inequality=">",
        ),
        DataSplit(
            label="test",
            column_name="foo",
            column_value=3.0,
            inequality="<=",
        ),
    ]
    polars_data.data_splits = data_splits

    data_splits = polars_data.split_data()
    assert data_splits.train.X.shape[0] == 3
    assert data_splits.train.y.shape[0] == 3
    assert data_splits.test.X.shape[0] == 3
    assert data_splits.test.y.shape[0] == 3

    # test "=="
    data_splits = [
        DataSplit(
            label="train",
            column_name="foo",
            column_value=3.0,
        ),
        DataSplit(
            label="test",
            column_name="foo",
            column_value=2.0,
        ),
    ]
    polars_data.data_splits = data_splits

    data_splits = polars_data.split_data()
    assert data_splits.train.X.shape[0] == 1
    assert data_splits.train.y.shape[0] == 1
    assert data_splits.test.X.shape[0] == 1
    assert data_splits.test.y.shape[0] == 1
    assert isinstance(data_splits.train.X, pl.DataFrame)


def test_data_splits_polars_index(polars_data: PolarsData):
    data_split = [DataSplit(label="train", start=0, stop=5)]
    polars_data.data_splits = data_split
    data_splits = polars_data.split_data()

    assert data_splits.train.X.shape[0] == 5
    assert data_splits.train.y.shape[0] == 5

    # no depen vars
    polars_data.dependent_vars = None
    data_splits = polars_data.split_data()

    assert data_splits.train.X.shape[0] == 5


def test_data_splits_polars_row(polars_data: PolarsData):

    data_split = [DataSplit(label="train", indices=[0, 1, 2])]
    polars_data.data_splits = data_split

    data_splits = polars_data.split_data()
    assert data_splits.train.X.shape[0] == 3
    assert data_splits.train.y.shape[0] == 3

    # no depen vars
    polars_data.dependent_vars = None
    data_splits = polars_data.split_data()

    assert data_splits.train.X.shape[0] == 3


def test_datacard_split_fail(pandas_data: PandasData, db_registries: CardRegistries):
    registry: CardRegistry = db_registries.data
    pandas_data.data_splits = []
    pandas_data.feature_descriptions = {"test": "test"}

    data_card = DataCard(interface=pandas_data, info=card_info)

    registry.register_card(card=data_card)

    loaded_card: DataCard = registry.load_card(uid=data_card.uid)

    # load data
    loaded_card.load_data()

    # should raise logging info
    loaded_card.load_data()

    with pytest.raises(ValueError):
        data_card.split_data()
