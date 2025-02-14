from opsml.test import OpsmlTestServer
from opsml.card import CardRegistry, RegistryType, RegistryMode, CardList, ModelCard
from opsml.model import SklearnModel
from opsml.data import PandasData
from pathlib import Path
import shutil


def test_client_modelcard(random_forest_classifier: SklearnModel):
    # start server
    with OpsmlTestServer():
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
        loaded_card: ModelCard = reg.load_card(uid=card.uid)

        # load all artifacts
        loaded_card.load(
            model=True,
            onnx=True,
            sample_data=True,
            preprocessor=True,
        )

        assert loaded_card.name == card.name
        assert loaded_card.repository == card.repository
        assert loaded_card.contact == card.contact
        assert loaded_card.tags == card.tags
        assert loaded_card.uid == card.uid
        assert loaded_card.version == card.version

        assert isinstance(loaded_card.interface, SklearnModel)
        assert loaded_card.interface.sample_data is not None
        assert loaded_card.interface.model is not None
        assert loaded_card.interface.onnx_session is not None
        assert loaded_card.interface.preprocessor is not None
        assert loaded_card.interface.onnx_session.session is not None
        assert isinstance(loaded_card.interface.sample_data, PandasData)

        # attempt to download all artifacts
        loaded_card.download_artifacts()

        # check that "card_artifacts" directory was created and contains 5 files

        created_path = Path("card_artifacts")
        assert created_path.exists()

        assert len(list(created_path.iterdir())) == 5

        # attempt to delete folder
        shutil.rmtree("card_artifacts")

    # wrong uid being use to upload card


# create modelcard and register it
