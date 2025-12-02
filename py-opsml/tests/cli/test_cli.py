###################################################################################################
# This file contains tes cases for the OpsML CLI.
# In order to test the CLI, we expose some of the top-level functions in the opsml.cli module.
###################################################################################################

from opsml.cli import (
    lock_service,
    install_service,
    generate_key,
    update_drift_profile_status,
    ScouterArgs,
    validate_project,
    download_card,
    DownloadCard,
)
from opsml.service import ServiceSpec
import pandas as pd
import os
from pathlib import Path
import shutil
from opsml.mock import OpsmlTestServer
from opsml.scouter.types import DriftType
from opsml.scouter import PsiDriftConfig, CustomMetricDriftConfig, CustomMetric
from opsml.scouter.alert import AlertThreshold

from opsml import (
    start_experiment,
    ModelCard,
    SklearnModel,
    Prompt,
    PromptCard,
    ServiceCard,
    CardRegistry,
    RegistryType,
)
from tests.conftest import WINDOWS_EXCLUDE
import pytest

# Set current directory
CURRENT_DIRECTORY = Path(os.getcwd()) / "tests" / "cli" / "assets"


def run_experiment(
    random_forest_classifier: SklearnModel,
    chat_prompt: Prompt,
    example_dataframe: pd.DataFrame,
):
    with start_experiment(space="test", log_hardware=True) as exp:
        X, _, _, _ = example_dataframe
        # create psi drift profile
        random_forest_classifier.create_drift_profile(
            alias="psi",
            data=X,
            config=PsiDriftConfig(),
        )

        # create custom metric drift profile
        metric = CustomMetric(
            name="custom",
            value=0.5,
            alert_threshold=AlertThreshold.Above,
        )

        random_forest_classifier.create_drift_profile(
            alias="custom",
            data=[metric],
            config=CustomMetricDriftConfig(),
        )

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
def test_pyproject_app_lock_service(
    random_forest_classifier: SklearnModel,
    chat_prompt: Prompt,
    example_dataframe: pd.DataFrame,
):
    """
    This test is meant to test creating an opsml.lock file and installing the app/downloading
    all app artifacts and loading them.

    # The test will:
    1. Create initial experiment and register a model and prompt
    2. Create a lock file via lock_service form pyproject.toml (cli: opsml lock)
    3. Check if the lock file was created
    4. Install the app via install_service (cli: opsml install app)
    5. Check if the opsml_app directory was created and all artifacts were downloaded
    6. Load all artifacts and check if they are not None
    7. Create a new experiment to register a new model and prompt (increment version)
    8. Re-lock the project which should overwrite the existing lock file and bump the versions
    9. Install the app again and check if the new artifacts were downloaded
    10. Load all artifacts and check if versions are correct


    """
    with OpsmlTestServer(True, CURRENT_DIRECTORY):
        # run experiment to populate registry
        run_experiment(random_forest_classifier, chat_prompt, example_dataframe)

        lock_service(CURRENT_DIRECTORY)

        # Check if the lock file was created
        lock_file = CURRENT_DIRECTORY / "opsml.lock"
        assert lock_file.exists()

        # download the assets
        install_service(CURRENT_DIRECTORY, CURRENT_DIRECTORY)

        # check if opsml_service was created
        opsml_service = CURRENT_DIRECTORY / "opsml_service"
        assert opsml_service.exists()

        # check if the opsml_service contains the assets
        assert (opsml_service).exists()

        # try loading service
        service = ServiceCard.from_path(opsml_service)
        assert service is not None
        assert service["my_model"].model is not None
        assert service["my_model"].version == "1.0.0"
        assert service["my_prompt"].prompt is not None
        assert service["my_prompt"].version == "1.0.0"

        ## delete the opsml_service and lock file
        shutil.rmtree(opsml_service)
        os.remove(lock_file)

        # write new experiment to the registry
        run_experiment(random_forest_classifier, chat_prompt, example_dataframe)

        # check multiple files exist
        reg = CardRegistry("model")
        cards = reg.list_cards(space="space", name="model")

        assert len(cards) == 2

        # lock the service
        lock_service(CURRENT_DIRECTORY)

        # Check if the lock file was created
        lock_file = CURRENT_DIRECTORY / "opsml.lock"

        assert lock_file.exists()

        # re-install the app
        install_service(CURRENT_DIRECTORY, CURRENT_DIRECTORY)

        ## check if opsml_service was created
        opsml_service = CURRENT_DIRECTORY / "opsml_service"
        assert opsml_service.exists()

        service = ServiceCard.from_path(opsml_service)
        assert service is not None
        assert service["my_model"].model is not None
        assert service["my_model"].version == "1.1.0"
        assert service["my_prompt"].prompt is not None
        assert service["my_prompt"].version == "1.1.0"

        ## delete the opsml_service and lock file
        shutil.rmtree(opsml_service)
        os.remove(lock_file)


def test_generate_key():
    """
    This test is meant to test generating a master key via the CLI.
    """

    password = "test_password"
    rounds = 10

    generate_key(password=password, rounds=rounds)


@pytest.mark.skipif(WINDOWS_EXCLUDE, reason="skipping")
def test_update_profile_status_key():
    """
    This test is meant to test updating the status of a drift profile via the CLI.
    """

    # need to start the server to create a mock scouter server
    with OpsmlTestServer():
        args = ScouterArgs(
            space="test",
            name="test",
            version="1.0.0",
            active=True,
            drift_type=DriftType.Psi,
            deactivate_others=False,
        )
        update_drift_profile_status(args)


@pytest.mark.skipif(WINDOWS_EXCLUDE, reason="skipping")
def test_pyproject_app_validate_project():
    validate_project(CURRENT_DIRECTORY)


@pytest.mark.skipif(WINDOWS_EXCLUDE, reason="skipping")
def test_load_model_card(
    random_forest_classifier: SklearnModel,
    chat_prompt: Prompt,
    example_dataframe: pd.DataFrame,
    tmp_path: Path,
):
    with OpsmlTestServer(True, CURRENT_DIRECTORY):
        # run experiment to populate registry
        run_experiment(random_forest_classifier, chat_prompt, example_dataframe)

        artifacts = tmp_path / "artifacts"
        download_args = DownloadCard(
            space="space", name="model", write_dir=artifacts.as_posix()
        )
        download_card(download_args, RegistryType.Model)

        card = ModelCard.load_from_path(artifacts)
        assert card.model is not None
        assert card.version == "1.0.0"


@pytest.mark.skipif(WINDOWS_EXCLUDE, reason="skipping")
def test_load_spec_to_py():
    path = CURRENT_DIRECTORY / "opsmlspec.yaml"
    spec = ServiceSpec.from_path(path)

    print(spec)
    a
