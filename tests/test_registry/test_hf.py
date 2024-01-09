import uuid
from pathlib import Path
from typing import cast

from lightning import LightningDataModule

from opsml.cards import Description, ModelCard, ModelCardMetadata
from opsml.model import HuggingFaceModel, SklearnModel, LightGBMModel, PyTorchModel, LightningModel, TensorFlowModel
from opsml.storage.card_loader import CardLoader
from opsml.storage.card_saver import save_card_artifacts
from opsml.types import RegistryType, SaveName, CommonKwargs
from transformers import Pipeline

def test_save_tensorflow_multi_input_modelcard(
    multi_input_tf_example: TensorFlowModel,
):
    model: TensorFlowModel = multi_input_tf_example

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
    assert Path(modelcard.uri, SaveName.TRAINED_MODEL.value).exists()
    assert Path(modelcard.uri, SaveName.SAMPLE_MODEL_DATA.value).with_suffix(".joblib").exists()
    assert Path(modelcard.uri, SaveName.ONNX_MODEL.value).with_suffix(".onnx").exists()
    assert Path(modelcard.uri, SaveName.CARD.value).with_suffix(".joblib").exists()

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

    #
    loaded_card.load_model()

    assert type(loaded_card.interface.model) == type(modelcard.interface.model)

    #
    loaded_card.load_onnx_model()
    assert loaded_card.interface.onnx_model is not None
    assert loaded_card.interface.onnx_model.sess is not None