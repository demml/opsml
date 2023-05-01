"""Base code for Onnx model conversion"""
from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd
from numpy.typing import NDArray
from pydantic import BaseModel, Field  # pylint: disable=no-name-in-module
from skl2onnx.common.data_types import (
    DoubleTensorType,
    FloatTensorType,
    Int32TensorType,
    Int64TensorType,
    StringTensorType,
    TensorType,
)

InputData = Union[pd.DataFrame, NDArray, Dict[str, NDArray]]


class DataDtypes(str, Enum):
    STRING = "string"
    INT32 = "int32"
    INT64 = "int64"
    FLOAT32 = "float32"
    FLOAT64 = "float64"


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


class OnnxModelDefinition(BaseModel):
    onnx_version: str = Field(..., description="Version of onnx model used to create proto")
    model_bytes: bytes = Field(..., description="Onnx model as serialized string")


class ModelReturn(BaseModel):
    model_definition: Optional[OnnxModelDefinition] = None
    onnx_input_features: Dict[str, Feature]  # change this later
    onnx_output_features: Dict[str, Feature]  # change this later
    data_schema: Optional[Dict[str, Feature]] = None
    model_type: str = "placeholder"
    data_type: str = "placeholder"

    class Config:
        allow_mutation = True


class Base(BaseModel):
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
        values = list(self.dict().values())
        for _, type_ in self.feature_map.items():  # there can only be one
            array = self.to_numpy(type_=type_, values=values)
            return {"inputs": array.reshape(1, -1)}

    def to_dataframe(self):
        raise NotImplementedError


class DictBase(Base):
    def to_onnx(self):
        feats = {}

        for feat, feat_val in self:
            array = self.to_numpy(type_=self.feature_map[feat], values=feat_val)
            feats[feat] = array.reshape(1, -1)
        return feats

    def to_dataframe(self):
        return pd.DataFrame(self.dict(), index=[0])


class DeepLearningNumpyBase(Base):
    def to_onnx(self):
        feats = {}
        for feat, feat_val in self:
            array = self.to_numpy(type_=self.feature_map[feat], values=feat_val)
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
            array = self.to_numpy(type_=self.feature_map[feat], values=feat_val)
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


@dataclass
class TorchOnnxArgs:
    """
    input_names (List[str]): Optional list containing input names for model inputs.
    This is a PyTorch-specific attribute
    output_names (List[str]): Optional list containing output names for model outputs.
    This is a PyTorch-specific attribute
    dynamic_axes (Dictionary): Optional PyTorch attribute that defines dynamic axes
    constant_folding (bool): Whether to use constant folding optimiation. Default is True
    """

    input_names: List[str]
    output_names: List[str]
    dynamic_axes: Optional[Dict[str, Dict[int, str]]] = None
    do_constant_folding: bool = True
    export_params: bool = True
    verbose: bool = False

    def to_dict(self):
        return asdict(self)


class ModelApiDef(BaseModel):
    model_name: str
    model_type: str
    onnx_definition: bytes
    onnx_version: str
    model_version: str
    data_dict: DataDict
    sample_data: dict
    data_schema: Optional[dict] = None

    class Config:
        json_encoders = {bytes: lambda bs: bs.hex()}
        allow_extra = True


class ModelDownloadInfo(BaseModel):
    name: Optional[str] = None
    version: Optional[str] = None
    team: Optional[str] = None
    uid: Optional[str] = None


class BaseTensorType:
    def __init__(self, dtype: str, input_shape: Union[Tuple[int, ...], List[int]]):
        self.input_shape = input_shape
        self.dtype = dtype

    def get_tensor_type(self) -> TensorType:
        raise NotImplementedError

    @staticmethod
    def validate(dtype: str) -> bool:
        raise NotImplementedError


class Float32Tensor(BaseTensorType):
    def get_tensor_type(self) -> FloatTensorType:
        return FloatTensorType([None, *self.input_shape])

    @staticmethod
    def validate(dtype: str) -> bool:
        return dtype == DataDtypes.FLOAT32


class Float64Tensor(BaseTensorType):
    def get_tensor_type(self) -> DoubleTensorType:
        return DoubleTensorType([None, *self.input_shape])

    @staticmethod
    def validate(dtype: str) -> bool:
        return dtype == DataDtypes.FLOAT64


class Int32Tensor(BaseTensorType):
    def get_tensor_type(self) -> Int32TensorType:
        return Int32TensorType([None, *self.input_shape])

    @staticmethod
    def validate(dtype: str) -> bool:
        return dtype == DataDtypes.INT32


class Int64Tensor(BaseTensorType):
    def get_tensor_type(self) -> Int64TensorType:
        return Int64TensorType([None, *self.input_shape])

    @staticmethod
    def validate(dtype: str) -> bool:
        return dtype == DataDtypes.INT64


class StringTensor(BaseTensorType):
    def get_tensor_type(self) -> StringTensorType:
        return StringTensorType([None, *self.input_shape])

    @staticmethod
    def validate(dtype: str) -> bool:
        return dtype == DataDtypes.STRING


def get_onnx_tensor_spec(
    dtype: str,
    input_shape: Union[Tuple[int, ...], List[int]],
) -> TensorType:
    """Takes a dtype and input shape and returns Onnx Tensor type proto to be
    used with Onnx model

    Args:
        dtype (str): Dtype of data
        input_shape (list(int)): Input shape of data

    Returns:
        Onnx TensorType
    """
    tensor_type = next(
        (
            tensor_type
            for tensor_type in BaseTensorType.__subclasses__()
            if tensor_type.validate(
                dtype=dtype,
            )
        ),
        StringTensor,
    )

    return tensor_type(
        dtype=dtype,
        input_shape=input_shape,
    ).get_tensor_type()
