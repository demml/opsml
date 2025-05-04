from opsml.test import OpsmlTestServer  # type: ignore
from opsml import (  # type: ignore
    CardRegistry,
    RegistryType,
    ModelCard,
    ModelInterface,
    TaskType,
)
from opsml.error import OpsmlError
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
        assert loaded_card.interface.task_type == TaskType.AnomalyDetection


@pytest.mark.skipif(WINDOWS_EXCLUDE, reason="skipping")
def test_crud_artifactcard_failure(
    incorrect_custom_interface: ModelInterface,
):
    """This test is to check whether the rollback card logic works correctly."""
    # start server
    with OpsmlTestServer(True):
        reg = CardRegistry(registry_type=RegistryType.Model)

        card = ModelCard(
            interface=incorrect_custom_interface,
            space="test",
            name="test",
            to_onnx=True,
            tags=["foo:bar", "baz:qux"],
        )

        with pytest.raises(OpsmlError) as error:
            reg.register_card(card)

        assert (
            str(error.value)
            == "OpsmlError: AttributeError: 'IncorrectCustomModel' object has no attribute 'preprocessor'"
        )

        # check that no cards are registered
        assert len(reg.list_cards()) == 0
