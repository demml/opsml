import shutil
import uuid
from pathlib import Path
from typing import cast

import polars as pl
from sklearn.preprocessing import LabelEncoder

from opsml.cards import DataCard
from opsml.data import (
    ArrowData,
    ImageDataset,
    NumpyData,
    PandasData,
    PolarsData,
    TextDataset,
)
from opsml.storage import client
from opsml.storage.card_loader import CardLoader
from opsml.storage.card_saver import save_card_artifacts
from opsml.types import RegistryType, SaveName
from opsml.types.extra import Suffix


def test_numpy_api_client(
    numpy_data: NumpyData,
    api_storage_client: client.StorageClientBase,
) -> None:
    data: NumpyData = numpy_data

    datacard = DataCard(
        interface=data,
        name="test_data",
        repository="mlops",
        contact="test_email",
        version="0.0.1",
        uid=uuid.uuid4().hex,
    )

    save_card_artifacts(datacard)

    # check paths exist on server
    assert api_storage_client.exists(Path(datacard.uri, SaveName.DATA.value).with_suffix(Suffix.ZARR.value))
    assert api_storage_client.exists(Path(datacard.uri, SaveName.CARD.value).with_suffix(Suffix.JSON.value))

    # load objects
    loader = CardLoader(
        card_args={
            "name": datacard.name,
            "repository": datacard.repository,
            "version": datacard.version,
        },
        registry_type=RegistryType.DATA,
    )

    loaded_card = cast(DataCard, loader.load_card())
    assert isinstance(loaded_card, DataCard)

    loaded_card.load_data()
    assert isinstance(loaded_card.interface, NumpyData)
    assert type(loaded_card.interface.data) == type(datacard.interface.data)
    assert loaded_card.interface.data_splits == datacard.interface.data_splits


