import pandas as pd
import pytest
from pytest_lazyfixture import lazy_fixture

from opsml_data.registry.data_card import DataCard
from opsml_data.registry.data_registry import DataRegistry


@pytest.mark.parametrize(
    "test_data",
    [
        lazy_fixture("test_array"),
        lazy_fixture("test_df"),
        lazy_fixture("test_arrow_table"),
    ],
)
def test_register_data(setup_database, test_data, storage_client):

    registry: DataRegistry = setup_database

    data_card = DataCard(
        data=test_data,
        data_name="test_df",
        team="mlops",
        user_email="mlops.com",
    )

    registry.register(data_card=data_card)

    storage_client.delete_object_from_url(gcs_uri=data_card.data_uri)


@pytest.mark.parametrize(
    "test_data",
    [
        lazy_fixture("test_df"),
    ],
)
def test_list_data(setup_database, test_data):

    registry: DataRegistry = setup_database

    data_card = DataCard(
        data=test_data,
        data_name="test_df",
        team="mlops",
        user_email="mlops.com",
    )

    metadata = registry.register(data_card=data_card)

    df = registry.list_data(data_name="test_df", team="spsms")
    assert isinstance(df, pd.DataFrame)

    # test without team
    df = registry.list_data(data_name="test_df")
    assert isinstance(df, pd.DataFrame)

    # test without any
    df = registry.list_data()
    assert isinstance(df, pd.DataFrame)


@pytest.mark.parametrize(
    "test_data",
    [
        lazy_fixture("test_df"),
    ],
)
def test_data_card_splits(test_data):

    # registry: DataRegistry = setup_database

    data_split = [
        {"label": "train", "col": "year", "val": 2020},
        {"label": "test", "col": "year", "val": 2021},
    ]

    data_card = DataCard(
        data=test_data,
        data_name="test_df",
        team="mlops",
        user_email="mlops.com",
        data_splits=data_split,
    )

    assert data_card.data_splits.train.col == "year"
    assert data_card.data_splits.test.val == 2021

    data_split = {
        "train": {"start": 0, "stop": 2},
        "test": {"start": 3, "stop": 4},
    }

    data_card = DataCard(
        data=test_data,
        data_name="test_df",
        team="mlops",
        user_email="mlops.com",
        data_splits=data_split,
    )

    assert data_card.data_splits.train.start == 0
    assert data_card.data_splits.test.stop == 4

    # metadata = registry.register(data_card=data_card)


@pytest.mark.parametrize(
    "test_data",
    [
        lazy_fixture("test_df"),
    ],
)
def test_load_data_card(setup_database, test_data, storage_client):
    data_name = "test_df"
    team = "mlops"
    user_email = "mlops.com"

    registry: DataRegistry = setup_database

    data_split = {
        "train": {"col": "year", "val": 2020},
        "test": {"col": "year", "val": 2021},
    }

    data_card = DataCard(
        data=test_data,
        data_name=data_name,
        team=team,
        user_email=user_email,
        data_splits=data_split,
    )

    registry.register(data_card=data_card)
    loaded_data = registry.load(data_name=data_name, team=team, version=data_card.version)

    # update
    loaded_data.version = 100

    registry.update(data_card=loaded_data)
    storage_client.delete_object_from_url(gcs_uri=loaded_data.data_uri)

    df = registry.list_data(data_name=data_name, team=team, version=100)

    assert df["version"].to_numpy()[0] == 100
