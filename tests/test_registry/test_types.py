import os
from opsml.registry.cards.types import ImageMetadata, ImageRecord, ImageDataset
from pydantic_core._pydantic_core import ValidationError
import pytest

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


def test_image_dataset():
    image_dataset = ImageDataset(
        image_dir="tests/assets/image_dataset",
        metadata="metadata.json",
    )

    # fail if file doesn't exists
    with pytest.raises(ValidationError) as ve:
        ImageDataset(
            image_dir="tests/assets/image_dataset",
            metadata="blah.json",
        )
    ve.match("metadata file blah.json does not exist")

    # fail on non-json
    with pytest.raises(ValidationError) as ve:
        ImageDataset(
            image_dir="tests/assets/image_dataset",
            metadata="metadata.txt",
        )
    ve.match("metadata must be a json file")
