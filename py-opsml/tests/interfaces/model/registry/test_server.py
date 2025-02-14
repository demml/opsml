from opsml.test import OpsmlTestServer
from opsml.card import CardRegistry, RegistryType, RegistryMode, CardList, ModelCard
from opsml.model import SklearnModel


def test_server(random_forest_classifier: SklearnModel):
    with OpsmlTestServer(False) as _server:
        reg = CardRegistry(registry_type=RegistryType.Model)

        assert reg.registry_type == RegistryType.Model
        assert reg.mode == RegistryMode.Client

        cards = reg.list_cards()

        assert isinstance(cards, CardList)
        assert len(cards) == 0

        interface: SklearnModel = random_forest_classifier

        card = ModelCard(
            interface=interface,
            repository="test",
            name="test",
            contact="test",
            to_onnx=True,
            tags=["foo:bar", "baz:qux"],
        )

        reg.register_card(card)
        cards = reg.list_cards()
        cards.as_table()

        assert isinstance(cards, CardList)
        assert len(cards) == 1
        loaded_card = reg.load_card(uid=card.uid)

    a

    # wrong uid being use to upload card


# create modelcard and register it
