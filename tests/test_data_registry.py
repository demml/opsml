from opsml_data.registry.data_registry import DataRegistry
from opsml_data.registry.data_card import DataCard
import pytest
from pytest_lazyfixture import lazy_fixture
import pandas as pd


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

    metadata = registry.register(data_card=data_card)

    storage_client.delete_object_from_url(gcs_uri=metadata.data_uri)


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


def test_load_data_card(setup_database, test_data):

    registry: DataRegistry = setup_database

    data_card = DataCard(
        data=test_data,
        data_name="test_df",
        team="mlops",
        user_email="mlops.com",
    )

    metadata = registry.register(data_card=data_card)
