###################################################################################################
# This file contains test cases for testing an OpsML App workflow
###################################################################################################


import time
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
from opsml.card import ServiceCard, Card, RegistryType
import opsml.scouter
from opsml.scouter.types import CommonCrons
from opsml.scouter.alert import AlertThreshold
from opsml.scouter.queue import Features
from opsml.app import AppState, ReloadConfig
from opsml.card import download_service
from opsml.scouter import Metrics, Metric
import numpy as np

from opsml import (  # type: ignore
    start_experiment,
    ModelCard,
    SklearnModel,
    PromptCard,
    Prompt,
)
from tests.conftest import WINDOWS_EXCLUDE
import pytest

CURRENT_DIRECTORY = Path(os.getcwd())
ASSETS_DIRECTORY = CURRENT_DIRECTORY / "tests" / "service" / "assets"
RAND_INT = np.random.randint(0, 100)
SERVICE_SPACE = f"opsml_{RAND_INT}"
SERVICE_NAME = f"service_{RAND_INT}"


def create_service(
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
            space="opsml",
            name="model",
            interface=random_forest_classifier,
            tags=["foo:bar", "baz:qux"],
            version="1.0.0",
        )
        exp.register_card(modelcard)

        prompt_card = PromptCard(
            space="opsml",
            name="prompt",
            prompt=chat_prompt,
            version="1.0.0",
        )
        exp.register_card(prompt_card)

        service = ServiceCard(
            space=SERVICE_SPACE,
            name=SERVICE_NAME,
            cards=[
                Card(
                    alias="model",
                    uid=modelcard.uid,
                    registry_type=RegistryType.Model,
                ),
                Card(
                    alias="prompt",
                    uid=prompt_card.uid,
                    registry_type=RegistryType.Prompt,
                ),
            ],
        )
        exp.register_card(service)


@pytest.mark.skipif(WINDOWS_EXCLUDE, reason="skipping")
def test_service_reload(
    mock_environment,
    random_forest_classifier: SklearnModel,
    chat_prompt: Prompt,
    example_dataframe: pd.DataFrame,
):
    """
    This test is meant to test the workflow of creating artifacts, creating a lock files, downloading
    artifacts and loading them all from a path into an AppState object

    """
    with OpsmlTestServer(True, ASSETS_DIRECTORY):
        # run experiment to populate registry
        create_service(random_forest_classifier, chat_prompt, example_dataframe)

        opsml_app = ASSETS_DIRECTORY / "opsml_app"
        service_reload = ASSETS_DIRECTORY / "service_reload"

        # download service
        download_service(
            write_dir=opsml_app,
            space=SERVICE_SPACE,
            name=SERVICE_NAME,
        )

        app = AppState.from_path(
            path=opsml_app,
            transport_config=opsml.scouter.HTTPConfig(),  # type: ignore
            reload_config=ReloadConfig(
                cron=CommonCrons.Every1Minute.cron,
                write_path=service_reload,
            ),
        )
        app.start_reloader()
        assert app.service.version == "0.1.0"
        assert app.queue["custom"].identifier == "opsml/model/v1.0.0/custom"
        assert app.queue["psi"].identifier == "opsml/model/v1.0.0/psi"
        #
        # insert metric
        metrics = Metrics(metrics=[Metric("custom", 2.0)])
        app.queue["custom"].insert(metrics)
        app.queue["psi"].insert(
            Features(
                {
                    "col_0": 10.0,
                    "col_1": 10.0,
                }
            )
        )

        # create next service version and wait 2 sec before triggering a reload
        create_service(random_forest_classifier, chat_prompt, example_dataframe)
        time.sleep(5)
        #
        # This is just to force a reload
        app.reload()
        #
        ## allow time to load before assertions
        time.sleep(5)
        assert app.service.version == "0.2.0"
        assert app.queue["custom"].identifier == "opsml/model/v1.1.0/custom"
        assert app.queue["psi"].identifier == "opsml/model/v1.1.0/psi"
        #
        metrics = Metrics(metrics=[Metric("custom", 2.0)])
        app.queue["custom"].insert(metrics)
        app.queue["psi"].insert(
            Features(
                {
                    "col_0": 10.0,
                    "col_1": 10.0,
                }
            )
        )

        app.shutdown()
        shutil.rmtree(opsml_app, ignore_errors=True)
