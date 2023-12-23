import os
import sys
from typing import Tuple

import pandas as pd
import pytest
from sklearn import pipeline

from opsml.registry import CardRegistries, DataCard, ModelCard


@pytest.mark.skipif(sys.platform == "win32", reason="No wn_32 test")
def test_delete_data_model(
    api_registries: CardRegistries,
    sklearn_pipeline: Tuple[pipeline.Pipeline, pd.DataFrame],
):
    model, data = sklearn_pipeline
    # create data card
    data_registry = api_registries.data

    data_card = DataCard(
        data=data,
        name="pipeline_data",
        team="mlops",
        user_email="mlops.com",
    )
    data_registry.register_card(card=data_card)

    assert os.path.exists(
        data_registry._registry.storage_client.build_absolute_path(data_card.metadata.uris.data_uri),
    )
    assert os.path.exists(
        data_registry._registry.storage_client.build_absolute_path(data_card.metadata.uris.datacard_uri),
    )

    # assert card and artifacts exist
    cards = data_registry.list_cards(name="pipeline_data", team="mlops")
    assert len(cards) == 1

    model_card = ModelCard(
        trained_model=model,
        sample_input_data=data[0:1],
        name="pipeline_model",
        team="mlops",
        user_email="mlops.com",
        tags={"id": "model1"},
        datacard_uid=data_card.uid,
        to_onnx=True,
    )

    model_registry = api_registries.model
    model_registry.register_card(model_card)

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
