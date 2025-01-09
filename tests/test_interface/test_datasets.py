import uuid
from pathlib import Path
from typing import cast

from opsml.cards import DataCard
from opsml.data import (
    ImageDataset,
    ImageMetadata,
    ImageRecord,
    TextDataset,
    TextMetadata,
    TextRecord,
)
from opsml.storage.card_loader import CardLoader
from opsml.storage.card_saver import save_card_artifacts
from opsml.types import RegistryType, SaveName, Suffix
from tests.conftest import OPSML_STORAGE_URI, client


def test_image_metadata():
    record = {
        "filepath": Path("tests/assets/image_dataset/cats.jpg"),
        "caption": "This is a second value of a text feature you added to your images",
    }

    record = ImageRecord(**record)
    assert record.filepath == Path("tests/assets/image_dataset/cats.jpg")

    bbox_record = {
        "filepath": Path("tests/assets/image_dataset/cat2.jpg"),
        "objects": {"bbox": [[160.0, 31.0, 248.0, 616.0], [741.0, 68.0, 202.0, 401.0]], "categories": [2, 2]},
    }

    record = ImageRecord(**bbox_record)
    assert record.objects.bbox == [[160.0, 31.0, 248.0, 616.0], [741.0, 68.0, 202.0, 401.0]]

    arrow = record.to_arrow(data_dir="tests/assets/image_dataset")
    assert arrow["path"] == "cat2.jpg"

    metadata = ImageMetadata(records=[record])
    assert metadata.size == 63304

    metadata.write_to_file(Path("tests/assets/image_dataset/metadata.jsonl"))
    assert Path("tests/assets/image_dataset/metadata.jsonl").exists()

    # load metadata
    _ = ImageMetadata.load_from_file(Path("tests/assets/image_dataset/metadata.jsonl"))

    client.storage_client.rm(Path("tests/assets/image_dataset/metadata.jsonl"))
    assert not Path("tests/assets/image_dataset/metadata.jsonl").exists()


def test_image_dataset(create_image_dataset: Path):
    data_dir = create_image_dataset
    image_data = ImageDataset(data_dir=data_dir)
    storage_client = client.storage_client

    datacard = DataCard(
        interface=image_data,
        name="test_data",
        repository="mlops",
        contact="test_email",
        version="0.0.1",
        uid=uuid.uuid4().hex,
    )

    save_card_artifacts(datacard)

    assert storage_client.exists(Path(datacard.uri, SaveName.DATA.value))
    assert storage_client.exists(Path(datacard.uri, SaveName.DATASET.value).with_suffix(Suffix.JOBLIB.value))
    assert storage_client.exists(Path(datacard.uri, SaveName.CARD.value).with_suffix(Suffix.JSON.value))
    storage_client.rm(Path(OPSML_STORAGE_URI))
    assert not storage_client.exists(Path(OPSML_STORAGE_URI))


def test_image_dataset_multiproc(create_image_dataset: Path):
    data_dir = create_image_dataset
    image_data = ImageDataset(data_dir=data_dir, shard_size="200KB")
    storage_client = client.storage_client

    datacard = DataCard(
        interface=image_data,
        name="test_data",
        repository="mlops",
        contact="test_email",
        version="0.0.1",
        uid=uuid.uuid4().hex,
    )

    save_card_artifacts(datacard)

    assert storage_client.exists(Path(datacard.uri, SaveName.DATA.value))
    assert storage_client.exists(Path(datacard.uri, SaveName.DATASET.value).with_suffix(Suffix.JOBLIB.value))
    assert storage_client.exists(Path(datacard.uri, SaveName.CARD.value).with_suffix(Suffix.JSON.value))
    storage_client.rm(Path(OPSML_STORAGE_URI))
    assert not storage_client.exists(Path(OPSML_STORAGE_URI))


