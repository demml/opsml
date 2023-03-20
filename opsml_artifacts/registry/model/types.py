"""Base code for Onnx model conversion"""
from enum import Enum
from typing import Any, Dict, List, Optional

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
    PYTORCH = "pytorch"


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
    DICT = dict


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
    onnx_version: str = Field(..., description="Version of onnx model used to create proto")
    model_bytes: bytes = Field(..., description="Onnx model as serialized string")


class OnnxModelReturn(BaseModel):
    model_definition: ModelDefinition
    onnx_input_features: Dict[str, Feature]
    onnx_output_features: Dict[str, Feature]
    data_schema: Optional[Dict[str, Feature]]
    model_type: str = "None"
    data_type: str = "None"

    class Config:
        allow_mutation = True


class Base(BaseModel):
    def to_onnx(self):
        raise NotImplementedError

    def to_dataframe(self):
        raise NotImplementedError


class NumpyBase(Base):
    def to_onnx(self):
        return {
            "inputs": np.array(
                list(self.dict().values()),
                np.float32,
            ).reshape(1, -1)
        }

    def to_dataframe(self):
        raise NotImplementedError


class DictBase(Base):
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

    def to_dataframe(self):
        return pd.DataFrame(self.dict(), index=[0])


class DeepLearningNumpyBase(Base):
    def to_onnx(self):
        return {feat: np.expand_dims(np.array(feat_val, np.float32), axis=0) for feat, feat_val in self}

    def to_dataframe(self):
        raise NotImplementedError


class DeepLearningDictBase(Base):
    """API base class for tensorflow/keras multi-input models.
    Multi-input models typically allow for a dictionary of arrays
    """

    def to_onnx(self):
        feats = {}
        for feat, feat_val in self:
            if isinstance(feat_val[0], float):
                feats[feat] = np.expand_dims(np.array(feat_val, np.float32), axis=0)
            elif isinstance(feat_val[0], int):
                feats[feat] = np.expand_dims(np.array(feat_val, np.int64), axis=0)
            else:
                feats[feat] = np.expand_dims(np.array(feat_val), axis=0)
        return feats

    def to_dataframe(self):
        raise NotImplementedError


class ApiSigTypes(Enum):
    UNDEFINED = Any
    INT = int
    INT32 = int
    INT64 = int
    FLOAT = float
    FLOAT32 = float
    FLOAT64 = float
    STR = str


class TorchOnnxArgs(BaseModel):
    """
    tinput_names (List[str]): Optional list containing input names for model inputs.
    This is a PyTorch-specific attribute
    output_names (List[str]): Optional list containing output names for model outputs.
    This is a PyTorch-specific attribute
    dynamic_axes (Dictionary): Optional PyTorch attribute that defines dynamic axes
    """

    input_names: List[str] = ["inputs"]
    output_names: List[str] = ["outputs"]
    dynamic_axes: Dict[str, Dict[int, str]] = {"inputs": {0: "bs"}}


class ModelApiDef(BaseModel):
    model_name: str
    model_type: str
    onnx_definition: bytes
    onnx_version: str
    input_signature: dict
    output_signature: dict
    model_version: str
    data_dict: dict
    sample_data: dict

    class Config:
        json_encoders = {bytes: lambda bs: bs.hex()}
        allow_extra = True


class ModelDownloadInfo(BaseModel):
    name: Optional[str] = None
    version: Optional[str] = None
    team: Optional[str] = None
    uid: Optional[str] = None
