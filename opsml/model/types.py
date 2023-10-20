# pylint: disable=no-member
# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""Base code for Onnx model conversion"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Union

import numpy as np
import pandas as pd
import polars as pl
from numpy.typing import NDArray
from pydantic import BaseModel, Field, ConfigDict  # pylint: disable=no-name-in-module

InputData = Union[pd.DataFrame, NDArray, Dict[str, NDArray]]


class DataDtypes(str, Enum):
    STRING = "string"
    INT32 = "int32"
    INT64 = "int64"
    FLOAT32 = "float32"
    FLOAT64 = "float64"


class OnnxModelType(str, Enum):
    TRANSFORMER = "transformer"
    SKLEARN_PIPELINE = "sklearn_pipeline"
    SKLEARN_ESTIMATOR = "sklearn_estimator"
    STACKING_ESTIMATOR = "stackingestimator"
    CALIBRATED_CLASSIFIER = "calibratedclassifiercv"
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
    OnnxModelType.CALIBRATED_CLASSIFIER,
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
    POLARS_DATAFRAME = pl.DataFrame


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

    data_type: Optional[str] = None
    input_features: Dict[str, Feature]
    output_features: Dict[str, Feature]

    model_config = ConfigDict(frozen=False)


class OnnxModelDefinition(BaseModel):
    onnx_version: str = Field(..., description="Version of onnx model used to create proto")
    model_bytes: bytes = Field(..., description="Onnx model as serialized string")

    model_config = ConfigDict(protected_namespaces=("protect_",))


class ApiDataSchemas(BaseModel):
    model_data_schema: DataDict  # expected model inputs and outputs
    input_data_schema: Optional[Dict[str, Feature]] = None  # what the api can be fed

    model_config = ConfigDict(frozen=False, protected_namespaces=("protect_",))


class ModelReturn(BaseModel):
    model_definition: Optional[OnnxModelDefinition] = None
    api_data_schema: ApiDataSchemas
    model_type: str = "placeholder"

    model_config = ConfigDict(frozen=False, protected_namespaces=("protect_",))


class ExtraOnnxArgs(BaseModel):
    """
    input_names (List[str]): Optional list containing input names for model inputs.
    This is a PyTorch-specific attribute
    output_names (List[str]): Optional list containing output names for model outputs.
    This is a PyTorch-specific attribute
    dynamic_axes (Dictionary): Optional PyTorch attribute that defines dynamic axes
    constant_folding (bool): Whether to use constant folding optimization. Default is True
    """

    input_names: List[str]
    output_names: List[str]
    dynamic_axes: Optional[Dict[str, Dict[int, str]]] = None
    do_constant_folding: bool = True
    export_params: bool = True
    verbose: bool = False
    options: Optional[Dict[str, Any]] = None


class Base(BaseModel):
    model_config = ConfigDict(frozen=False)

    def to_onnx(self):
        raise NotImplementedError

    def to_dataframe(self):
        raise NotImplementedError

    def to_numpy(self, type_: str, values: Any):
        if type_ == OnnxDataProto.DOUBLE.name:
            return np.array(values, np.float64)

        if type_ == OnnxDataProto.FLOAT.name:
            return np.array(values, np.float32)

        if type_ == OnnxDataProto.INT32.name:
            return np.array(values, np.int32)

        if type_ == OnnxDataProto.INT64.name:
            return np.array(values, np.int64)

        return np.array(values, str)


class NumpyBase(Base):
    def to_onnx(self):
        values = list(self.model_dump().values())
        for _, feature in self.feature_map.items():  # there can only be one
            array = self.to_numpy(
                type_=feature.feature_type,
                values=values,
            )
            return {"predict": array.reshape(1, -1)}

    def to_dataframe(self):
        raise NotImplementedError


class DictBase(Base):
    def to_onnx(self):
        feats = {}

        for feat, feat_val in self:
            array = self.to_numpy(
                type_=self.feature_map[feat].feature_type,
                values=feat_val,
            )
            feats[feat] = array.reshape(1, -1)
        return feats

    def to_dataframe(self):
        return pd.DataFrame(self.model_dump(), index=[0])


class DeepLearningNumpyBase(Base):
    def to_onnx(self):
        feats = {}
        for feat, feat_val in self:
            array = self.to_numpy(type_=self.feature_map[feat].feature_type, values=feat_val)
            feats[feat] = np.expand_dims(array, axis=0)
        return feats

    def to_dataframe(self):
        raise NotImplementedError


class DeepLearningDictBase(Base):
    """API base class for tensorflow/keras multi-input models.
    Multi-input models typically allow for a dictionary of arrays
    """

    def to_onnx(self):
        feats = {}
        for feat, feat_val in self:
            array = self.to_numpy(type_=self.feature_map[feat].feature_type, values=feat_val)
            feats[feat] = np.expand_dims(array, axis=0)

        return feats

    def to_dataframe(self):
        raise NotImplementedError


class ApiSigTypes(Enum):
    UNDEFINED = Any
    INT = int
    INT32 = int
    INT64 = int
    NUMBER = float
    FLOAT = float
    FLOAT32 = float
    FLOAT64 = float
    DOUBLE = float
    STR = str
    STRING = str
    ARRAY = list


# this is partly a hack to get Seldons metadata to work
# seldon metadata only accepts float, bool, int
class SeldonSigTypes(str, Enum):
    UNDEFINED = "BYTES"
    INT = "INT32"
    INT32 = "INT32"
    INT64 = "INT64"
    NUMBER = "FP32"
    FLOAT = "FP32"
    FLOAT16 = "FP16"
    FLOAT32 = "FP32"
    FLOAT64 = "FP64"
    DOUBLE = "FP64"
    STR = "BYTES"


class PydanticDataTypes(Enum):
    NUMBER = float
    INTEGER = int
    STRING = str
    ANY = Any


@dataclass
class OnnxAttr:
    onnx_path: Optional[str] = None
    onnx_version: Optional[str] = None


class ModelMetadata(BaseModel):
    model_name: str
    model_type: str
    onnx_uri: Optional[str] = None
    onnx_version: Optional[str] = None
    model_uri: str
    model_version: str
    model_team: str
    sample_data: dict
    data_schema: ApiDataSchemas

    model_config = ConfigDict(protected_namespaces=("protect_",))


class ModelDownloadInfo(BaseModel):
    name: Optional[str] = None
    version: Optional[str] = None
    team: Optional[str] = None
    uid: Optional[str] = None
