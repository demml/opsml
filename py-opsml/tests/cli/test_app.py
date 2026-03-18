###################################################################################################
# This file contains test cases for testing an OpsML App workflow
###################################################################################################

from opsml.cli import (
    lock_service,
    install_service,
)
from opsml.mock import MockConfig
import pandas as pd
import os
from pathlib import Path
import shutil
from opsml.mock import OpsmlTestServer
from opsml.scouter import (
    PsiDriftConfig,
    CustomMetricDriftConfig,
    CustomMetric,
)
import opsml.scouter
from opsml.scouter.alert import AlertThreshold
from opsml.app import AppState

from opsml import (
    start_experiment,
    ModelCard,
    SklearnModel,
    PromptCard,
    Prompt,
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
            baseline_value=0.5,
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
def test_pyproject_app(
    mock_environment,
    random_forest_classifier: SklearnModel,
    chat_prompt: Prompt,
    example_dataframe: pd.DataFrame,
):
    """
    This test is meant to test the workflow of creating artifacts, creating a lock files, downloading
    artifacts and loading them all from a path into an AppState object

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

        # load the service card and the queue
        app = AppState.from_path(
            path=opsml_service,
            transport_config=opsml.scouter.HttpConfig(),  # this will be mocked
        )

        assert app.queue is not None

        assert isinstance(app.queue.transport_config, MockConfig)

        ## delete the opsml_service and lock file
        shutil.rmtree(opsml_service)
        os.remove(lock_file)


@pytest.mark.skipif(WINDOWS_EXCLUDE, reason="skipping")
def test_from_spec(
    mock_environment,
    random_forest_classifier: SklearnModel,
    chat_prompt: Prompt,
    example_dataframe: pd.DataFrame,
):
    """
    Test that AppState.from_spec installs from opsmlspec.yaml and loads the service
    without manually calling lock_service/install_service first.
    """
    with OpsmlTestServer(True, CURRENT_DIRECTORY):
        run_experiment(random_forest_classifier, chat_prompt, example_dataframe)

        spec_path = CURRENT_DIRECTORY / "opsmlspec.yaml"
        app = AppState.from_spec(
            path=spec_path,
            transport_config=opsml.scouter.HttpConfig(),
        )

        assert app.queue is not None
        assert isinstance(app.queue.transport_config, MockConfig)

        opsml_service = CURRENT_DIRECTORY / "opsml_service"
        lock_file = CURRENT_DIRECTORY / "opsml.lock"
        shutil.rmtree(opsml_service, ignore_errors=True)
        if lock_file.exists():
            os.remove(lock_file)


@pytest.mark.skipif(WINDOWS_EXCLUDE, reason="skipping")
def test_from_spec_no_register(
    mock_environment,
    random_forest_classifier: SklearnModel,
    chat_prompt: Prompt,
    example_dataframe: pd.DataFrame,
):
    """
    Test that AppState.from_spec with register=False loads the service
    without registering a new ServiceCard.
    """
    with OpsmlTestServer(True, CURRENT_DIRECTORY):
        # Register model and prompt cards so they exist for download
        run_experiment(random_forest_classifier, chat_prompt, example_dataframe)

        app = AppState.from_spec(
            path=CURRENT_DIRECTORY,
            transport_config=opsml.scouter.HttpConfig(),
            register=False,
        )

        assert app.service is not None
        assert app.queue is not None
        assert isinstance(app.queue.transport_config, MockConfig)

        # Cleanup
        opsml_service = CURRENT_DIRECTORY / "opsml_service"
        lock_file = CURRENT_DIRECTORY / "opsml.lock"
        shutil.rmtree(opsml_service, ignore_errors=True)
        if lock_file.exists():
            os.remove(lock_file)
