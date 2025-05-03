from opsml.test import OpsmlTestServer  # type: ignore
from opsml import (  # type: ignore
    CardRegistry,
    RegistryType,
    ModelCard,
    DataCard,
    PromptCard,
    Prompt,
    ModelLoadKwargs,
    ModelInterface,
)
from opsml.card import CardDeck, Card  # type: ignore
from opsml.card import RegistryMode, CardList  # type: ignore
from opsml.model import SklearnModel  # type: ignore
from opsml.data import PandasData  # type: ignore
from pathlib import Path
import shutil
import pytest
from tests.conftest import CustomModel
from tests.conftest import WINDOWS_EXCLUDE


@pytest.mark.skipif(WINDOWS_EXCLUDE, reason="skipping")
def test_crud_artifactcard(
    custom_interface: ModelInterface,
):
    # start server
    with OpsmlTestServer(True):
        reg = CardRegistry(registry_type=RegistryType.Model)

        card = ModelCard(
            interface=custom_interface,
            space="test",
            name="test",
            to_onnx=True,
            tags=["foo:bar", "baz:qux"],
        )

        reg.register_card(card)

        ## load the card
        loaded_card = reg.load_card(card.uid, interface=CustomModel)

        loaded_card.load()

        assert loaded_card.interface.model is not None
        assert loaded_card.interface.preprocessor is not None