def test_image_split_dataset(create_split_image_dataset: Path):
    data_dir = create_split_image_dataset
    image_data = ImageDataset(data_dir=data_dir)
    storage_client = client.storage_client

    nbr_files = len(storage_client.find(data_dir))

    datacard = DataCard(
        interface=image_data,
        name="test_data",
        repository="mlops",
        contact="test_email",
        version="0.0.1",
        uid=uuid.uuid4().hex,
    )

    save_card_artifacts(datacard)

    assert storage_client.exists(Path(datacard.uri, SaveName.DATA.value))
    assert storage_client.exists(Path(datacard.uri, SaveName.CARD.value).with_suffix(Suffix.JSON.value))

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
    loaded_card.interface.data_dir = data_dir.parent / write_dir_path

    # Loading
    loaded_card.load_data()  # this will load all splits and use single processing
    assert storage_client.exists(Path(loaded_card.interface.data_dir, "train"))
    assert storage_client.exists(Path(loaded_card.interface.data_dir, "test"))
    assert storage_client.exists(Path(loaded_card.interface.data_dir, "eval"))

    # check numbers match up
    downloaded_files = len(storage_client.find(Path(loaded_card.interface.data_dir)))
    assert nbr_files == downloaded_files
    storage_client.rm(Path(loaded_card.interface.data_dir))
    assert not storage_client.exists(Path(loaded_card.interface.data_dir))

    # test specific split
    loaded_card.load_data(split="train", chunk_size=100)  # this will load train split and use multi processing
    assert storage_client.exists(Path(loaded_card.interface.data_dir, "train"))
    assert not storage_client.exists(Path(loaded_card.interface.data_dir, "test"))
    assert not storage_client.exists(Path(loaded_card.interface.data_dir, "eval"))
    storage_client.rm(Path(loaded_card.interface.data_dir))
    assert not storage_client.exists(Path(loaded_card.interface.data_dir))

    # cleanup datacard path
    storage_client.rm(Path(OPSML_STORAGE_URI))
    assert not storage_client.exists(Path(OPSML_STORAGE_URI))


def test_text_metadata():
    record = {"filepath": Path("tests/assets/text_dataset/text1.txt")}

    record = TextRecord(**record)
    assert record.filepath == Path("tests/assets/text_dataset/text1.txt")

    arrow = record.to_arrow(data_dir="tests/assets/text_dataset")
    assert arrow["path"] == "text1.txt"

    metadata = TextMetadata(records=[record])
    assert metadata.size == 4

    metadata.write_to_file(Path("tests/assets/text_dataset/metadata.jsonl"))
    assert Path("tests/assets/text_dataset/metadata.jsonl").exists()

    # load metadata
    _ = TextMetadata.load_from_file(Path("tests/assets/text_dataset/metadata.jsonl"))

    client.storage_client.rm(Path("tests/assets/text_dataset/metadata.jsonl"))
    assert not Path("tests/assets/text_dataset/metadata.jsonl").exists()


def test_text_dataset(create_text_dataset: Path):
    data_dir = create_text_dataset
    text_data = TextDataset(data_dir=data_dir)
    storage_client = client.storage_client

    datacard = DataCard(
        interface=text_data,
        name="test_data",
        repository="mlops",
        contact="test_email",
        version="0.0.1",
        uid=uuid.uuid4().hex,
    )

    save_card_artifacts(datacard)

    assert storage_client.exists(Path(datacard.uri, SaveName.DATA.value))
    assert storage_client.exists(Path(datacard.uri, SaveName.CARD.value).with_suffix(Suffix.JSON.value))
    storage_client.rm(Path(OPSML_STORAGE_URI))
    assert not storage_client.exists(Path(OPSML_STORAGE_URI))


def test_text_split_dataset(create_split_text_dataset: Path):
    data_dir = create_split_text_dataset
    text_data = TextDataset(data_dir=data_dir)
    storage_client = client.storage_client

    nbr_files = len(storage_client.find(data_dir))

    datacard = DataCard(
        interface=text_data,
        name="test_data",
        repository="mlops",
        contact="test_email",
        version="0.0.1",
        uid=uuid.uuid4().hex,
    )

    save_card_artifacts(datacard)

    assert storage_client.exists(Path(datacard.uri, SaveName.DATA.value))
    assert storage_client.exists(Path(datacard.uri, SaveName.CARD.value).with_suffix(Suffix.JSON.value))

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
    loaded_card.interface.data_dir = data_dir.parent / write_dir_path

    # Loading
    loaded_card.load_data()  # this will load all splits and use single processing
    assert storage_client.exists(Path(loaded_card.interface.data_dir, "train"))
    assert storage_client.exists(Path(loaded_card.interface.data_dir, "test"))
    assert storage_client.exists(Path(loaded_card.interface.data_dir, "eval"))

    # check numbers match up
    downloaded_files = len(storage_client.find(Path(loaded_card.interface.data_dir)))
    assert nbr_files == downloaded_files
    storage_client.rm(Path(loaded_card.interface.data_dir))
    assert not storage_client.exists(Path(loaded_card.interface.data_dir))

    # test specific split
    loaded_card.load_data(split="train", chunk_size=100)  # this will load train split and use multi processing
    assert storage_client.exists(Path(loaded_card.interface.data_dir, "train"))
    assert not storage_client.exists(Path(loaded_card.interface.data_dir, "test"))
    assert not storage_client.exists(Path(loaded_card.interface.data_dir, "eval"))
    storage_client.rm(Path(loaded_card.interface.data_dir))
    assert not storage_client.exists(Path(loaded_card.interface.data_dir))

    # cleanup datacard path
    storage_client.rm(Path(OPSML_STORAGE_URI))
    assert not storage_client.exists(Path(OPSML_STORAGE_URI))
