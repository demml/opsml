import json
from functools import cached_property
from typing import Any, List

import numpy as np
from core.config import Config
from numpy.typing import NDArray
from onnxruntime import InferenceSession
from pydantic import BaseModel, ConfigDict

from opsml import ModelMetadata


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
        with Config.METADATA_PATH.open("r") as f:
            self.metadata = ModelMetadata(**json.load(f))
        self.onnx_model = InferenceSession(Config.MODEL_PATH)

    @cached_property
    def input_name(self) -> str:
        """Returns the names of the input features for the model"""
        return list(self.metadata.data_schema.onnx_input_features.keys())[0]

    def predict(self, features: NDArray[np.float32]) -> List[Any]:
        """Predicts the target variable for a given set of features

        Args:
            features:
                A numpy array of features

        Returns:
            Predicted value
        """
        return self.onnx_model.run(None, {self.input_name: features})
