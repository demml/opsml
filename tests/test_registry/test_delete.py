import sys
from pathlib import Path
from typing import Tuple

import pytest

from opsml.cards import DataCard, ModelCard, RunCard
from opsml.data import PandasData
from opsml.model import SklearnModel
from opsml.registry import CardRegistries, CardRegistry
from opsml.storage import client
from opsml.types import SaveName, Suffix


@pytest.mark.skipif(sys.platform == "win32", reason="No wn_32 test")
def test_delete_data_model(
    db_registries: CardRegistries,
    sklearn_pipeline: Tuple[SklearnModel, PandasData],
) -> None:
    # create data card
    data_registry: CardRegistry = db_registries.data
    model, data = sklearn_pipeline
    datacard = DataCard(
        interface=data,
        name="pipeline_data",
        repository="mlops",
        contact="mlops.com",
    )
    data_registry.register_card(card=datacard)
    cards = data_registry.list_cards(name="pipeline_data", repository="mlops")

    # assert card and artifacts exist
    assert len(cards) == 1
    assert Path(datacard.uri, SaveName.CARD.value).with_suffix(Suffix.JSON.value).exists()

    modelcard = ModelCard(
        interface=model,
        name="pipeline_model",
        repository="mlops",
        contact="mlops.com",
        datacard_uid=datacard.uid,
        to_onnx=True,
    )

    model_registry: CardRegistry = db_registries.model
    model_registry.register_card(card=modelcard)
    cards = model_registry.list_cards(name="pipeline_model", repository="mlops")
    assert len(cards) == 1

    assert Path(modelcard.uri, SaveName.TRAINED_MODEL.value).with_suffix(Suffix.JOBLIB.value).exists()
    assert Path(modelcard.uri, SaveName.SAMPLE_MODEL_DATA.value).with_suffix(Suffix.JOBLIB.value).exists()
    assert Path(modelcard.uri, SaveName.MODEL_METADATA.value).with_suffix(Suffix.JSON.value).exists()
    assert Path(modelcard.uri, SaveName.CARD.value).with_suffix(Suffix.JSON.value).exists()

    # delete model card
    model_registry.delete_card(card=modelcard)
    cards = model_registry.list_cards(name="pipeline_model", repository="mlops")
    assert len(cards) == 0

    assert not Path(modelcard.uri, SaveName.TRAINED_MODEL.value).with_suffix(Suffix.JOBLIB.value).exists()
    assert not Path(modelcard.uri, SaveName.SAMPLE_MODEL_DATA.value).with_suffix(Suffix.JOBLIB.value).exists()
    assert not Path(modelcard.uri, SaveName.MODEL_METADATA.value).with_suffix(Suffix.JSON.value).exists()
    assert not Path(modelcard.uri, SaveName.CARD.value).with_suffix(Suffix.JSON.value).exists()

    # delete datacard
    data_registry.delete_card(card=datacard)
    cards = data_registry.list_cards(name="pipeline_data", repository="mlops")
    assert len(cards) == 0

    assert not Path(datacard.uri, SaveName.CARD.value).with_suffix(Suffix.JSON.value).exists()


@pytest.mark.skipif(sys.platform == "win32", reason="No wn_32 test")
def test_delete_runcard(db_registries: CardRegistries) -> None:
    registry = db_registries.run
    run = RunCard(
        name="test_run",
        repository="mlops",
        contact="mlops.com",
        datacard_uids=["test_uid"],
    )
    run.log_metric("test_metric", 10)
    run.log_metrics({"test_metric2": 20})
    assert run.get_metric("test_metric").value == 10  # type: ignore
    assert run.get_metric("test_metric2").value == 20  # type: ignore

    registry.register_card(card=run)
    assert Path(run.uri, SaveName.CARD.value).with_suffix(Suffix.JSON.value).exists()

    registry.delete_card(card=run)
    cards = registry.list_cards(name="test_run", repository="mlops")
    assert len(cards) == 0

    assert not Path(run.uri, SaveName.CARD.value).with_suffix(Suffix.JSON.value).exists()


@pytest.mark.skipif(sys.platform == "win32", reason="No wn_32 test")
def test_delete_data_model_api(
    api_storage_client: client.StorageClientBase,
    sklearn_pipeline: Tuple[SklearnModel, PandasData],
    api_registries: CardRegistries,
) -> None:
    # create data card
    data_registry: CardRegistry = api_registries.data
    model, data = sklearn_pipeline
    datacard = DataCard(
        interface=data,
        name="pipeline_data",
        repository="mlops",
        contact="mlops.com",
    )
    data_registry.register_card(card=datacard)
    cards = data_registry.list_cards(name="pipeline_data", repository="mlops")

    # assert card and artifacts exist
    assert len(cards) == 1
    assert api_storage_client.exists(Path(datacard.uri, SaveName.CARD.value).with_suffix(Suffix.JSON.value))

    modelcard = ModelCard(
        interface=model,
        name="pipeline_model",
        repository="mlops",
        contact="mlops.com",
        datacard_uid=datacard.uid,
        to_onnx=True,
    )

    model_registry: CardRegistry = api_registries.model
    model_registry.register_card(card=modelcard)
    cards = model_registry.list_cards(name="pipeline_model", repository="mlops")
    assert len(cards) == 1

    assert api_storage_client.exists(Path(modelcard.uri, SaveName.TRAINED_MODEL.value).with_suffix(Suffix.JOBLIB.value))
    assert api_storage_client.exists(
        Path(modelcard.uri, SaveName.SAMPLE_MODEL_DATA.value).with_suffix(Suffix.JOBLIB.value)
    )
    assert api_storage_client.exists(Path(modelcard.uri, SaveName.MODEL_METADATA.value).with_suffix(Suffix.JSON.value))
    assert api_storage_client.exists(Path(modelcard.uri, SaveName.CARD.value).with_suffix(Suffix.JSON.value))

    # delete model card
    model_registry.delete_card(card=modelcard)
    cards = model_registry.list_cards(name="pipeline_model", repository="mlops")
    assert len(cards) == 0

    assert not api_storage_client.exists(
        Path(modelcard.uri, SaveName.TRAINED_MODEL.value).with_suffix(Suffix.JOBLIB.value)
    )
    assert not api_storage_client.exists(
        Path(modelcard.uri, SaveName.SAMPLE_MODEL_DATA.value).with_suffix(Suffix.JOBLIB.value)
    )
    assert not api_storage_client.exists(
        Path(modelcard.uri, SaveName.MODEL_METADATA.value).with_suffix(Suffix.JSON.value)
    )
    assert not api_storage_client.exists(Path(modelcard.uri, SaveName.CARD.value).with_suffix(Suffix.JSON.value))

    # delete datacard
    data_registry.delete_card(card=datacard)
    cards = data_registry.list_cards(name="pipeline_data", repository="mlops")
    assert len(cards) == 0

    assert not api_storage_client.exists(Path(datacard.uri, SaveName.CARD.value).with_suffix(Suffix.JSON.value))

    # this will create a soft failure in the files path since the file is already deleted
    data_registry.delete_card(card=datacard)
