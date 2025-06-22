###################################################################################################
# This file contains test cases for testing an OpsML App workflow in an api with an http queue
# This is an integration test and will require running the scouter-server docker image in the background.
###################################################################################################

from opsml.cli import (
    lock_project,
    install_app,
)  # type: ignore
from pathlib import Path

import os
from typing import Generator
from opsml.mock import OpsmlTestServer
from opsml.scouter import PsiDriftConfig


from opsml import (  # type: ignore
    start_experiment,
    ModelCard,
)
from tests.conftest import random_forest_classifier, example_dataframe
from pydantic import BaseModel
from opsml.scouter.util import FeatureMixin

# Set current directory
CURRENT_DIRECTORY = Path(os.getcwd()) / "tests" / "api" / "assets"


class TestResponse(BaseModel):
    message: str


class PredictRequest(BaseModel, FeatureMixin):
    feature_0: float
    feature_1: float
    feature_2: float
    feature_3: float


def run_experiment():
    with start_experiment(space="test", log_hardware=True) as exp:
        X, _, _, _ = example_dataframe()
        classifier = random_forest_classifier()
        # create psi drift profile
        classifier.create_drift_profile(
            alias="psi",
            data=X,
            config=PsiDriftConfig(),
        )

        modelcard = ModelCard(
            interface=random_forest_classifier,
            tags=["foo:bar", "baz:qux"],
            version="1.0.0",
        )
        exp.register_card(modelcard)


def create_artifacts() -> Generator[Path, None, None]:
    with OpsmlTestServer(True, CURRENT_DIRECTORY):
        run_experiment()
        lock_project(CURRENT_DIRECTORY)

        lock_file = CURRENT_DIRECTORY / "opsml.lock"
        assert lock_file.exists()

        # download the assets
        install_app(CURRENT_DIRECTORY, CURRENT_DIRECTORY)

        opsml_app = CURRENT_DIRECTORY / "opsml_app"
        assert opsml_app.exists()

        yield opsml_app
