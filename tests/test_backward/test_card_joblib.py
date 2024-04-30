from pathlib import Path
from typing import Tuple

import joblib

from opsml import CardRegistries, DataInterface, ModelCard, ModelInterface
from opsml.storage import client
from opsml.storage.card_loader import CardLoader
from opsml.types import RegistryType, SaveName, Suffix


def test_card_joblib_compatible(
    db_registries: CardRegistries,
    sklearn_pipeline: Tuple[ModelInterface, DataInterface],
) -> None:
    # create data card
    data_registry = db_registries.data
    model, _ = sklearn_pipeline

    # test onnx
    modelcard = ModelCard(
        interface=model,
        name="pipeline_model",
        repository="mlops",
        contact="mlops.com",
    )

    model_registry = db_registries.model
    model_registry.register_card(card=modelcard)

    # manually save modelcard
    dumped_model = modelcard.model_dump(
        exclude={
            "interface": {"model", "preprocessor", "sample_data", "onnx_model", "feature_extractor", "tokenizer"},
        }
    )

    # create joblib version of card
    save_path = Path(modelcard.uri / SaveName.CARD.value).with_suffix(Suffix.JOBLIB.value)
    joblib.dump(dumped_model, save_path)

    # delete json path
    client.storage_client.rm(Path(modelcard.uri / SaveName.CARD.value).with_suffix(Suffix.JSON.value))

    # assert json is deleted
    assert not client.storage_client.exists(Path(modelcard.uri / SaveName.CARD.value).with_suffix(Suffix.JSON.value))

    loader = CardLoader(registry_type=RegistryType.MODEL, card=modelcard)

    loader._load_card_from_storage(modelcard.uri)
