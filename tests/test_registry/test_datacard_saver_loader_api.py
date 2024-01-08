import uuid
from pathlib import Path
from typing import cast

from opsml.cards import DataCard
from opsml.data.interfaces import ArrowData, NumpyData, PandasData, PolarsData
from opsml.storage import client
from opsml.storage.card_loader import CardLoader
from opsml.storage.card_saver import save_card_artifacts
from opsml.types import RegistryType, SaveName
from opsml.types.extra import Suffix


def test_numpy_api_client(
    numpy_data: NumpyData,
    api_storage_client: client.StorageClientBase,
):
    data: NumpyData = numpy_data

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


def test_pandas_api_client(
    pandas_data: PandasData,
    api_storage_client: client.StorageClientBase,
):
    data: PandasData = pandas_data
    data.create_data_profile()

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
    assert api_storage_client.exists(Path(datacard.uri, SaveName.DATA.value).with_suffix(data.data_suffix))
    assert api_storage_client.exists(Path(datacard.uri, SaveName.DATA_PROFILE.value).with_suffix(Suffix.JOBLIB.value))
    assert api_storage_client.exists(Path(datacard.uri, SaveName.DATA_PROFILE.value).with_suffix(Suffix.HTML.value))
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

    loaded_card.load_data_profile()
    assert loaded_card.interface.data_profile is not None


def test_polars_api_client(
    polars_data: PolarsData,
    api_storage_client: client.StorageClientBase,
):
    data: PolarsData = polars_data
    data.create_data_profile()

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
    assert api_storage_client.exists(Path(datacard.uri, SaveName.DATA.value).with_suffix(data.data_suffix))
    assert api_storage_client.exists(Path(datacard.uri, SaveName.DATA_PROFILE.value).with_suffix(Suffix.JOBLIB.value))
    assert api_storage_client.exists(Path(datacard.uri, SaveName.DATA_PROFILE.value).with_suffix(Suffix.HTML.value))
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

    loaded_card.load_data_profile()
    assert loaded_card.interface.data_profile is not None


def test_arrow_api_client(
    arrow_data: ArrowData,
    api_storage_client: client.StorageClientBase,
):
    data: ArrowData = arrow_data

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
    assert api_storage_client.exists(Path(datacard.uri, SaveName.DATA.value).with_suffix(data.data_suffix))
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
