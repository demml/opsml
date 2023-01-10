import pandas as pd
import pytest
from pytest_lazyfixture import lazy_fixture

from opsml_artifacts.registry.cards.card import DataCard
from opsml_artifacts.registry.cards.registry import CardRegistry
from opsml_artifacts.registry.cards.card import ModelCardCreator


@pytest.mark.parametrize(
    "data_splits, test_data",
    [
        (lazy_fixture("test_split_array"), lazy_fixture("test_array")),
        (lazy_fixture("test_split_array"), lazy_fixture("test_df")),
        (lazy_fixture("test_split_array"), lazy_fixture("test_arrow_table")),
    ],
)
def test_register_data(setup_data_registry, test_data, storage_client, data_splits):

    # create data card
    registry: CardRegistry = setup_data_registry
    data_card = DataCard(
        data=test_data,
        name="test_df",
        team="mlops",
        user_email="mlops.com",
        data_splits=data_splits,
    )

    registry.register_card(card=data_card)

    df = registry.list_cards(name=data_card.name, team=data_card.team)
    assert isinstance(df, pd.DataFrame)

    df = registry.list_cards(name=data_card.name)
    assert isinstance(df, pd.DataFrame)

    df = registry.list_cards()
    assert isinstance(df, pd.DataFrame)

    storage_client.delete_object_from_url(gcs_uri=data_card.data_uri)


def test_register_base_model(setup_model_registry, model_list, storage_client):

    registry: CardRegistry = setup_model_registry
    models, data = model_list

    for model in models:
        model_creator = ModelCardCreator(model=model, input_data=data)
        model_card = model_creator.create_model_card(
            model_name="test_model",
            team="mlops",
            user_email="test_email",
            registered_data_uid="test_uid",
        )

        registry.register_card(card=model_card)
        storage_client.delete_object_from_url(gcs_uri=model_card.model_uri)


def test_register_pipeline_model(setup_model_registry, sklearn_pipeline, storage_client):

    registry: CardRegistry = setup_model_registry
    model, data = sklearn_pipeline

    model_creator = ModelCardCreator(model=model, input_data=data)
    model_card = model_creator.create_model_card(
        model_name="test_model",
        team="mlops",
        user_email="test_email",
        registered_data_uid="test_uid",
    )

    registry.register_card(card=model_card)
    registry.list_cards(name=model_card.name, team=model_card.team, version=model_card.version)
    storage_client.delete_object_from_url(gcs_uri=model_card.model_uri)


@pytest.mark.parametrize("test_data", [lazy_fixture("test_df")])
def test_data_card_splits(test_data):

    data_split = [
        {"label": "train", "column": "year", "column_value": 2020},
        {"label": "test", "column": "year", "column_value": 2021},
    ]

    data_card = DataCard(
        data=test_data,
        name="test_df",
        team="mlops",
        user_email="mlops.com",
        data_splits=data_split,
    )

    assert data_card.data_splits[0]["column"] == "year"
    assert data_card.data_splits[0]["column_value"] == 2020

    data_split = [
        {"label": "train", "start": 0, "stop": 2},
        {"label": "test", "start": 3, "stop": 4},
    ]

    data_card = DataCard(
        data=test_data,
        name="test_df",
        team="mlops",
        user_email="mlops.com",
        data_splits=data_split,
    )

    assert data_card.data_splits[0]["start"] == 0
    assert data_card.data_splits[0]["stop"] == 2


@pytest.mark.parametrize("test_data", [lazy_fixture("test_df")])
def test_load_data_card(setup_data_registry, test_data, storage_client):
    data_name = "test_df"
    team = "mlops"
    user_email = "mlops.com"

    registry: CardRegistry = setup_data_registry

    data_split = [
        {"label": "train", "column": "year", "column_value": 2020},
        {"label": "test", "column": "year", "column_value": 2021},
    ]

    data_card = DataCard(
        data=test_data,
        name=data_name,
        team=team,
        user_email=user_email,
        data_splits=data_split,
    )

    registry.register_card(card=data_card)
    loaded_data = registry.load_card(name=data_name, team=team, version=data_card.version)

    # update
    loaded_data.version = 100

    registry.update_card(card=loaded_data)
    storage_client.delete_object_from_url(gcs_uri=loaded_data.data_uri)

    df = registry.list_cards(name=data_name, team=team, version=100)

    assert df["version"].to_numpy()[0] == 100
