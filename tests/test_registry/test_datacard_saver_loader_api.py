import uuid
from pathlib import Path
from typing import cast

from opsml.registry.cards import DataCard, DataCardMetadata, Description
from opsml.registry.cards.card_loader import CardLoader
from opsml.registry.cards.card_saver import save_card_artifacts
from opsml.registry.data.interfaces import NumpyData
from opsml.registry.storage import client
from opsml.registry.types import RegistryType, SaveName


def test_save_huggingface_modelcard_api_client(
    test_numpy_array: NumpyData,
    api_storage_client: client.StorageClientBase,
):
    data: NumpyData = test_numpy_array

    datacard = DataCard(
        interface=data,
        name="test_data",
        team="mlops",
        user_email="test_email",
        version="0.0.1",
        uid=uuid.uuid4().hex,
        metadata=DataCardMetadata(
            description=Description(summary="test description"),
        ),
    )

    save_card_artifacts(datacard)

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
