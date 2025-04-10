from opsml.cli import lock_project  # type: ignore
import os
from pathlib import Path

from opsml.test import OpsmlTestServer

from opsml import (  # type: ignore
    start_experiment,
    DataCard,
    ModelCard,
    ModelCardMetadata,
    PandasData,
    SklearnModel,
    Prompt,
    PromptCard,
    CardDeck,
    Card,
    RegistryType,
)
from opsml.card import CardRegistries
from tests.conftest import WINDOWS_EXCLUDE
import pytest
import time
# Sets up logging for tests


@pytest.mark.skipif(WINDOWS_EXCLUDE, reason="skipping")
def test_pyproject_app_lock_project(
    random_forest_classifier: SklearnModel,
    chat_prompt: Prompt,
):
    with OpsmlTestServer(False):
        with start_experiment(space="test", log_hardware=True) as exp:
            modelcard = ModelCard(
                interface=random_forest_classifier,
                space="space",
                name="model",
                tags=["foo:bar", "baz:qux"],
                version="1.0.0",
            )
            exp.register_card(modelcard)

            prompt_card = PromptCard(
                prompt=chat_prompt,
                space="space",
                name="prompt",
                version="1.0.0",
            )
            exp.register_card(prompt_card)

            assert prompt_card.experimentcard_uid == exp.card.uid

        current_directory = Path(os.getcwd()) / "tests" / "cli" / "assets"
        lock_project(current_directory)

        # add test to download assets from lock file
        # get_app_artifacts
