from opsml.test import OpsmlTestServer
from opsml import (
    CardRegistry,
    RegistryType,
    ModelCard,
    DataCard,
    PromptCard,
    ChatPrompt,
)
from opsml.card import RegistryMode
from opsml.card import CardList
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
    assert loaded_card.tags == card.tags
    assert loaded_card.uid == card.uid
    assert loaded_card.version == card.version

    assert isinstance(loaded_card.interface, PandasData)

    # attempt to download all artifacts
    loaded_card.download_artifacts()

    # check that "card_artifacts" directory was created and contains 5 files

    created_path = Path("card_artifacts")
    assert created_path.exists()

    assert len(list(created_path.iterdir())) == 2

    # attempt to delete folder
    shutil.rmtree("card_artifacts")

    # attempt to update the card
    loaded_card.name = "test2"

    assert loaded_card.interface is not None
    assert card.interface is not None

    assert loaded_card.interface.data_splits.splits[0].column_split is not None
    assert (
        loaded_card.interface.data_splits.splits[0].column_split.column_name == "col_1"
    )

    split_data = loaded_card.interface.split_data()
    assert split_data["train"].x.shape[1] == 9
    assert split_data["train"].y.shape[1] == 1

    # update the card
    reg.update_card(loaded_card)

    # load the updated card
    updated_card: DataCard = reg.load_card(uid=loaded_card.uid)

    # assert that the card was updated
    assert updated_card.name == "test2"

    return updated_card, reg


def crud_promptcard(prompt: ChatPrompt):
    reg = CardRegistry(registry_type="prompt")

    assert reg.registry_type == RegistryType.Prompt
    assert reg.mode == RegistryMode.Client

    cards = reg.list_cards()

    assert isinstance(cards, CardList)
    assert len(cards) == 0

    card = PromptCard(
        prompt=prompt,
        repository="test",
        name="test",
    )

    reg.register_card(card)
    cards = reg.list_cards()
    cards.as_table()

    assert isinstance(cards, CardList)
    assert len(cards) == 1
    loaded_card: PromptCard = reg.load_card(uid=card.uid)

    assert loaded_card.name == card.name
    assert loaded_card.repository == card.repository
    assert loaded_card.tags == card.tags
    assert loaded_card.uid == card.uid
    assert loaded_card.version == card.version

    assert isinstance(loaded_card.prompt, ChatPrompt)

    # update the card
    loaded_card.name = "test2"
    # update the card
    reg.update_card(loaded_card)

    # load the updated card
    updated_card: PromptCard = reg.load_card(uid=loaded_card.uid)

    # assert that the card was updated
    assert updated_card.name == "test2"

    return updated_card, reg


def crud_modelcard(random_forest_classifier: SklearnModel, datacard: DataCard):
    reg = CardRegistry(registry_type=RegistryType.Model)

    assert reg.registry_type == RegistryType.Model
    assert reg.mode == RegistryMode.Client

    cards = reg.list_cards()

    assert isinstance(cards, CardList)
    assert len(cards) == 0

    interface: SklearnModel = random_forest_classifier
    interface.create_drift_profile(datacard.interface.data)

    card = ModelCard(
        interface=interface,
        repository="test",
        name="test",
        to_onnx=True,
        tags=["foo:bar", "baz:qux"],
    )

    # set uid
    card.datacard_uid = datacard.uid

    card.experimentcard_uid = "test"
    assert card.experimentcard_uid == "test"

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

    # make sure datacard_uid is set
    assert updated_card.datacard_uid == datacard.uid

    # assert that the card was updated
    assert updated_card.name == "test2"

    return updated_card, reg


def delete_card(card: DataCard | ModelCard, registry: CardRegistry):
    registry.delete_card(card=card)

    cards = registry.list_cards(uid=card.uid)
    assert len(cards) == 0


def test_crud_artifactcard(
    random_forest_classifier: SklearnModel,
    pandas_data: PandasData,
    chat_prompt: ChatPrompt,
):
    # start server
    with OpsmlTestServer(True):
        # datacard is required for modelcard, so we cant delete it before using it,
        # which is why there is a separate delete_card function

        datacard, data_registry = crud_datacard(pandas_data)
        modelcard, model_registry = crud_modelcard(random_forest_classifier, datacard)
        promptcard, prompt_registry = crud_promptcard(chat_prompt)

        delete_card(datacard, data_registry)
        delete_card(modelcard, model_registry)
        delete_card(promptcard, prompt_registry)
