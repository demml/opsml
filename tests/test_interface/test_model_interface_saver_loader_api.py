import sys
import uuid
from pathlib import Path
from typing import cast

import pytest

from opsml.cards import Description, ModelCard, ModelCardMetadata
from opsml.model import (
    CatBoostModel,
    HuggingFaceModel,
    LightGBMModel,
    LightningModel,
    SklearnModel,
    TensorFlowModel,
    TorchModel,
)
from opsml.storage import client
from opsml.storage.card_loader import CardLoader
from opsml.storage.card_saver import save_card_artifacts
from opsml.types import CommonKwargs, RegistryType, SaveName, Suffix

DARWIN_EXCLUDE = sys.platform == "darwin" and sys.version_info < (3, 11)
WINDOWS_EXCLUDE = sys.platform == "win32"

EXCLUDE = bool(DARWIN_EXCLUDE or WINDOWS_EXCLUDE)


@pytest.mark.skipif(EXCLUDE, reason="skipping")
def test_save_huggingface_modelcard_api_client(
    huggingface_torch_distilbert: HuggingFaceModel,
    api_storage_client: client.StorageClientBase,
):
    model: HuggingFaceModel = huggingface_torch_distilbert

    modelcard = ModelCard(
        interface=model,
        name="test_model",
        repository="mlops",
        contact="test_email",
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
    assert api_storage_client.exists(Path(modelcard.uri, SaveName.TOKENIZER.value))
    assert api_storage_client.exists(Path(modelcard.uri, SaveName.SAMPLE_MODEL_DATA.value).with_suffix(".joblib"))
    assert api_storage_client.exists(Path(modelcard.uri, SaveName.ONNX_MODEL.value))
    assert api_storage_client.exists(Path(modelcard.uri, SaveName.QUANTIZED_MODEL.value))
    assert api_storage_client.exists(Path(modelcard.uri, SaveName.CARD.value).with_suffix(".joblib"))

    # load objects
    loader = CardLoader(
        card_args={
            "name": modelcard.name,
            "repository": modelcard.repository,
            "version": modelcard.version,
        },
        registry_type=RegistryType.MODEL,
    )

    loaded_card = cast(ModelCard, loader.load_card())
    assert isinstance(loaded_card, ModelCard)

    loaded_card.load_model()
    assert type(loaded_card.interface.model) == type(modelcard.interface.model)
    assert type(loaded_card.interface.tokenizer) == type(modelcard.interface.tokenizer)

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
        repository="mlops",
        contact="test_email",
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
            "repository": modelcard.repository,
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
        repository="mlops",
        contact="test_email",
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
            "repository": modelcard.repository,
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
        repository="mlops",
        contact="test_email",
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
            "repository": modelcard.repository,
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


@pytest.mark.skipif(EXCLUDE, reason="skipping")
def test_save_torch_modelcard_api_client(
    pytorch_simple: TorchModel,
    api_storage_client: client.StorageClientBase,
):
    model: TorchModel = pytorch_simple

    modelcard = ModelCard(
        interface=model,
        name="test_model",
        repository="mlops",
        contact="test_email",
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
            "repository": modelcard.repository,
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


@pytest.mark.skipif(EXCLUDE, reason="skipping")
def test_save_torch_lightning_modelcard_api_client(
    lightning_regression: LightningModel,
    api_storage_client: client.StorageClientBase,
):
    model, model_arch = lightning_regression
    model = cast(LightningModel, model)

    modelcard = ModelCard(
        interface=model,
        name="test_model",
        repository="mlops",
        contact="test_email",
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
            "repository": modelcard.repository,
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


@pytest.mark.skipif(EXCLUDE, reason="skipping")
def test_save_tensorflow_modelcard_api_client(
    tf_transformer_example: TensorFlowModel,
    api_storage_client: client.StorageClientBase,
):
    model: TensorFlowModel = tf_transformer_example

    modelcard = ModelCard(
        interface=model,
        name="test_model",
        repository="mlops",
        contact="test_email",
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
    assert api_storage_client.exists(Path(modelcard.uri, SaveName.SAMPLE_MODEL_DATA.value).with_suffix(".joblib"))
    assert api_storage_client.exists(Path(modelcard.uri, SaveName.ONNX_MODEL.value).with_suffix(".onnx"))
    assert api_storage_client.exists(Path(modelcard.uri, SaveName.CARD.value).with_suffix(".joblib"))

    # load objects
    loader = CardLoader(
        card_args={
            "name": modelcard.name,
            "repository": modelcard.repository,
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


@pytest.mark.skipif(EXCLUDE, reason="skipping")
def test_save_tensorflow_multi_input_modelcard_api_client(
    multi_input_tf_example: TensorFlowModel,
    api_storage_client: client.StorageClientBase,
):
    model: TensorFlowModel = multi_input_tf_example

    modelcard = ModelCard(
        interface=model,
        name="test_model",
        repository="mlops",
        contact="test_email",
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
    assert api_storage_client.exists(Path(modelcard.uri, SaveName.SAMPLE_MODEL_DATA.value).with_suffix(".joblib"))
    assert api_storage_client.exists(Path(modelcard.uri, SaveName.ONNX_MODEL.value).with_suffix(".onnx"))
    assert api_storage_client.exists(Path(modelcard.uri, SaveName.CARD.value).with_suffix(".joblib"))

    # load objects
    loader = CardLoader(
        card_args={
            "name": modelcard.name,
            "repository": modelcard.repository,
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


def test_save_catboost_modelcard(
    catboost_regressor: CatBoostModel,
    api_storage_client: client.StorageClientBase,
):
    model: CatBoostModel = catboost_regressor
    modelcard = ModelCard(
        interface=model,
        name="test_model",
        repository="mlops",
        contact="test_email",
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
    assert api_storage_client.exists(
        Path(modelcard.uri, SaveName.TRAINED_MODEL.value).with_suffix(Suffix.CATBOOST.value)
    )
    assert api_storage_client.exists(Path(modelcard.uri, SaveName.PREPROCESSOR.value).with_suffix(Suffix.JOBLIB.value))
    assert api_storage_client.exists(
        Path(modelcard.uri, SaveName.SAMPLE_MODEL_DATA.value).with_suffix(Suffix.JOBLIB.value)
    )
    assert api_storage_client.exists(Path(modelcard.uri, SaveName.ONNX_MODEL.value).with_suffix(Suffix.ONNX.value))
    assert api_storage_client.exists(Path(modelcard.uri, SaveName.CARD.value).with_suffix(Suffix.JOBLIB.value))

    # load objects
    loader = CardLoader(
        card_args={
            "name": modelcard.name,
            "repository": modelcard.repository,
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
