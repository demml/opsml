from typing import Dict
import pandas as pd
import numpy as np
import polars as pl
import pytest
from pytest_lazyfixture import lazy_fixture
from opsml.registry.cards.cards import DataCard, DataSplit
from opsml.registry.sql.registry import CardRegistry
from sklearn.model_selection import train_test_split


@pytest.mark.parametrize("test_data", [lazy_fixture("test_df")])
def test_data_card_splits(test_data: pd.DataFrame):
    # list of dicts will automatically be converted to DataSplit
    data_split = [
        {"label": "train", "column_name": "year", "column_value": 2020},
        {"label": "test", "column_name": "year", "column_value": 2021},
    ]
    data_card = DataCard(
        data=test_data,
        name="test_df",
        team="mlops",
        user_email="mlops.com",
        data_splits=data_split,
    )
    assert data_card.data_splits[0].column_name == "year"
    assert data_card.data_splits[0].column_value == 2020

    data_split = [
        DataSplit(label="train", start=0, stop=2),
        DataSplit(label="test", start=3, stop=4),
    ]

    data_card = DataCard(
        data=test_data,
        name="test_df",
        team="mlops",
        user_email="mlops.com",
        data_splits=data_split,
    )

    assert data_card.data_splits[0].start == 0
    assert data_card.data_splits[0].stop == 2


def test_data_splits(db_registries: Dict[str, CardRegistry], iris_data: pd.DataFrame):
    train_idx, test_idx = train_test_split(np.arange(iris_data.shape[0]), test_size=0.2)

    data_name = "test_df"
    team = "mlops"
    user_email = "mlops.com"
    registry: CardRegistry = db_registries["data"]

    data_card_1 = DataCard(
        data=iris_data,
        name=data_name,
        team=team,
        user_email=user_email,
        dependent_vars=["target"],
        data_splits=[
            DataSplit(label="train", indices=train_idx),
            DataSplit(label="test", indices=test_idx),
        ],
    )

    data_splits = data_card_1.split_data()
    assert data_splits.train.X is not None
    assert data_splits.train.y is not None
    assert data_splits.test.X is not None
    assert data_splits.test.y is not None

    data_card_2 = DataCard(
        data=iris_data,
        name=data_name,
        team=team,
        user_email=user_email,
        data_splits=[
            DataSplit(label="train", indices=train_idx),
            DataSplit(label="test", indices=test_idx),
        ],
    )

    data_splits = data_card_2.split_data()
    assert data_splits.train.X is not None
    assert data_splits.train.y is None
    assert data_splits.test.X is not None
    assert data_splits.test.y is None


def test_data_splits_column_value(db_registries: Dict[str, CardRegistry], iris_data: pd.DataFrame):
    data = iris_data
    data_name = "test_df"
    team = "mlops"
    user_email = "mlops.com"
    registry: CardRegistry = db_registries["data"]

    # test ">= and <"
    data_card = DataCard(
        data=data,
        name=data_name,
        team=team,
        user_email=user_email,
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
        name=data_name,
        team=team,
        user_email=user_email,
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
        name=data_name,
        team=team,
        user_email=user_email,
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


def test_data_splits_polars_column_value(
    db_registries: Dict[str, CardRegistry],
    iris_data_polars: pl.DataFrame,
):
    data = iris_data_polars
    data_name = "test_df"
    team = "mlops"
    user_email = "mlops.com"
    registry: CardRegistry = db_registries["data"]

    # test ">= and <"
    data_card = DataCard(
        data=data,
        name=data_name,
        team=team,
        user_email=user_email,
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
        name=data_name,
        team=team,
        user_email=user_email,
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
        name=data_name,
        team=team,
        user_email=user_email,
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


def test_datacard_split_fail(db_registries: Dict[str, CardRegistry], test_df: pd.DataFrame):
    data_name = "test_df"
    team = "mlops"
    user_email = "mlops.com"

    registry: CardRegistry = db_registries["data"]

    data_card = DataCard(
        data=test_df,
        name=data_name,
        team=team,
        user_email=user_email,
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
