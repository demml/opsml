from functools import cached_property
from typing import Any, List, cast

import numpy as np
from core.config import Config
from numpy.typing import NDArray
from onnxruntime import InferenceSession
from pydantic import BaseModel, ConfigDict

from opsml import ModelLoader


class HealthCheckResult(BaseModel):
    is_alive: bool


class ModelRequest(BaseModel):
    features: List[float]

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "features": [1.0, 2.0, 3.0, 4.0, 5.0],
            }
        }
    )


class ModelResponse(BaseModel):
    prediction: List[float]


class OnnxModel:
    def __init__(self):
        self.loader = ModelLoader(Config.MODEL_PATH)
        self.loader.load_onnx_model()

    @cached_property
    def model(self) -> InferenceSession:
        return cast(InferenceSession, self.loader.onnx_model.sess)

    def predict(self, features: NDArray[np.float32]) -> List[Any]:
        """Predicts the target variable for a given set of features

        Args:
            features:
                A numpy array of features

        Returns:
            Predicted value
        """
        return self.model.run(None, {"predict": features})
