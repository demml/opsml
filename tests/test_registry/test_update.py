from pathlib import Path
from typing import Tuple

import pytest

from opsml.cards import (
    ModelCard,
)
from opsml.data import (
    DataInterface,
)
from opsml.model import ModelInterface
from opsml.registry import CardRegistries


def test_update_move_savepaths(
    db_registries: CardRegistries,
    sklearn_pipeline: Tuple[ModelInterface, DataInterface],
) -> None:
    model_registry = db_registries.model
    model, _ = sklearn_pipeline

    modelcard = ModelCard(
        interface=model,
        name="model1",
        repository="opsml",
        contact="opsml",
        datacard_uid=None,
    )
    model_registry.register_card(card=modelcard)

    assert Path(modelcard.uri).exists()

    # update the model card
    previous_uri = modelcard.uri
    modelcard = model_registry.load_card(uid=modelcard.uid)
    modelcard.load_model()

    modelcard.version = "1.0.1"
    model_registry.update_card(card=modelcard)

    assert previous_uri != modelcard.uri
    assert Path(modelcard.uri).exists()
    assert not Path(previous_uri).exists()

    # load the model card
    loaded_modelcard = model_registry.load_card(uid=modelcard.uid)

    assert loaded_modelcard.version == "1.0.1"
    assert loaded_modelcard.uri == modelcard.uri
    assert loaded_modelcard.name == modelcard.name
    assert loaded_modelcard.repository == modelcard.repository


def test_update_fail(
    db_registries: CardRegistries,
    sklearn_pipeline: Tuple[ModelInterface, DataInterface],
) -> None:
    model_registry = db_registries.model
    model, _ = sklearn_pipeline

    modelcard = ModelCard(
        interface=model,
        name="model1",
        repository="opsml",
        contact="opsml",
        datacard_uid=None,
    )
    with pytest.raises(AssertionError) as e:
        model_registry.update_card(card=modelcard)
    assert "Card does not exist in registry. Please use register card first" in str(e.value)

    # registry card
    model_registry.register_card(card=modelcard)

    # register 2nd card
    modelcard = ModelCard(
        interface=model,
        name="model2",
        repository="opsml",
        contact="opsml",
        datacard_uid=None,
    )
    # registry card
    model_registry.register_card(card=modelcard)

    # update second card with first card's name
    modelcard.name = "model1"
    with pytest.raises(ValueError) as e:
        model_registry.update_card(card=modelcard)
    assert "Card for opsml/model1/1.0.0 already exists with a different uid" in str(e.value)
