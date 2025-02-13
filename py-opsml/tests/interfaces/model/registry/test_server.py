from opsml.test import OpsmlTestServer
from opsml.card import CardRegistry, RegistryType, RegistryMode, CardList, ModelCard
from opsml.model import SklearnModel
from pathlib import Path


def test_server(tmp_path: Path, random_forest_classifier: SklearnModel):
    with OpsmlTestServer() as _server:
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

        # create modelcard and register it
    a
