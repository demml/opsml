from opsml.data.interfaces._image import ImageRecord


def test_image_record():
    record = {
        "filename": "cats.jpg",
        "data_dir": "tests/assets/image_dataset",
        "caption": "This is a second value of a text feature you added to your images",
    }

    record = ImageRecord(**record)
    assert record.filename == "cats.jpg"

    bbox_record = {
        "filename": "cat2.jpg",
        "data_dir": "tests/assets/image_dataset",
        "objects": {"bbox": [[160.0, 31.0, 248.0, 616.0], [741.0, 68.0, 202.0, 401.0]], "categories": [2, 2]},
    }

    record = ImageRecord(**bbox_record)
    assert record.filename == "cat2.jpg"
    assert record.objects.bbox == [[160.0, 31.0, 248.0, 616.0], [741.0, 68.0, 202.0, 401.0]]
