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
    TF_KERAS = "keras"


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

    UNDEFINED = 0
    FLOAT = 1
    UINT8 = 2
    INT8 = 3
    UINT16 = 4
    INT16 = 5
    INT32 = 6
    INT64 = 7
    STRING = 8
    BOOL = 9
    FLOAT16 = 10
    DOUBLE = 11
    UINT32 = 12
    UINT64 = 13
    COMPLEX64 = 14
    COMPLEX128 = 15
    BFLOAT16 = 16


class Feature(BaseModel):
    feature_type: str
    shape: list


class DataDict(BaseModel):
    """Datamodel for feature info"""

    data_type: str
    input_features: Dict[str, Feature]
    output_features: Dict[str, Feature]


class ModelDefinition(BaseModel):
    model_bytes: bytes = Field(..., description="Encrypted onnx model bytes")
    encrypt_key: bytes = Field(..., description="Key to user or decrypting model definition")


class OnnxModelReturn(BaseModel):
    model_definition: ModelDefinition
    onnx_input_features: Dict[str, Feature]
    onnx_output_features: Dict[str, Feature]
    data_schema: Optional[Dict[str, str]]
    model_type: str
    data_type: str


class Base(BaseModel):
    def to_onnx(self):
        raise NotImplementedError

    def to_dataframe(self):
        raise NotImplementedError


class APIBase(Base):
    def to_onnx(self):
        return {
            feat: np.array(
                feat_val,
                np.float32,
            ).reshape(1, -1)
            for feat, feat_val in self
        }

    def to_dataframe(self):
        raise NotImplementedError


class ApiBase(Base):
    def to_onnx(self):
        feats = {}
        for feat, feat_val in self:
            if isinstance(feat_val, float):
                feats[feat] = np.array(feat_val, np.float32).reshape(1, -1)
            elif isinstance(feat_val, int):
                feats[feat] = np.array(feat_val, np.int64).reshape(1, -1)
            else:
                feats[feat] = np.array(feat_val).reshape(1, -1)
        return feats


class ApiSigTypes(Enum):
    FLOAT = float
    INT = int
    STR = str
