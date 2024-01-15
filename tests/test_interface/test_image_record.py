from pathlib import Path

from opsml.data.interfaces.custom_data.image import ImageMetadata, ImageRecord
from opsml.data import ImageData
from tests.conftest import client


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

    arrow = record.to_arrow(data_dir="image_dataset")
    assert arrow["path"] == "image_dataset/cat2.jpg"

    metadata = ImageMetadata(records=[record])
    assert metadata.size == 63304

    metadata.write_to_file(Path("tests/assets/image_dataset/metadata.jsonl"))
    assert Path("tests/assets/image_dataset/metadata.jsonl").exists()

    # load metadata
    _ = ImageMetadata.load_from_file(Path("tests/assets/image_dataset/metadata.jsonl"))

    client.storage_client.rm(Path("tests/assets/image_dataset/metadata.jsonl"))
    assert not Path("tests/assets/image_dataset/metadata.jsonl").exists()


def test_image_dataset(create_image_dataset:Path):
    data_dir = create_image_dataset
    image_data = ImageData(data_dir=data_dir)
    
    
    
