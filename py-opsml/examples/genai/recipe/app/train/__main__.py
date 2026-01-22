from opsml.card import Card, CardRegistries, ServiceCard
from opsml.types import DriftArgs

from .prompt import create_recipe_prompt_card

if __name__ == "__main__":
    registries = CardRegistries()

    # Get cards
    promptcard = create_recipe_prompt_card()

    # Register cards

    registries.prompt.register_card(
        promptcard,
        save_kwargs={
            "drift": DriftArgs(
                active=True,
                deactivate_others=True,
            ),
        },
    )

    # create service card
    service_card = ServiceCard(
        name="recipe_service",
        space="opsml",
        cards=[
            Card(alias="recipe", card=promptcard),
        ],
    )

    registries.service.register_card(service_card)
