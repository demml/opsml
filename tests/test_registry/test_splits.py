from typing import Dict
import pandas as pd
import numpy as np
import polars as pl
import pytest
from pytest_lazyfixture import lazy_fixture
from opsml.registry.cards import DataCard, DataSplit
from opsml.registry.sql.registry import CardRegistry, CardInfo

card_info = CardInfo(name="test-data", team="opsml", user_email="@opsml.com")


@pytest.mark.parametrize("test_data", [lazy_fixture("test_df")])
def test_data_card_splits_column_pandas(test_data: pd.DataFrame):
    # list of dicts will automatically be converted to DataSplit
    data_split = [
        {"label": "train", "column_name": "year", "column_value": 2020},
        {"label": "test", "column_name": "year", "column_value": 2021},
    ]
    data_card = DataCard(data=test_data, info=card_info, data_splits=data_split)
    assert data_card.data_splits[0].column_name == "year"
    assert data_card.data_splits[0].column_value == 2020

    splits = data_card.split_data()

    assert splits.train.X.shape[0] == 1
    assert splits.test.X.shape[0] == 1

    data_card = DataCard(
        data=test_data,
        info=card_info,
        data_splits=data_split,
        dependent_vars=["n_legs"],
    )
    assert data_card.data_splits[0].column_name == "year"
    assert data_card.data_splits[0].column_value == 2020

    splits = data_card.split_data()

    assert splits.train.y.shape[0] == 1
    assert splits.test.y.shape[0] == 1
    assert isinstance(splits.train.X, pd.DataFrame)


def test_data_splits_pandas_inequalities(
    iris_data: pd.DataFrame,
    pandas_timestamp_df: pd.DataFrame,
):
    data = iris_data

    # test ">= and <"
    data_card = DataCard(
        data=data,
        info=card_info,
        dependent_vars=["target"],
        data_splits=[
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
        ],
    )

    data_splits = data_card.split_data()
    assert data_splits.train.X.shape[0] == 93
    assert data_splits.train.y.shape[0] == 93
    assert data_splits.test.X.shape[0] == 57
    assert data_splits.test.y.shape[0] == 57

    # test "> and <="
    data_card = DataCard(
        data=data,
        info=card_info,
        dependent_vars=["target"],
        data_splits=[
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
        ],
    )

    data_splits = data_card.split_data()
    assert data_splits.train.X is not None
    assert data_splits.train.y is not None
    assert data_splits.test.X is not None
    assert data_splits.test.y is not None

    # test "=="
    data_card = DataCard(
        data=data,
        info=card_info,
        dependent_vars=["target"],
        data_splits=[
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
        ],
    )

    data_splits = data_card.split_data()
    assert data_splits.train.X is not None
    assert data_splits.train.y is not None
    assert data_splits.test.X is not None
    assert data_splits.test.y is not None

    ### test timestamp
    date_split = pd.to_datetime("2019-01-01").floor("D")
    data_card = DataCard(
        data=pandas_timestamp_df,
        info=card_info,
        data_splits=[
            DataSplit(
                label="train",
                column_name="date",
                column_value=date_split,
                inequality=">",
            ),
        ],
    )

    data_splits = data_card.split_data()
    assert data_splits.train.X.shape[0] == 1


@pytest.mark.parametrize("test_data", [lazy_fixture("test_df")])
def test_data_card_splits_row_pandas(test_data: pd.DataFrame):
    data_split = [
        DataSplit(label="train", start=0, stop=2),
        DataSplit(label="test", start=3, stop=4),
    ]

    data_card = DataCard(
        data=test_data,
        info=card_info,
        data_splits=data_split,
    )

    assert data_card.data_splits[0].start == 0
    assert data_card.data_splits[0].stop == 2

    splits = data_card.split_data()
    assert splits.train.X.shape[0] == 2
    assert splits.test.X.shape[0] == 1

    data_card = DataCard(
        data=test_data,
        info=card_info,
        data_splits=data_split,
        dependent_vars=["n_legs"],
    )

    splits = data_card.split_data()
    assert splits.train.y.shape[0] == 2
    assert splits.test.y.shape[0] == 1


