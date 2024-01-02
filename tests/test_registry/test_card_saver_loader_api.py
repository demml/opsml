import uuid
from pathlib import Path
from typing import cast

from opsml.registry.cards import Description, ModelCard, ModelCardMetadata
from opsml.registry.cards.card_loader import CardLoader
from opsml.registry.cards.card_saver import save_card_artifacts
from opsml.registry.model.interfaces import (
    HuggingFaceModel,
    LightGBMModel,
    LightningModel,
    PyTorchModel,
    SklearnModel,
)
from opsml.registry.storage import client
from opsml.registry.types import CommonKwargs, RegistryType, SaveName


def test_save_huggingface_modelcard_api_client(
    huggingface_torch_distilbert: HuggingFaceModel,
    api_storage_client: client.StorageClientBase,
):
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
    assert api_storage_client.exists(Path(modelcard.uri, SaveName.TRAINED_MODEL.value))
    assert api_storage_client.exists(Path(modelcard.uri, SaveName.PREPROCESSOR.value))
    assert api_storage_client.exists(Path(modelcard.uri, SaveName.SAMPLE_MODEL_DATA.value).with_suffix(".joblib"))
    assert api_storage_client.exists(Path(modelcard.uri, SaveName.ONNX_MODEL.value))
    assert api_storage_client.exists(Path(modelcard.uri, SaveName.QUANTIZED_MODEL.value))
    assert api_storage_client.exists(Path(modelcard.uri, SaveName.CARD.value).with_suffix(".joblib"))

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

    #
    loaded_card.load_onnx_model()
    assert loaded_card.interface.onnx_model is not None
    assert loaded_card.interface.onnx_model.sess is not None

    loaded_card.load_onnx_model(load_quantized=True)
    assert loaded_card.interface.onnx_model is not None
    assert loaded_card.interface.onnx_model.sess is not None


def test_save_sklearn_modelcard_api_client(
    random_forest_classifier: SklearnModel,
    api_storage_client: client.StorageClientBase,
):
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
    assert api_storage_client.exists(Path(modelcard.uri, SaveName.TRAINED_MODEL.value).with_suffix(".joblib"))
    assert api_storage_client.exists(Path(modelcard.uri, SaveName.PREPROCESSOR.value).with_suffix(".joblib"))
    assert api_storage_client.exists(Path(modelcard.uri, SaveName.SAMPLE_MODEL_DATA.value).with_suffix(".joblib"))
    assert api_storage_client.exists(Path(modelcard.uri, SaveName.ONNX_MODEL.value).with_suffix(".onnx"))
    assert api_storage_client.exists(Path(modelcard.uri, SaveName.CARD.value).with_suffix(".joblib"))

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


def test_save_lgb_booster_modelcard_api_client(
    lgb_booster_model: LightGBMModel,  # change to lgb
    api_storage_client: client.StorageClientBase,
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
    assert api_storage_client.exists(Path(modelcard.uri, SaveName.TRAINED_MODEL.value).with_suffix(".txt"))
    assert api_storage_client.exists(Path(modelcard.uri, SaveName.PREPROCESSOR.value).with_suffix(".joblib"))
    assert api_storage_client.exists(Path(modelcard.uri, SaveName.SAMPLE_MODEL_DATA.value).with_suffix(".joblib"))
    assert api_storage_client.exists(Path(modelcard.uri, SaveName.ONNX_MODEL.value).with_suffix(".onnx"))
    assert api_storage_client.exists(Path(modelcard.uri, SaveName.CARD.value).with_suffix(".joblib"))

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


def test_save_lgb_sklearn_modelcard_api_client(
    lgb_regressor_model: LightGBMModel,  # change to lgb
    api_storage_client: client.StorageClientBase,
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
    assert api_storage_client.exists(Path(modelcard.uri, SaveName.TRAINED_MODEL.value).with_suffix(".joblib"))
    assert api_storage_client.exists(Path(modelcard.uri, SaveName.PREPROCESSOR.value).with_suffix(".joblib"))
    assert api_storage_client.exists(Path(modelcard.uri, SaveName.SAMPLE_MODEL_DATA.value).with_suffix(".joblib"))
    assert api_storage_client.exists(Path(modelcard.uri, SaveName.ONNX_MODEL.value).with_suffix(".onnx"))
    assert api_storage_client.exists(Path(modelcard.uri, SaveName.CARD.value).with_suffix(".joblib"))

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


def test_save_torch_modelcard_api_client(
    pytorch_simple: PyTorchModel,
    api_storage_client: client.StorageClientBase,
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
    assert api_storage_client.exists(Path(modelcard.uri, SaveName.TRAINED_MODEL.value).with_suffix(".pt"))
    assert api_storage_client.exists(Path(modelcard.uri, SaveName.SAMPLE_MODEL_DATA.value).with_suffix(".joblib"))
    assert api_storage_client.exists(Path(modelcard.uri, SaveName.ONNX_MODEL.value).with_suffix(".onnx"))
    assert api_storage_client.exists(Path(modelcard.uri, SaveName.CARD.value).with_suffix(".joblib"))

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


def test_save_torch_lightning_modelcard_api_client(
    lightning_regression: LightningModel,
    api_storage_client: client.StorageClientBase,
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
    assert api_storage_client.exists(Path(modelcard.uri, SaveName.TRAINED_MODEL.value).with_suffix(".ckpt"))
    assert api_storage_client.exists(Path(modelcard.uri, SaveName.SAMPLE_MODEL_DATA.value).with_suffix(".joblib"))
    assert api_storage_client.exists(Path(modelcard.uri, SaveName.ONNX_MODEL.value).with_suffix(".onnx"))
    assert api_storage_client.exists(Path(modelcard.uri, SaveName.CARD.value).with_suffix(".joblib"))

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


# add tf test
