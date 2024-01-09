import uuid
from pathlib import Path
from typing import cast

from opsml.cards import Description, ModelCard, ModelCardMetadata
from opsml.model import (
    HuggingFaceModel,
    LightGBMModel,
    LightningModel,
    PyTorchModel,
    SklearnModel,
    TensorFlowModel,
)
from opsml.storage.card_loader import CardLoader
from opsml.storage.card_saver import save_card_artifacts
from opsml.types import CommonKwargs, RegistryType, SaveName
from transformers import Pipeline

def test_save_huggingface_modelcard(huggingface_torch_distilbert: HuggingFaceModel):
    model: HuggingFaceModel = huggingface_torch_distilbert

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
    assert Path(modelcard.uri, SaveName.PREPROCESSOR.value).exists()
    assert Path(modelcard.uri, SaveName.SAMPLE_MODEL_DATA.value).with_suffix(".joblib").exists()
    assert Path(modelcard.uri, SaveName.ONNX_MODEL.value).exists()
    assert Path(modelcard.uri, SaveName.QUANTIZED_MODEL.value).exists()
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

    loaded_card.load_model()
    assert type(loaded_card.interface.model) == type(modelcard.interface.model)
    assert type(loaded_card.interface.preprocessor) == type(modelcard.interface.preprocessor)

    #
    loaded_card.load_onnx_model()
    assert loaded_card.interface.onnx_model is not None
    assert loaded_card.interface.onnx_model.sess is not None

    loaded_card.load_onnx_model(load_quantized=True)
    assert loaded_card.interface.onnx_model is not None
    assert loaded_card.interface.onnx_model.sess is not None


def test_save_huggingface_pipeline_modelcard(huggingface_text_classification_pipeline: HuggingFaceModel):
    model: HuggingFaceModel = huggingface_text_classification_pipeline

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
    assert Path(modelcard.uri, SaveName.PREPROCESSOR.value).exists()
    assert Path(modelcard.uri, SaveName.SAMPLE_MODEL_DATA.value).with_suffix(".joblib").exists()
    assert Path(modelcard.uri, SaveName.ONNX_MODEL.value).exists()
    assert Path(modelcard.uri, SaveName.QUANTIZED_MODEL.value).exists()
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

    loaded_card.load_model()
    assert type(loaded_card.interface.model) == type(modelcard.interface.model)
    assert type(loaded_card.interface.preprocessor) == type(modelcard.interface.preprocessor)

    #
    loaded_card.load_onnx_model()
    assert loaded_card.interface.onnx_model is not None
    assert loaded_card.interface.onnx_model.sess is not None

    loaded_card.load_onnx_model(load_quantized=True)
    assert loaded_card.interface.onnx_model is not None
    assert loaded_card.interface.onnx_model.sess is not None


def test_save_sklearn_modelcard(random_forest_classifier: SklearnModel):
    model: SklearnModel = random_forest_classifier
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
    assert Path(modelcard.uri, SaveName.TRAINED_MODEL.value).with_suffix(".joblib").exists()
    assert Path(modelcard.uri, SaveName.PREPROCESSOR.value).with_suffix(".joblib").exists()
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

    loaded_card.load_model()
    assert type(loaded_card.interface.model) == type(modelcard.interface.model)

    loaded_card.load_onnx_model()
    assert loaded_card.interface.onnx_model is not None
    assert loaded_card.interface.onnx_model.sess is not None


def test_save_lgb_booster_modelcard(
    lgb_booster_model: LightGBMModel,
):
    model: LightGBMModel = lgb_booster_model

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
    assert Path(modelcard.uri, SaveName.TRAINED_MODEL.value).with_suffix(".txt").exists()
    assert Path(modelcard.uri, SaveName.PREPROCESSOR.value).with_suffix(".joblib").exists()
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

    loaded_card.load_model()
    assert type(loaded_card.interface.model) == type(modelcard.interface.model)

    loaded_card.load_onnx_model()
    assert loaded_card.interface.onnx_model is not None
    assert loaded_card.interface.onnx_model.sess is not None


def test_save_lgb_sklearn_modelcard(
    lgb_regressor_model: LightGBMModel,
):
    model: LightGBMModel = lgb_regressor_model

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
    assert Path(modelcard.uri, SaveName.TRAINED_MODEL.value).with_suffix(".joblib").exists()
    assert Path(modelcard.uri, SaveName.PREPROCESSOR.value).with_suffix(".joblib").exists()
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


def test_save_torch_modelcard(
    pytorch_simple: PyTorchModel,
):
    model: PyTorchModel = pytorch_simple

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
    assert Path(modelcard.uri, SaveName.TRAINED_MODEL.value).with_suffix(".pt").exists()
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

    model.model.load_state_dict(loaded_card.interface.model)
    loaded_card.interface.model = model.model

    assert type(loaded_card.interface.model) == type(modelcard.interface.model)

    #
    loaded_card.load_onnx_model()
    assert loaded_card.interface.onnx_model is not None
    assert loaded_card.interface.onnx_model.sess is not None


def test_save_torch_lightning_modelcard(
    lightning_regression: LightningModel,
):
    model, model_arch = lightning_regression
    model = cast(LightningModel, model)

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
    assert Path(modelcard.uri, SaveName.TRAINED_MODEL.value).with_suffix(".ckpt").exists()
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

    # pytorch lightning model need model arch to load
    loaded_card.load_model(**{CommonKwargs.MODEL_ARCH.value: model_arch})

    assert type(loaded_card.interface.model) == type(modelcard.interface.model.model)

    #
    loaded_card.load_onnx_model()
    assert loaded_card.interface.onnx_model is not None
    assert loaded_card.interface.onnx_model.sess is not None


def test_save_tensorflow_modelcard(
    tf_transformer_example: TensorFlowModel,
):
    model: TensorFlowModel = tf_transformer_example

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

def test_save_huggingface_pipeline_modelcard(huggingface_text_classification_pipeline: HuggingFaceModel):
    model: HuggingFaceModel = huggingface_text_classification_pipeline

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
        
    # attempt to load onnx model before loading model
    loaded_card.load_onnx_model()
    assert loaded_card.onnx_model is not None
    assert loaded_card.onnx_model.sess is not None
    assert isinstance(loaded_card.onnx_model.sess, Pipeline)
    
    # loading onnx model should also load preprocessors
    assert type(loaded_card.preprocessor) == type(modelcard.interface.tokenizer)
    assert loaded_card.interface.model is None # model should still be none


    loaded_card.load_model()
    assert type(loaded_card.model) == type(modelcard.interface.model)
    assert isinstance(loaded_card.model, Pipeline)