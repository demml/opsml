import os
import sys

import pytest

from opsml.registry import CardRegistries, DataCard
from opsml.registry.image import ImageDataset


@pytest.mark.skipif(sys.platform == "win32", reason="No wn_32 test")
def test_register_data(api_registries: CardRegistries):
    # create data card
    registry = api_registries.data

    image_dataset = ImageDataset(
        image_dir="tests/assets/image_dataset",
        metadata="metadata.jsonl",
    )

    data_card = DataCard(
        data=image_dataset,
        name="image_dataset",
        team="mlops",
        user_email="mlops.com",
    )

    registry.register_card(card=data_card)
    loaded_card: DataCard = registry.load_card(uid=data_card.uid)

    loaded_card.data.image_dir = "test_image_dir"
    loaded_card.load_data()

    assert os.path.isdir(loaded_card.data.image_dir)
    meta_path = os.path.join(loaded_card.data.image_dir, loaded_card.data.metadata)
    assert os.path.exists(meta_path)
