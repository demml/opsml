
import sys
import uuid
from pathlib import Path
from typing import cast

import pytest
from transformers import Pipeline

from opsml.cards import Description, ModelCard, ModelCardMetadata
from opsml.model import (
    HuggingFaceModel,
    LightGBMModel,
    LightningModel,
    PyTorchModel,
    SklearnModel,
    TensorFlowModel,
    CatBoostModel
)
from opsml.storage.card_loader import CardLoader
from opsml.storage.card_saver import save_card_artifacts
from opsml.types import CommonKwargs, RegistryType, SaveName, Suffix

DARWIN_EXCLUDE = sys.platform == "darwin" and sys.version_info < (3, 11)
WINDOWS_EXCLUDE = sys.platform == "win32"

EXCLUDE = bool(DARWIN_EXCLUDE or WINDOWS_EXCLUDE)


def test_save_catboost_modelcard(catboost_regressor: CatBoostModel):
    model: CatBoostModel = catboost_regressor
    modelcard = ModelCard(
        interface=model,
        name="test_model",
        team="mlops",
        user_email="test_email",
        datacard_uid=uuid.uuid4().hex,
        to_onnx=True,
        version="0.0.1",
        uid=uuid.uuid4().hex,
        metadata=ModelCardMetadata(
            description=Description(summary="test summary"),
        ),
    )

    save_card_artifacts(modelcard)

    # check paths exist on server
    assert Path(modelcard.uri, SaveName.TRAINED_MODEL.value).with_suffix(Suffix.CATBOOST.value).exists()
    assert Path(modelcard.uri, SaveName.PREPROCESSOR.value).with_suffix(Suffix.JOBLIB.value).exists()
    assert Path(modelcard.uri, SaveName.SAMPLE_MODEL_DATA.value).with_suffix(Suffix.JOBLIB.value).exists()
    assert Path(modelcard.uri, SaveName.ONNX_MODEL.value).with_suffix(Suffix.ONNX.value).exists()
    assert Path(modelcard.uri, SaveName.CARD.value).with_suffix(Suffix.JOBLIB.value).exists()

    # load objects
    loader = CardLoader(
        card_args={
            "name": modelcard.name,
            "team": modelcard.team,
            "version": modelcard.version,
        },
        registry_type=RegistryType.MODEL,
    )

    loaded_card = cast(ModelCard, loader.load_card())
    assert isinstance(loaded_card, ModelCard)

    loaded_card.load_model()
    assert type(loaded_card.interface.model) == type(modelcard.interface.model)

    loaded_card.load_onnx_model()
    assert loaded_card.interface.onnx_model is not None
    assert loaded_card.interface.onnx_model.sess is not None
