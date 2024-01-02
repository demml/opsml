import uuid
from pathlib import Path
from typing import cast

from opsml.registry.cards import DataCard
from opsml.registry.cards.card_loader import CardLoader
from opsml.registry.cards.card_saver import save_card_artifacts
from opsml.registry.data.interfaces import NumpyData
from opsml.registry.storage import client
from opsml.registry.types import RegistryType, SaveName
from opsml.registry.types.extra import Suffix



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
    )

    save_card_artifacts(datacard)

    # check paths exist on server
    assert api_storage_client.exists(Path(datacard.uri, SaveName.DATA.value).with_suffix(Suffix.ZARR.value))
    assert api_storage_client.exists(Path(datacard.uri, SaveName.CARD.value).with_suffix(".joblib"))

    # load objects
    loader = CardLoader(
        card_args={
            "name": datacard.name,
            "team": datacard.team,
            "version": datacard.version,
        },
        registry_type=RegistryType.DATA,
    )

    loaded_card = cast(DataCard, loader.load_card())
    assert isinstance(loaded_card, DataCard)

    loaded_card.load_data()
    assert type(loaded_card.interface.data) == type(datacard.interface.data)

