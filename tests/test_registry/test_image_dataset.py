from typing import Dict
import os
from opsml.registry.cards import DataCard
from opsml.registry.sql.registry import CardRegistry
from opsml.registry.image import ImageDataset, ImageRecord, ImageMetadata
from pydantic_core._pydantic_core import ValidationError
import pytest
import tempfile

# these examples are pulled from huggingface
# the aim is to have as much parity as possible


def test_image_record():
    record = {
        "file_name": "0002.png",
        "caption": "This is a second value of a text feature you added to your images",
    }

    metadata = ImageRecord(**record)
    assert metadata.file_name == "0002.png"

    bbox_record = {
        "file_name": "0003.png",
        "objects": {"bbox": [[160.0, 31.0, 248.0, 616.0], [741.0, 68.0, 202.0, 401.0]], "categories": [2, 2]},
    }

    metadata = ImageRecord(**bbox_record)
    assert metadata.file_name == "0003.png"
    assert metadata.objects.bbox == [[160.0, 31.0, 248.0, 616.0], [741.0, 68.0, 202.0, 401.0]]


def test_image_metadata():
    records = [
        {"file_name": "0001.png", "objects": {"bbox": [[302.0, 109.0, 73.0, 52.0]], "categories": [0]}},
        {
            "file_name": "0002.png",
            "caption": "This is a second value of a text feature you added to your images",
        },
        {"file_name": "0002.png", "objects": {"bbox": [[810.0, 100.0, 57.0, 28.0]], "categories": [1]}},
        {
            "file_name": "0003.png",
            "objects": {"bbox": [[160.0, 31.0, 248.0, 616.0], [741.0, 68.0, 202.0, 401.0]], "categories": [2, 2]},
        },
    ]

    metadata = ImageMetadata(records=records)

    assert metadata.records[0].file_name == "0001.png"
    assert metadata.records[0].objects.bbox == [[302.0, 109.0, 73.0, 52.0]]

    with tempfile.TemporaryDirectory() as tmp_dir:
        filename = os.path.join(tmp_dir, "metadata.jsonl")
        metadata.write_to_file(filename)
        assert os.path.exists(filename)


def test_image_dataset():
    ImageDataset(
        image_dir="tests/assets/image_dataset",
        metadata="metadata.jsonl",
    )

    # fail if file doesn't exists
    with pytest.raises(ValidationError) as ve:
        ImageDataset(
            image_dir="tests/assets/image_dataset",
            metadata="blah.jsonl",
        )
    ve.match("metadata file blah.jsonl does not exist")

    # fail on non-json
    with pytest.raises(ValidationError) as ve:
        ImageDataset(
            image_dir="tests/assets/image_dataset",
            metadata="metadata.txt",
        )
    ve.match("metadata must be a jsonl file")


def test_register_data(
    db_registries: Dict[str, CardRegistry],
):
    # create data card
    registry = db_registries["data"]

    records = [
        {"file_name": "cats.jpg", "caption": "This is a second value of a text feature you added to your images"},
        {"file_name": "cat2.jpg", "caption": "This is a second value of a text feature you added to your images"},
    ]
    metadata = ImageMetadata(records=records)

    image_dataset = ImageDataset(
        image_dir="tests/assets/image_dataset",
        metadata=metadata,
    )

    data_card = DataCard(
        data=image_dataset,
        name="test_df",
        team="mlops",
        user_email="mlops.com",
    )

    registry.register_card(card=data_card)

    loaded_card = registry.load_card(uid=data_card.uid)
    loaded_card.data.image_dir = "test_image_dir"
    loaded_card.load_data()

    assert os.path.isdir(loaded_card.data.image_dir)
    meta_path = os.path.join(loaded_card.data.image_dir, "metadata.jsonl")
    assert os.path.exists(meta_path)
