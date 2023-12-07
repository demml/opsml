# pylint: disable=no-member
# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""Base code for Onnx model conversion"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Protocol, Union

import numpy as np
import pandas as pd
import polars as pl
import pyarrow as pa
from numpy.typing import NDArray
from pydantic import BaseModel, ConfigDict, Field  # pylint: disable=no-name-in-module

ValidModelInput = Union[pd.DataFrame, np.ndarray, Dict[str, np.ndarray], pl.DataFrame]  # type: ignore
ValidSavedSample = Union[pa.Table, np.ndarray, Dict[str, np.ndarray]]  # type: ignore


class DataDtypes(str, Enum):
    STRING = "string"
    INT32 = "int32"
    INT64 = "int64"
    FLOAT32 = "float32"
    FLOAT64 = "float64"


class TrainedModelType(str, Enum):
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
    TrainedModelType.SKLEARN_ESTIMATOR,
    TrainedModelType.STACKING_ESTIMATOR,
    TrainedModelType.SKLEARN_PIPELINE,
    TrainedModelType.LGBM_REGRESSOR,
    TrainedModelType.LGBM_CLASSIFIER,
    TrainedModelType.XGB_REGRESSOR,
    TrainedModelType.CALIBRATED_CLASSIFIER,
]

LIGHTGBM_SUPPORTED_MODEL_TYPES = [
    TrainedModelType.LGBM_BOOSTER,
]

UPDATE_REGISTRY_MODELS = [
    TrainedModelType.LGBM_CLASSIFIER,
    TrainedModelType.LGBM_REGRESSOR,
    TrainedModelType.XGB_REGRESSOR,
]

AVAILABLE_MODEL_TYPES = list(TrainedModelType)


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
    shape: List[Any]


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

    def to_onnx(self) -> Dict[str, NDArray[Any]]:
        raise NotImplementedError

    def to_dataframe(self) -> pd.DataFrame:
        raise NotImplementedError

    def to_numpy(self, type_: str, values: Any) -> NDArray[Any]:
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
    def to_onnx(self) -> Dict[str, NDArray[Any]]:
        values = list(self.model_dump().values())
        for _, feature in self.feature_map.items():  # type: ignore[attr-defined]
            array = self.to_numpy(
                type_=feature.feature_type,
                values=values,
            )
        return {"predict": array.reshape(1, -1)}

    def to_dataframe(self) -> pd.DataFrame:
        raise NotImplementedError


class DictBase(Base):
    def to_onnx(self) -> Dict[str, NDArray[Any]]:
        feats = {}

        for feat, feat_val in self:
            array = self.to_numpy(
                type_=self.feature_map[feat].feature_type,  # type: ignore[attr-defined]
                values=feat_val,
            )
            feats[feat] = array.reshape(1, -1)
        return feats

    def to_dataframe(self) -> pd.DataFrame:
        return pd.DataFrame(self.model_dump(), index=[0])


class DeepLearningNumpyBase(Base):
    def to_onnx(self) -> Dict[str, NDArray[Any]]:
        feats = {}
        for feat, feat_val in self:
            array = self.to_numpy(type_=self.feature_map[feat].feature_type, values=feat_val)  # type: ignore[attr-defined]
            feats[feat] = np.expand_dims(array, axis=0)
        return feats

    def to_dataframe(self) -> pd.DataFrame:
        raise NotImplementedError


class DeepLearningDictBase(Base):
    """API base class for tensorflow/keras multi-input models.
    Multi-input models typically allow for a dictionary of arrays
    """

    def to_onnx(self) -> Dict[str, NDArray[Any]]:
        feats = {}
        for feat, feat_val in self:
            array = self.to_numpy(type_=self.feature_map[feat].feature_type, values=feat_val)  # type: ignore[attr-defined]
            feats[feat] = np.expand_dims(array, axis=0)

        return feats

    def to_dataframe(self) -> pd.DataFrame:
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
    onnx_model_def: Optional[OnnxModelDefinition] = None
    model_uri: str
    model_version: str
    model_team: str
    sample_data: Dict[str, Any]
    data_schema: ApiDataSchemas

    model_config = ConfigDict(protected_namespaces=("protect_",))


class ModelDownloadInfo(BaseModel):
    name: Optional[str] = None
    version: Optional[str] = None
    team: Optional[str] = None
    uid: Optional[str] = None


### Sklearn protocol stub
class BaseEstimator(Protocol):
    ...


### Onnx protocol stubs
class Graph:
    @property
    def output(self) -> Any:
        ...

    @property
    def input(self) -> Any:
        ...


class ModelProto(Protocol):
    ir_version: int
    producer_name: str
    producer_version: str
    domain: str
    model_version: int
    doc_string: str

    def SerializeToString(self) -> bytes:  # pylint: disable=invalid-name
        ...

    @property
    def graph(self) -> Graph:
        return Graph()


# proto class for type checking in order to prevent cyclic import
class Metadata(Protocol):
    @property
    def model_type(self) -> str:
        ...

    @property
    def model_class(self) -> str:
        ...

    @property
    def onnx_model_def(self) -> Optional[OnnxModelDefinition]:
        ...

    @property
    def additional_onnx_args(self) -> Optional[ExtraOnnxArgs]:
        ...

    @additional_onnx_args.setter
    def additional_onnx_args(self) -> None:
        ...

    @property
    def sample_data_type(self) -> str:
        ...


class ModelCard(Protocol):
    @property
    def metadata(self) -> Metadata:
        ...

    @property
    def trained_model(self) -> Any:
        ...

    @property
    def sample_input_data(self) -> ValidModelInput:
        ...

    @property
    def to_onnx(self) -> bool:
        ...
