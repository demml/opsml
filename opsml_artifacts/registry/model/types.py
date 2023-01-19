"""Base code for Onnx model conversion"""
from enum import Enum
from typing import Dict, Optional

import numpy as np
import pandas as pd
from pydantic import BaseModel, Field  # pylint: disable=no-name-in-module


class OnnxModelType(str, Enum):
    SKLEARN_PIPELINE = "sklearn_pipeline"
    SKLEARN_ESTIMATOR = "sklearn_estimator"
    STACKING_ESTIMATOR = "stackingestimator"
    LGBM_REGRESSOR = "lgbmregressor"
    LGBM_CLASSIFIER = "lgbmclassifier"
    XGB_REGRESSOR = "xgbregressor"
    LGBM_BOOSTER = "booster"


SKLEARN_SUPPORTED_MODEL_TYPES = [
    OnnxModelType.SKLEARN_ESTIMATOR,
    OnnxModelType.STACKING_ESTIMATOR,
    OnnxModelType.SKLEARN_PIPELINE,
    OnnxModelType.LGBM_REGRESSOR,
    OnnxModelType.LGBM_CLASSIFIER,
    OnnxModelType.XGB_REGRESSOR,
]

LIGHTGBM_SUPPORTED_MODEL_TYPES = [
    OnnxModelType.LGBM_BOOSTER,
]

UPDATE_REGISTRY_MODELS = [
    OnnxModelType.LGBM_CLASSIFIER,
    OnnxModelType.LGBM_REGRESSOR,
    OnnxModelType.XGB_REGRESSOR,
]

AVAILABLE_MODEL_TYPES = list(OnnxModelType)


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


class OnnxModelReturn(BaseModel):
    model_definition: ModelDefinition
    feature_dict: Dict[str, Feature]
    data_schema: Optional[Dict[str, str]]
    model_type: str
    data_type: str


class Base(BaseModel):
    def to_onnx(self):
        raise NotImplementedError

    def to_dataframe(self):
        raise NotImplementedError


class NumpyBase(Base):
    def to_onnx(self):
        return {
            "inputs": np.array(
                [list(self.dict().values())],
                np.float32,
            ).reshape(1, -1)
        }

    def to_dataframe(self):
        raise NotImplementedError


class PandasBase(Base):
    def to_onnx(self):
        feats = {}
        for feat, feat_val in self:
            if isinstance(feat_val, float):
                feats[feat] = np.array([[feat_val]]).astype(np.float32)
            elif isinstance(feat_val, int):
                feats[feat] = np.array([[feat_val]]).astype(np.int64)
            else:
                feats[feat] = np.array([[feat_val]])
        return feats

    def to_dataframe(self):
        return pd.DataFrame(self.dict(), index=[0])
