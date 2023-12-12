import sys
from os import path
from typing import Dict

import pytest
from sklearn import linear_model
from sklearn.pipeline import Pipeline

from opsml.registry.cards import DataCard, ModelCard, RunCard
from opsml.registry.sql.registry import CardRegistry


@pytest.mark.skipif(sys.platform == "win32", reason="No wn_32 test")
def test_delete_data_model(
    db_registries: Dict[str, CardRegistry],
    sklearn_pipeline: Pipeline,
):
    # create data card
    data_registry: CardRegistry = db_registries["data"]
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
    data_filepath = data_card.metadata.uris.data_uri
    datacard_filepath = data_card.metadata.uris.datacard_uri
    assert path.exists(data_filepath)
    assert path.exists(datacard_filepath)

    model_card = ModelCard(
        trained_model=model,
        sample_input_data=data[0:1],
        name="pipeline_model",
        team="mlops",
        user_email="mlops.com",
        datacard_uid=data_card.uid,
        to_onnx=True,
    )

    model_registry: CardRegistry = db_registries["model"]
    model_registry.register_card(card=model_card)
    cards = model_registry.list_cards(name="pipeline_model", team="mlops")
    assert len(cards) == 1

    trained_model_path = model_card.metadata.uris.trained_model_uri
    metadata_path = model_card.metadata.uris.model_metadata_uri
    onnx_model_path = model_card.metadata.uris.onnx_model_uri
    sample_data_path = model_card.metadata.uris.sample_data_uri
    modelcard_path = model_card.metadata.uris.modelcard_uri

    assert path.exists(trained_model_path)
    assert path.exists(metadata_path)
    assert path.exists(onnx_model_path)
    assert path.exists(sample_data_path)
    assert path.exists(modelcard_path)

    # delete model card
    model_registry.delete_card(card=model_card)
    cards = model_registry.list_cards(name="pipeline_model", team="mlops")
    assert len(cards) == 0

    # check artifacts have been deleted
    assert not path.exists(trained_model_path)
    assert not path.exists(metadata_path)
    assert not path.exists(onnx_model_path)
    assert not path.exists(sample_data_path)
    assert not path.exists(modelcard_path)

    # delete datacard
    data_registry.delete_card(card=data_card)
    cards = data_registry.list_cards(name="pipeline_data", team="mlops")
    assert len(cards) == 0

    # check artifacts have been deleted
    assert not path.exists(data_filepath)
    assert not path.exists(datacard_filepath)


@pytest.mark.skipif(sys.platform == "win32", reason="No wn_32 test")
def test_delete_runcard(
    linear_regression: linear_model.LinearRegression,
    db_registries: Dict[str, CardRegistry],
):
    registry: CardRegistry = db_registries["run"]
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

    # check artifacts have been deleted
    assert not path.exists(run.runcard_uri)
