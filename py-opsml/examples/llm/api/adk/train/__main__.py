from .eta import create_modelcard
from .prompt import create_shipment_prompt_card, create_response_prompt_card
from opsml.card import CardRegistries, ServiceCard, Card


if __name__ == "__main__":
    registries = CardRegistries()

    # Get cards
    modelcard = create_modelcard()
    shipment_prompt_card = create_shipment_prompt_card()
    response_prompt_card = create_response_prompt_card()

    # Register cards
    registries.model.register_card(modelcard)
    registries.prompt.register_card(shipment_prompt_card)
    registries.prompt.register_card(response_prompt_card)

    # create service card
    service_card = ServiceCard(
        name="shipment_service",
        space="opsml",
        cards=[
            Card(alias="shipment", card=shipment_prompt_card),
            Card(alias="response", card=response_prompt_card),
            Card(alias="eta", card=modelcard),
        ],
    )

    registries.service.register_card(service_card)
