"""Base code for Onnx model conversion"""
from enum import Enum
from typing import Dict

import numpy as np
import pandas as pd
from pydantic import BaseModel, Field  # pylint: disable=no-name-in-module


class OnnxModelType(str, Enum):
    SKLEARN_PIPELINE = "sklearn_pipeline"
    SKLEARN_ESTIMATOR = "sklearn_estimator"
    LGBM_REGRESSOR = "lgbmregressor"
    XGB_REGRESSOR = "xgbregressor"
    STACKING_REGRESSOR = "stackingregressor"


class InputDataType(Enum):
    """Input put data associated with model"""

    PANDAS_DATAFRAME = pd.DataFrame
    NUMPY_ARRAY = np.ndarray


class OnnxDataProto(Enum):
    """Maps onnx element types to their data types"""

    INT32 = 6
    INT64 = 7
    FLOAT = 1
    STRING = 8


class Feature(BaseModel):
    feature_type: str
    shape: list


class DataDict(BaseModel):
    """Datamodel for feature info"""

    data_type: str
    features: Dict[str, Feature]


class ModelDefinition(BaseModel):
    model_bytes: bytes = Field(..., description="Encrypted onnx model bytes")
    encrypt_key: bytes = Field(..., description="Key to user or decrypting model definition")