def test_pandas_api_client(
    pandas_data: PandasData,
    api_storage_client: client.StorageClientBase,
) -> None:
    data: PandasData = pandas_data
    assert data.data is not None

    encoder = LabelEncoder()
    data.data["animals"] = encoder.fit_transform(data.data["animals"])

    data.create_data_profile()

    datacard = DataCard(
        interface=data,
        name="test_data",
        repository="mlops",
        contact="test_email",
        version="0.0.1",
        uid=uuid.uuid4().hex,
    )

    save_card_artifacts(datacard)

    # check paths exist on server
    assert api_storage_client.exists(Path(datacard.uri, SaveName.DATA.value).with_suffix(data.data_suffix))
    assert api_storage_client.exists(Path(datacard.uri, SaveName.DATA_PROFILE.value).with_suffix(Suffix.JSON.value))
    assert api_storage_client.exists(Path(datacard.uri, SaveName.CARD.value).with_suffix(Suffix.JSON.value))

    # load objects
    loader = CardLoader(
        card_args={
            "name": datacard.name,
            "repository": datacard.repository,
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
) -> None:
    data: PolarsData = polars_data
    assert data.data is not None

    encoder = LabelEncoder()
    transformed = encoder.fit_transform(data.data["bar"].to_pandas())
    data.data = data.data.with_columns([pl.Series(transformed).alias("bar")])

    data.create_data_profile()

    datacard = DataCard(
        interface=data,
        name="test_data",
        repository="mlops",
        contact="test_email",
        version="0.0.1",
        uid=uuid.uuid4().hex,
    )

    save_card_artifacts(datacard)

    # check paths exist on server
    assert api_storage_client.exists(Path(datacard.uri, SaveName.DATA.value).with_suffix(data.data_suffix))
    assert api_storage_client.exists(Path(datacard.uri, SaveName.DATA_PROFILE.value).with_suffix(Suffix.JSON.value))
    assert api_storage_client.exists(Path(datacard.uri, SaveName.CARD.value).with_suffix(Suffix.JSON.value))

    # load objects
    loader = CardLoader(
        card_args={
            "name": datacard.name,
            "repository": datacard.repository,
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
) -> None:
    data: ArrowData = arrow_data

    datacard = DataCard(
        interface=data,
        name="test_data",
        repository="mlops",
        contact="test_email",
        version="0.0.1",
        uid=uuid.uuid4().hex,
    )

    save_card_artifacts(datacard)

    # check paths exist on server
    assert api_storage_client.exists(Path(datacard.uri, SaveName.DATA.value).with_suffix(data.data_suffix))
    assert api_storage_client.exists(Path(datacard.uri, SaveName.CARD.value).with_suffix(Suffix.JSON.value))

    # load objects
    loader = CardLoader(
        card_args={
            "name": datacard.name,
            "repository": datacard.repository,
            "version": datacard.version,
        },
        registry_type=RegistryType.DATA,
    )

    loaded_card = cast(DataCard, loader.load_card())
    assert isinstance(loaded_card, DataCard)

    loaded_card.load_data()
    assert type(loaded_card.interface.data) == type(datacard.interface.data)


def test_image_data(
    create_image_dataset: Path,
    api_storage_client: client.StorageClientBase,
) -> None:

    data_dir = create_image_dataset
    image_data = ImageDataset(data_dir=data_dir)

    datacard = DataCard(
        interface=image_data,
        name="test_data",
        repository="mlops",
        contact="test_email",
        version="0.0.1",
        uid=uuid.uuid4().hex,
    )

    save_card_artifacts(datacard)

    # check paths exist on server
    assert api_storage_client.exists(Path(datacard.uri, SaveName.DATA.value))
    assert api_storage_client.exists(Path(datacard.uri, SaveName.CARD.value).with_suffix(Suffix.JSON.value))

    # load objects
    loader = CardLoader(
        card_args={
            "name": datacard.name,
            "repository": datacard.repository,
            "version": datacard.version,
        },
        registry_type=RegistryType.DATA,
    )

    loaded_card = cast(DataCard, loader.load_card())
    assert isinstance(loaded_card, DataCard)

    ## swap write path so we can test loading
    write_dir_path = uuid.uuid4().hex
    loaded_interface = cast(ImageDataset, loaded_card.interface)
    loaded_interface.data_dir = data_dir.parent / write_dir_path
    loaded_card.load_data()

    assert loaded_interface.data_dir.exists()

    shutil.rmtree(loaded_interface.data_dir, ignore_errors=True)
    assert not loaded_interface.data_dir.exists()


def test_text_data(
    create_text_dataset: Path,
    api_storage_client: client.StorageClientBase,
) -> None:

    data_dir = create_text_dataset
    text_data = TextDataset(data_dir=data_dir)

    datacard = DataCard(
        interface=text_data,
        name="test_data",
        repository="mlops",
        contact="test_email",
        version="0.0.1",
        uid=uuid.uuid4().hex,
    )

    save_card_artifacts(datacard)

    # check paths exist on server
    assert api_storage_client.exists(Path(datacard.uri, SaveName.DATA.value))
    assert api_storage_client.exists(Path(datacard.uri, SaveName.CARD.value).with_suffix(Suffix.JSON.value))

    # load objects
    loader = CardLoader(
        card_args={
            "name": datacard.name,
            "repository": datacard.repository,
            "version": datacard.version,
        },
        registry_type=RegistryType.DATA,
    )

    loaded_card = cast(DataCard, loader.load_card())
    assert isinstance(loaded_card, DataCard)

    ## swap write path so we can test loading
    write_dir_path = uuid.uuid4().hex
    loaded_interface = cast(TextDataset, loaded_card.interface)
    loaded_interface.data_dir = data_dir.parent / write_dir_path
    loaded_card.load_data()

    assert loaded_interface.data_dir.exists()

    shutil.rmtree(loaded_interface.data_dir, ignore_errors=True)
    assert not loaded_interface.data_dir.exists()
