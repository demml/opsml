###################################################################################################
# This file contains test cases for testing an OpsML App workflow in an api with an http queue
# This is an integration test and will require running the scouter-server docker image in the background.
###################################################################################################

from opsml.cli import (
    lock_service,
    install_service,
)  # type: ignore
from pathlib import Path
from fastapi import FastAPI, Request
import os
from sklearn import ensemble  # type: ignore
import pytest
from typing import Generator, Dict, cast, Tuple, Union
from opsml.mock import OpsmlTestServer
from opsml.scouter import PsiDriftConfig, HttpConfig
import numpy as np
from contextlib import asynccontextmanager
from opsml import (  # type: ignore
    start_experiment,
    ModelCard,
)
from opsml.helpers.data import create_fake_data  # type: ignore
from sklearn.preprocessing import StandardScaler  # type: ignore
from opsml import TaskType
from opsml.model import SklearnModel
import pandas as pd
from numpy.typing import NDArray
from opsml.app import AppState
from pydantic import BaseModel
from opsml.scouter.queue import Features, Feature, ScouterQueue

# from opsml.scouter.queue import ScouterQueue
from opsml.scouter.util import FeatureMixin

# Set current directory
CURRENT_DIRECTORY = Path(os.getcwd()) / "tests" / "api" / "assets"


class TestResponse(BaseModel):
    message: str


class PredictRequest(BaseModel, FeatureMixin):
    col_0: float
    col_1: float
    col_2: float
    col_3: float
    col_4: float
    col_5: float
    col_6: float
    col_7: float
    col_8: float
    col_9: float

    @staticmethod
    def example_request() -> Dict[str, float]:
        return {
            "col_0": np.random.rand(),
            "col_1": np.random.rand(),
            "col_2": np.random.rand(),
            "col_3": np.random.rand(),
            "col_4": np.random.rand(),
            "col_5": np.random.rand(),
            "col_6": np.random.rand(),
            "col_7": np.random.rand(),
            "col_8": np.random.rand(),
            "col_9": np.random.rand(),
        }

    def to_array(self) -> NDArray[np.float64]:
        return np.array(
            [
                self.col_0,
                self.col_1,
                self.col_2,
                self.col_3,
                self.col_4,
                self.col_5,
                self.col_6,
                self.col_7,
                self.col_8,
                self.col_9,
            ]
        ).reshape(1, -1)


def prediction_to_features(prediction: Union[int, float]) -> Features:
    return Features(features=[Feature.float(name="target", value=prediction)])


def example_dataframe() -> Tuple[pd.DataFrame, pd.DataFrame]:
    X, y = cast(Tuple[pd.DataFrame, pd.DataFrame], create_fake_data(n_samples=1200))

    return (X, y)


def random_forest_classifier():
    X_train, y_train = example_dataframe()
    reg = ensemble.RandomForestClassifier(n_estimators=5)
    reg.fit(X_train.to_numpy(), y_train)

    return (
        SklearnModel(
            model=reg,
            sample_data=X_train,
            task_type=TaskType.Classification,
            preprocessor=StandardScaler(),
        ),
        X_train,
        y_train,
    )


def run_experiment() -> None:
    with start_experiment(space="test", log_hardware=True) as exp:
        classifier, X, y = random_forest_classifier()
        # create psi drift profile
        classifier.create_drift_profile(
            alias="psi",
            data=y,
            config=PsiDriftConfig(),
        )

        modelcard = ModelCard(
            interface=classifier,
            tags=["foo:bar", "baz:qux"],
            version="1.0.0",
        )
        exp.register_card(modelcard)


@pytest.fixture
def create_artifacts() -> Generator[Tuple[Path, Path], None, None]:
    with OpsmlTestServer(True, CURRENT_DIRECTORY):
        run_experiment()
        lock_service(CURRENT_DIRECTORY)

        lock_file = CURRENT_DIRECTORY / "opsml.lock"
        assert lock_file.exists()

        # download the assets
        install_service(CURRENT_DIRECTORY, CURRENT_DIRECTORY)

        opsml_service = CURRENT_DIRECTORY / "opsml_service"
        assert opsml_service.exists()

        # Check if the lock file was created
        lock_file = CURRENT_DIRECTORY / "opsml.lock"
        assert lock_file.exists()

        yield opsml_service, lock_file


def create_app(opsml_service: Path) -> FastAPI:
    config = HttpConfig()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app_state = AppState.from_path(
            path=opsml_service,
            transport_config=config,
        )
        app.state.app_state = app_state

        yield

        # Shutdown the queue
        app.state.app_state.queue.shutdown()

    app = FastAPI(lifespan=lifespan)

    @app.post("/predict", response_model=TestResponse)
    async def predict(request: Request, payload: PredictRequest) -> TestResponse:
        modelcard: ModelCard = request.app.state.app_state.service["model"]
        queue: ScouterQueue = request.app.state.app_state.queue

        # make prediction
        prediction = modelcard.model.predict(payload.to_array())

        # Send to queue
        queue["psi"].insert(prediction_to_features(prediction[0]))

        return TestResponse(message="success")

    return app
