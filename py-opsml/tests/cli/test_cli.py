###################################################################################################
# This file contains tes cases for the OpsML CLI.
# In order to test the CLI, we expose some of the top-level functions in the opsml.cli module.
###################################################################################################

from opsml.cli import lock_project, install_app, generate_key  # type: ignore
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
    CardDeck,
    CardRegistry,
)
from tests.conftest import WINDOWS_EXCLUDE
import pytest

# Set current directory
CURRENT_DIRECTORY = Path(os.getcwd()) / "tests" / "cli" / "assets"


def run_experiment(
    random_forest_classifier: SklearnModel,
    chat_prompt: Prompt,
):
    with start_experiment(space="test", log_hardware=True) as exp:
        modelcard = ModelCard(
            interface=random_forest_classifier,
            tags=["foo:bar", "baz:qux"],
            version="1.0.0",
        )
        exp.register_card(modelcard)

        prompt_card = PromptCard(
            prompt=chat_prompt,
            version="1.0.0",
        )
        exp.register_card(prompt_card)


@pytest.mark.skipif(WINDOWS_EXCLUDE, reason="skipping")
def test_pyproject_app_lock_project(
    random_forest_classifier: SklearnModel,
    chat_prompt: Prompt,
):
    """
    This test is meant to test creating an opsml.lock file and installing the app/downloading
    all app artifacts and loading them.

    # The test will:
    1. Create initial experiment and register a model and prompt
    2. Create a lock file via lock_project form pyproject.toml (cli: opsml lock)
    3. Check if the lock file was created
    4. Install the app via install_app (cli: opsml install app)
    5. Check if the opsml_app directory was created and all artifacts were downloaded
    6. Load all artifacts and check if they are not None
    7. Create a new experiment to register a new model and prompt (increment version)
    8. Re-lock the project which should overwrite the existing lock file and bump the versions
    9. Install the app again and check if the new artifacts were downloaded
    10. Load all artifacts and check if versions are correct


    """
    with OpsmlTestServer(False, CURRENT_DIRECTORY):
        # run experiment to populate registry
        run_experiment(random_forest_classifier, chat_prompt)

        lock_project(CURRENT_DIRECTORY)

        # Check if the lock file was created
        lock_file = CURRENT_DIRECTORY / "opsml.lock"
        assert lock_file.exists()

        # download the assets
        install_app(CURRENT_DIRECTORY, CURRENT_DIRECTORY)

        # check if opsml_app was created
        opsml_app = CURRENT_DIRECTORY / "opsml_app"
        assert opsml_app.exists()

        # check if the opsml_app contains the assets
        assert (opsml_app / "app1").exists()
        assert (opsml_app / "app2").exists()
        assert (opsml_app / "app3").exists()

        # try loading each deck
        for app in ["app1", "app2", "app3"]:
            deck = CardDeck.load_from_path(opsml_app / app)
            assert deck is not None
            assert deck["my_model"].model is not None
            assert deck["my_model"].version == "1.0.0"
            assert deck["my_prompt"].prompt is not None
            assert deck["my_prompt"].version == "1.0.0"

        ## delete the opsml_app and lock file
        shutil.rmtree(opsml_app)
        os.remove(lock_file)

        # write new experiment to the registry
        run_experiment(random_forest_classifier, chat_prompt)

        # check multiple files exist
        reg = CardRegistry("model")
        cards = reg.list_cards(space="space", name="model")

        assert len(cards) == 2

        # lock the project again
        lock_project(CURRENT_DIRECTORY)

        # Check if the lock file was created
        lock_file = CURRENT_DIRECTORY / "opsml.lock"

        assert lock_file.exists()

        # re-install the app
        install_app(CURRENT_DIRECTORY, CURRENT_DIRECTORY)

        ## check if opsml_app was created
        opsml_app = CURRENT_DIRECTORY / "opsml_app"
        assert opsml_app.exists()

        for app in ["app1", "app2", "app3"]:
            deck = CardDeck.load_from_path(opsml_app / app)
            assert deck is not None
            assert deck["my_model"].model is not None
            assert deck["my_model"].version == "1.1.0"
            assert deck["my_prompt"].prompt is not None
            assert deck["my_prompt"].version == "1.1.0"

        ## delete the opsml_app and lock file
        shutil.rmtree(opsml_app)
        os.remove(lock_file)


def test_generate_key():
    """
    This test is meant to test generating a master key via the CLI.
    """

    password = "test_password"
    rounds = 10

    generate_key(password=password, rounds=rounds)
