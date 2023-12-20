import os
import sys

import pytest
from sklearn import linear_model
from sklearn.pipeline import Pipeline

from opsml.registry import CardRegistries
from opsml.registry.cards import DataCard, ModelCard, RunCard


@pytest.mark.skipif(sys.platform == "win32", reason="No wn_32 test")
def test_delete_data_model(
    db_registries: CardRegistries,
    sklearn_pipeline: Pipeline,
):
    # create data card
    data_registry = db_registries.data
    model, data = sklearn_pipeline
    data_card = DataCard(
        data=data,
        name="pipeline_data",
        team="mlops",
        user_email="mlops.com",
    )
    data_registry.register_card(card=data_card)
    cards = data_registry.list_cards(name="pipeline_data", team="mlops")

    # assert card and artifacts exist
    assert len(cards) == 1

    assert os.path.exists(
        data_registry._registry.storage_client.build_absolute_path(data_card.metadata.uris.data_uri),
    )
    assert os.path.exists(
        data_registry._registry.storage_client.build_absolute_path(data_card.metadata.uris.datacard_uri),
    )

    model_card = ModelCard(
        trained_model=model,
        sample_input_data=data[0:1],
        name="pipeline_model",
        team="mlops",
        user_email="mlops.com",
        datacard_uid=data_card.uid,
        to_onnx=True,
    )

    model_registry = db_registries.model
    model_registry.register_card(card=model_card)
    cards = model_registry.list_cards(name="pipeline_model", team="mlops")
    assert len(cards) == 1

    assert os.path.exists(
        model_registry._registry.storage_client.build_absolute_path(model_card.metadata.uris.trained_model_uri),
    )
    assert os.path.exists(
        model_registry._registry.storage_client.build_absolute_path(model_card.metadata.uris.model_metadata_uri),
    )
    assert os.path.exists(
        model_registry._registry.storage_client.build_absolute_path(model_card.metadata.uris.onnx_model_uri),
    )
    assert os.path.exists(
        model_registry._registry.storage_client.build_absolute_path(model_card.metadata.uris.sample_data_uri),
    )
    assert os.path.exists(
        model_registry._registry.storage_client.build_absolute_path(model_card.metadata.uris.modelcard_uri),
    )

    # delete model card
    model_registry.delete_card(card=model_card)
    cards = model_registry.list_cards(name="pipeline_model", team="mlops")
    assert len(cards) == 0

    assert not os.path.exists(
        model_registry._registry.storage_client.build_absolute_path(model_card.metadata.uris.trained_model_uri),
    )
    assert not os.path.exists(
        model_registry._registry.storage_client.build_absolute_path(model_card.metadata.uris.model_metadata_uri),
    )
    assert not os.path.exists(
        model_registry._registry.storage_client.build_absolute_path(model_card.metadata.uris.onnx_model_uri),
    )
    assert not os.path.exists(
        model_registry._registry.storage_client.build_absolute_path(model_card.metadata.uris.sample_data_uri),
    )
    assert not os.path.exists(
        model_registry._registry.storage_client.build_absolute_path(model_card.metadata.uris.modelcard_uri),
    )

    # delete datacard
    data_registry.delete_card(card=data_card)
    cards = data_registry.list_cards(name="pipeline_data", team="mlops")
    assert len(cards) == 0

    assert not os.path.exists(
        data_registry._registry.storage_client.build_absolute_path(data_card.metadata.uris.data_uri),
    )
    assert not os.path.exists(
        data_registry._registry.storage_client.build_absolute_path(data_card.metadata.uris.datacard_uri),
    )


@pytest.mark.skipif(sys.platform == "win32", reason="No wn_32 test")
def test_delete_runcard(
    linear_regression: linear_model.LinearRegression,
    db_registries: CardRegistries,
):
    registry = db_registries.run
    run = RunCard(
        name="test_run",
        team="mlops",
        user_email="mlops.com",
        datacard_uids=["test_uid"],
    )
    run.log_metric("test_metric", 10)
    run.log_metrics({"test_metric2": 20})
    assert run.get_metric("test_metric").value == 10
    assert run.get_metric("test_metric2").value == 20

    # save artifacts
    model, _ = linear_regression
    run.log_artifact("reg_model", model)
    assert run.artifacts.get("reg_model").__class__.__name__ == "LinearRegression"
    registry.register_card(card=run)

    registry.delete_card(card=run)
    cards = registry.list_cards(name="test_run", team="mlops")
    assert len(cards) == 0

    assert not os.path.exists(
        db_registries.run._registry.storage_client.build_absolute_path(run.runcard_uri),
    )