@pytest.mark.parametrize("test_data", [lazy_fixture("test_df")])
def test_data_card_splits_index_pandas(test_data: pd.DataFrame):
    data_split = [
        DataSplit(label="train", indices=[0, 1, 2]),
    ]

    data_card = DataCard(
        data=test_data,
        info=card_info,
        data_splits=data_split,
    )
    splits = data_card.split_data()
    assert splits.train.X.shape[0] == 3

    data_card = DataCard(
        data=test_data,
        info=card_info,
        data_splits=data_split,
        dependent_vars=["n_legs"],
    )

    splits = data_card.split_data()
    assert splits.train.y.shape[0] == 3


########## Numpy


def test_numpy_splits_index(regression_data):
    X, y = regression_data

    data_split = [
        DataSplit(label="train", indices=[0, 1, 2]),
    ]

    data_card = DataCard(
        data=X,
        info=card_info,
        data_splits=data_split,
    )
    splits = data_card.split_data()
    assert splits.train.X.shape[0] == 3
    assert isinstance(splits.train.X, np.ndarray)


def test_numpy_splits_row(regression_data):
    X, y = regression_data

    data_split = [
        DataSplit(label="train", start=0, stop=3),
    ]

    data_card = DataCard(
        data=X,
        info=card_info,
        data_splits=data_split,
    )
    splits = data_card.split_data()
    assert splits.train.X.shape[0] == 3


########## Polars
def test_data_splits_polars_column_value(iris_data_polars: pl.DataFrame):
    data = iris_data_polars

    # test ">= and <"
    data_card = DataCard(
        data=data,
        info=card_info,
        dependent_vars=["target"],
        data_splits=[
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
        ],
    )

    data_splits = data_card.split_data()

    assert data_splits.train.X.shape[0] == 93
    assert data_splits.train.y.shape[0] == 93
    assert data_splits.test.X.shape[0] == 57
    assert data_splits.test.y.shape[0] == 57

    # test "> and <="
    data_card = DataCard(
        data=data,
        info=card_info,
        dependent_vars=["target"],
        data_splits=[
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
        ],
    )

    data_splits = data_card.split_data()
    assert data_splits.train.X is not None
    assert data_splits.train.y is not None
    assert data_splits.test.X is not None
    assert data_splits.test.y is not None

    # test "=="
    data_card = DataCard(
        data=data,
        info=card_info,
        data_splits=[
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
        ],
    )

    splits = data_card.split_data()
    assert splits.train.X is not None
    assert splits.test.X is not None
    assert isinstance(splits.train.X, pl.DataFrame)


def test_data_splits_polars_index(iris_data_polars: pl.DataFrame):
    data = iris_data_polars

    # depen vars
    data_card = DataCard(
        data=data,
        info=card_info,
        dependent_vars=["target"],
        data_splits=[DataSplit(label="train", start=0, stop=10)],
    )
    data_splits = data_card.split_data()

    assert data_splits.train.X.shape[0] == 10
    assert data_splits.train.y.shape[0] == 10

    # no depen vars
    data_card = DataCard(
        data=data,
        info=card_info,
        data_splits=[DataSplit(label="train", start=0, stop=10)],
    )
    data_splits = data_card.split_data()

    assert data_splits.train.X.shape[0] == 10


def test_data_splits_polars_row(
    db_registries: Dict[str, CardRegistry],
    iris_data_polars: pl.DataFrame,
):
    data = iris_data_polars

    # depen vars
    data_card = DataCard(
        data=data,
        info=card_info,
        dependent_vars=["target"],
        data_splits=[DataSplit(label="train", indices=[0, 1, 2])],
    )
    data_splits = data_card.split_data()

    assert data_splits.train.X.shape[0] == 3
    assert data_splits.train.y.shape[0] == 3

    # no depen vars
    data_card = DataCard(
        data=data,
        info=card_info,
        data_splits=[DataSplit(label="train", indices=[0, 1, 2])],
    )
    data_splits = data_card.split_data()

    assert data_splits.train.X.shape[0] == 3


def test_datacard_split_fail(db_registries: Dict[str, CardRegistry], test_df: pd.DataFrame):
    registry: CardRegistry = db_registries["data"]

    data_card = DataCard(
        data=test_df,
        info=card_info,
        feature_descriptions={"test": "test"},
    )

    registry.register_card(card=data_card)

    loaded_card: DataCard = registry.load_card(uid=data_card.uid)

    # load data
    loaded_card.load_data()

    # should raise logging info
    loaded_card.load_data()

    with pytest.raises(ValueError):
        data_card.split_data()
