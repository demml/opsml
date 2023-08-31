from opsml.registry import DataCard, CardRegistries
from opsml.registry.cards.types import ImageDataset


def test_register_data(api_registries: CardRegistries):
    # create data card
    registry = api_registries.data

    image_dataset = ImageDataset(
        image_dir="tests/assets/image_dataset",
        metadata="metadata.json",
    )

    data_card = DataCard(
        data=image_dataset,
        name="image_dataset",
        team="mlops",
        user_email="mlops.com",
    )

    registry.register_card(card=data_card)
    loaded_card = registry.load_card(uid=data_card.uid)
    loaded_card.load_data()
