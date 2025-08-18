###################################################################################################
# This file contains test cases for testing an OpsML App workflow
###################################################################################################

from opsml.cli import (
    lock_project,
    install_service,
)  # type: ignore
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
from opsml.scouter.types import CommonCrons
from opsml.scouter.alert import AlertThreshold
from opsml.app import AppState, ReloadConfig


from opsml import (  # type: ignore
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

        lock_project(CURRENT_DIRECTORY)

        # Check if the lock file was created
        lock_file = CURRENT_DIRECTORY / "opsml.lock"
        assert lock_file.exists()

        # download the assets
        install_service(CURRENT_DIRECTORY, CURRENT_DIRECTORY)

        # check if opsml_app was created
        opsml_app = CURRENT_DIRECTORY / "opsml_app"
        assert opsml_app.exists()

        # check if the opsml_app contains the assets
        assert (opsml_app / "app1").exists()

        # load the service card and the queue
        app = AppState.from_path(
            path=opsml_app / "app1",
            # transport_config=opsml.scouter.HTTPConfig(),  # this will be mocked
            reload_config=ReloadConfig(cron=CommonCrons.Every1Minute.cron),
        )

        # assert app.queue is not None
        # assert isinstance(app.queue.transport_config, MockConfig)
        assert app.has_reloader is True

        # run another experiment and re-lock
        run_experiment(random_forest_classifier, chat_prompt, example_dataframe)
        lock_project(CURRENT_DIRECTORY)

        # test reload function
        app.reload()

        ## Add logic to create a new service card to trigger reload

        ## delete the opsml_app and lock file
        shutil.rmtree(opsml_app)
        os.remove(lock_file)
        a
