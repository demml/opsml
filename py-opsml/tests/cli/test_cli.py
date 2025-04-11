###################################################################################################
# This file contains tes cases for the OpsML CLI.
# In order to test the CLI, we expose some of the top-level functions in the opsml.cli module.
###################################################################################################

from opsml.cli import lock_project, install_app  # type: ignore
import os
from pathlib import Path
import shutil
from opsml.test import OpsmlTestServer

from opsml import (  # type: ignore
    start_experiment,
    ModelCard,
    SklearnModel,
    Prompt,
    PromptCard,
)
from tests.conftest import WINDOWS_EXCLUDE
import pytest
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

        # Check if the lock file was created
        lock_file = current_directory / "opsml.lock"
        assert lock_file.exists()

        # download the assets
        install_app(current_directory, current_directory)

        # check if opsml_app was created
        opsml_app = current_directory / "opsml_app"
        assert opsml_app.exists()
        # check if the opsml_app contains the assets
        assert (opsml_app / "app1").exists()
        assert (opsml_app / "app2").exists()
        assert (opsml_app / "app3").exists()

        # delete the opsml_app
        shutil.rmtree(opsml_app)
        os.remove(lock_file)
