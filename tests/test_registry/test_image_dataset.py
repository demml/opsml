from typing import Dict
import os
from opsml.registry.cards import DataCard
from opsml.registry.sql.registry import CardRegistry
from opsml.registry.cards.types import ImageDataset


def test_register_data(
    db_registries: Dict[str, CardRegistry],
):
    # create data card
    registry = db_registries["data"]

    image_dataset = ImageDataset(
        image_dir="tests/assets/image_dataset",
        metadata="metadata.jsonl",
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
    meta_path = os.path.join(loaded_card.data.image_dir, loaded_card.data.metadata)
    assert os.path.exists(meta_path)
