from typing import Dict
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
        metadata="metadata.json",
    )

    data_card = DataCard(
        data=image_dataset,
        name="test_df",
        team="mlops",
        user_email="mlops.com",
    )

    registry.register_card(card=data_card)
