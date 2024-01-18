import sys
from pathlib import Path
from typing import Tuple

import pytest

from opsml.cards import DataCard, ModelCard
from opsml.registry import CardRegistries
from opsml.storage import client
from opsml.types import SaveName
from opsml.types.extra import Suffix


@pytest.mark.skipif(sys.platform == "win32", reason="No wn_32 test")
def test_delete_data_model(
    api_registries: CardRegistries,
    populate_model_data_for_api: Tuple[ModelCard, DataCard],
    api_storage_client: client.StorageClient,
):
    modelcard, datacard = populate_model_data_for_api

    data_registry = api_registries.data
    model_registry = api_registries.model

    assert api_storage_client.exists(Path(datacard.uri, SaveName.CARD.value).with_suffix(Suffix.JOBLIB.value))
    assert api_storage_client.exists(
        Path(datacard.uri, SaveName.DATA.value).with_suffix(datacard.interface.data_suffix)
    )

    # assert card and artifacts exist
    cards = data_registry.list_cards(name=datacard.name, repository=datacard.repository)
    assert len(cards) == 1

    cards = model_registry.list_cards(name=modelcard.name, repository=modelcard.repository)
    assert len(cards) == 1

    assert api_storage_client.exists(
        Path(modelcard.uri, SaveName.TRAINED_MODEL.value).with_suffix(modelcard.interface.model_suffix)
    )
    assert api_storage_client.exists(Path(modelcard.uri, SaveName.MODEL_METADATA.value).with_suffix(Suffix.JSON.value))
    assert api_storage_client.exists(Path(modelcard.uri, SaveName.ONNX_MODEL.value).with_suffix(Suffix.ONNX.value))
    assert api_storage_client.exists(
        Path(modelcard.uri, SaveName.SAMPLE_MODEL_DATA.value).with_suffix(Suffix.JOBLIB.value)
    )
    assert api_storage_client.exists(Path(modelcard.uri, SaveName.CARD.value).with_suffix(Suffix.JOBLIB.value))

    # delete model card
    model_registry.delete_card(card=modelcard)
    cards = model_registry.list_cards(name=modelcard.name, repository=modelcard.repository)
    assert len(cards) == 0

    assert not api_storage_client.exists(
        Path(modelcard.uri, SaveName.TRAINED_MODEL.value).with_suffix(modelcard.interface.model_suffix)
    )
    assert not api_storage_client.exists(
        Path(modelcard.uri, SaveName.MODEL_METADATA.value).with_suffix(Suffix.JSON.value)
    )
    assert not api_storage_client.exists(Path(modelcard.uri, SaveName.ONNX_MODEL.value).with_suffix(Suffix.ONNX.value))
    assert not api_storage_client.exists(
        Path(modelcard.uri, SaveName.SAMPLE_MODEL_DATA.value).with_suffix(Suffix.JOBLIB.value)
    )
    assert not api_storage_client.exists(Path(modelcard.uri, SaveName.CARD.value).with_suffix(Suffix.JOBLIB.value))

    # delete datacard
    data_registry.delete_card(card=datacard)
    cards = data_registry.list_cards(name=datacard.name, repository=datacard.repository)
    assert len(cards) == 0

    assert not api_storage_client.exists(Path(datacard.uri, SaveName.CARD.value).with_suffix(Suffix.JOBLIB.value))
    assert not api_storage_client.exists(
        Path(datacard.uri, SaveName.DATA.value).with_suffix(datacard.interface.data_suffix)
    )
