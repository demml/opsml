# pylint: disable=invalid-name
from contextlib import asynccontextmanager
from pathlib import Path

import numpy as np
from fastapi import FastAPI, Request
from numpy.typing import NDArray
from opsml.app import AppState, ReloadConfig

# from opsml.scouter import HttpConfig # uncomment for model monitoring
from opsml.card import ModelCard
from opsml.logging import LoggingConfig, LogLevel, RustyLogger
from opsml.model import ModelLoadKwargs
from pydantic import BaseModel, Field

logger = RustyLogger.get_logger(
    LoggingConfig(log_level=LogLevel.Debug),
)


# 8 features
class PredictRequest(BaseModel):
    feature_1: float
    feature_2: float
    feature_3: float
    feature_4: float
    feature_5: float
    feature_6: float
    feature_7: float
    feature_8: float
    feature_9: float
    feature_10: float

    def to_f32_array(self) -> NDArray[np.float32]:
        """Converts the features to a numpy array of float32 with shape (1,10)"""
        return np.array(
            [
                self.feature_1,
                self.feature_2,
                self.feature_3,
                self.feature_4,
                self.feature_5,
                self.feature_6,
                self.feature_7,
                self.feature_8,
                self.feature_9,
                self.feature_10,
            ],
            dtype=np.float32,
        ).reshape(1, -1)


class ModelResponse(BaseModel):
    rf_class: int = Field(..., description="Predicted class from Random Forest model")
    lg_class: int = Field(..., description="Predicted class from LightGBM model")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up FastAPI app")

    app_state = AppState.from_path(
        path=Path("app/service_artifacts"),
        load_kwargs={
            "rf": {"load_kwargs": ModelLoadKwargs(load_onnx=True)},
            "lgb": {"load_kwargs": ModelLoadKwargs(load_onnx=True)},
        },
        reload_config=ReloadConfig(cron="0 0 0 * * *"),
        # transport_config=HttpConfig(), # uncomment for model monitoring
    )
    app_state.start_reloader()
    app.state.app_state = app_state

    yield

    logger.info("Shutting down FastAPI app")
    app.state.app_state.shutdown()
    app.state.app_state = None


app = FastAPI(lifespan=lifespan)


@app.post("/predict", response_model=ModelResponse)
async def predict(request: Request, payload: PredictRequest) -> ModelResponse:
    # Grab the reformulated prompt and response prompt from the app state
    rf_model: ModelCard = request.app.state.app_state.service["rf"]
    lgb_model: ModelCard = request.app.state.app_state.service["lgb"]
    data = payload.to_f32_array()

    rf_prediction = rf_model.onnx_session.run({"X": data}, None)
    lg_prediction = lgb_model.onnx_session.run({"X": data}, None)

    rf_class = rf_prediction[0][0]
    lg_class = lg_prediction[0][0]

    return ModelResponse(rf_class=rf_class, lg_class=lg_class)
