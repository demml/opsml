import uuid
from pathlib import Path
from typing import cast

from opsml.cards import Description, ModelCard, ModelCardMetadata
from opsml.model import HuggingFaceModel
from opsml.storage.card_loader import CardLoader
from opsml.storage.card_saver import save_card_artifacts
from opsml.types import RegistryType, SaveName
from transformers import Pipeline

def test_save_huggingface_vit_pipeline_modelcard(huggingface_vit_pipeline: HuggingFaceModel):
    model, _ = huggingface_vit_pipeline

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
    assert Path(modelcard.uri, SaveName.FEATURE_EXTRACTOR.value).exists()
    assert not Path(modelcard.uri, SaveName.TOKENIZER.value).exists()
    assert Path(modelcard.uri, SaveName.SAMPLE_MODEL_DATA.value).with_suffix(".joblib").exists()
    assert Path(modelcard.uri, SaveName.ONNX_MODEL.value).exists()
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
    assert loaded_card.interface.model is None
    assert loaded_card.interface.feature_extractor is None
        
    # attempt to load onnx model before loading model
    loaded_card.load_onnx_model()
    assert loaded_card.onnx_model is not None
    assert loaded_card.onnx_model.sess is not None
    assert isinstance(loaded_card.onnx_model.sess, Pipeline)
    
    # loading onnx model should also load preprocessors
    assert type(loaded_card.preprocessor) == type(modelcard.interface.feature_extractor)
    assert loaded_card.interface.model is None # model should still be none


    loaded_card.load_model()
    assert type(loaded_card.model) == type(modelcard.interface.model)
    assert isinstance(loaded_card.model, Pipeline)
    
    metadata = loaded_card.model_metadata
    
    assert getattr(metadata, "feature_extractor_uri", None) is not None
    assert getattr(metadata, "feature_extractor_name", None) is not None
    a
