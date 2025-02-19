from opsml.test import OpsmlTestServer
from opsml.card import (
    CardRegistry,
    RegistryType,
    RegistryMode,
    CardList,
    ModelCard,
    DataCard,
)
from opsml.model import SklearnModel
from opsml.data import PandasData
from pathlib import Path
import shutil


def crud_datacard(pandas_data: PandasData):
    reg = CardRegistry(registry_type="data")

    assert reg.registry_type == RegistryType.Data
    assert reg.mode == RegistryMode.Client

    cards = reg.list_cards()

    assert isinstance(cards, CardList)
    assert len(cards) == 0

    card = DataCard(
        interface=pandas_data,
        repository="test",
        name="test",
        contact="test",
        tags=["foo:bar", "baz:qux"],
    )

    reg.register_card(card)
    cards = reg.list_cards()
    cards.as_table()

    assert isinstance(cards, CardList)
    assert len(cards) == 1
    loaded_card: DataCard = reg.load_card(uid=card.uid)

    # load all artifacts
    loaded_card.load()

    assert loaded_card.name == card.name
    assert loaded_card.repository == card.repository
    assert loaded_card.contact == card.contact
    assert loaded_card.tags == card.tags
    assert loaded_card.uid == card.uid
    assert loaded_card.version == card.version

    assert isinstance(loaded_card.interface, PandasData)

    # attempt to download all artifacts
    loaded_card.download_artifacts()

    # check that "card_artifacts" directory was created and contains 5 files

    created_path = Path("card_artifacts")
    assert created_path.exists()

    assert len(list(created_path.iterdir())) == 5

    # attempt to delete folder
    shutil.rmtree("card_artifacts")

    # attempt to update the card
    loaded_card.name = "test2"

    # update the card
    reg.update_card(loaded_card)

    # load the updated card
    updated_card: DataCard = reg.load_card(uid=loaded_card.uid)

    # assert that the card was updated
    assert updated_card.name == "test2"

    # attempt to delete the card
    reg.delete_card(card=updated_card)

    cards = reg.list_cards(uid=updated_card.uid)
    assert len(cards) == 0


def crud_modelcard(random_forest_classifier: SklearnModel):
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

    card.runcard_uid = "test"
    assert card.runcard_uid == "test"

    reg.register_card(card)
    cards = reg.list_cards()
    cards.as_table()

    assert isinstance(cards, CardList)
    assert len(cards) == 1
    loaded_card: ModelCard = reg.load_card(uid=card.uid)

    # load all artifacts
    loaded_card.load(onnx=True)

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
    assert loaded_card.interface.onnx_session.session is not None

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

    # attempt to update the card
    loaded_card.name = "test2"

    # update the card
    reg.update_card(loaded_card)

    # load the updated card
    updated_card: ModelCard = reg.load_card(uid=loaded_card.uid)

    # assert that the card was updated
    assert updated_card.name == "test2"

    # attempt to delete the card
    reg.delete_card(card=updated_card)

    cards = reg.list_cards(uid=updated_card.uid)
    assert len(cards) == 0


def test_crud_modelcard(
    random_forest_classifier: SklearnModel,
    pandas_data: PandasData,
):
    # start server
    with OpsmlTestServer():
        crud_datacard(pandas_data)
        # crud_modelcard(random_forest_classifier)
