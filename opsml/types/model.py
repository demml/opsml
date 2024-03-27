# pylint: disable=no-member
# mypy: disable-error-code="attr-defined"

# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""Base code for Onnx model conversion"""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol, Tuple, Union

import numpy as np
import pandas as pd
import polars as pl
import pyarrow as pa
from pydantic import BaseModel, ConfigDict, Field, field_validator

from opsml.helpers.logging import ArtifactLogger
from opsml.types.extra import Description
from opsml.types.huggingface import HuggingFaceORTModel
from opsml.version import __version__

logger = ArtifactLogger.get_logger()

# Dict[str, Any] is used because an input value can be a numpy, torch, or tensorflow tensor
ValidModelInput = Union[pd.DataFrame, np.ndarray, Dict[str, Any], pl.DataFrame, str]  # type: ignore
ValidSavedSample = Union[pa.Table, np.ndarray, Dict[str, np.ndarray]]  # type: ignore

try:
    import onnxruntime as rt

    OnnxInferenceSession = rt.InferenceSession

except ModuleNotFoundError:
    OnnxInferenceSession = Any

try:
    from huggingface import Pipeline
    from optimum.onnxruntime import ORTModel
except ModuleNotFoundError:
    ORTModel = Any
    Pipeline = Any


class DataDtypes(str, Enum):
    STRING = "string"
    INT32 = "int32"
    INT64 = "int64"
    FLOAT32 = "float32"
    FLOAT64 = "float64"


class TrainedModelType(str, Enum):
    TRANSFORMERS = "transformers"
    SKLEARN_PIPELINE = "Pipeline"
    SKLEARN_ESTIMATOR = "SklearnEstimator"
    STACKING_REGRESSOR = "StackingRegressor"
    STACKING_CLASSIFIER = "StackingClassifier"
    STACKING_ESTIMATOR = "StackingEstimator"
    CALIBRATED_CLASSIFIER = "CalibratedClassifierCV"
    LGBM_REGRESSOR = "LGBMRegressor"
    LGBM_CLASSIFIER = "LGBMClassifier"
    XGB_REGRESSOR = "XGBRegressor"
    XGB_CLASSIFIER = "XGBClassifier"
    XGB_BOOSTER = "Booster"
    LGBM_BOOSTER = "Booster"
    TF_KERAS = "keras"
    PYTORCH = "pytorch"
    PYTORCH_LIGHTNING = "pytorch_lightning"
    CATBOOST = "CatBoost"
    VOWPAL = "VowpalWabbit"


SKLEARN_SUPPORTED_MODEL_TYPES = [
    TrainedModelType.SKLEARN_ESTIMATOR,
    TrainedModelType.STACKING_REGRESSOR,
    TrainedModelType.STACKING_CLASSIFIER,
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


class HuggingFaceModuleType(str, Enum):
    PRETRAINED_MODEL = "transformers.modeling_utils.PreTrainedModel"
    TRANSFORMER_MODEL = "transformers.models"
    TRANSFORMER_PIPELINE = "transformers.pipelines"


class Feature(BaseModel):
    feature_type: str
    shape: Tuple[Any, ...]


class DataSchema(BaseModel):
    """Datamodel for feature info"""

    data_type: Optional[str] = None
    input_features: Optional[Dict[str, Feature]] = None
    output_features: Optional[Dict[str, Feature]] = None
    onnx_input_features: Optional[Dict[str, Feature]] = None
    onnx_output_features: Optional[Dict[str, Feature]] = None
    onnx_data_type: Optional[str] = None
    onnx_version: Optional[str] = None

    model_config = ConfigDict(frozen=False)


class OnnxModel(BaseModel):
    onnx_version: str = Field(..., description="Version of onnx model used to create proto")
    sess: Union[OnnxInferenceSession, ORTModel, Pipeline] = Field(default=None, description="Onnx model session")  # type: ignore

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def sess_to_path(self, path: Path) -> None:
        """Helper method for taking existing onnx model session and saving to path

        Args:
            path:
                Path to save onnx model
        """

        if not isinstance(self.sess, rt.InferenceSession):
            return

        logger.info("Saving existing onnx model")

        if self.sess._model_bytes:  # pylint: disable=protected-access
            path.write_bytes(self.sess._model_bytes)  # pylint: disable=protected-access

        else:
            # copy model path to new path
            from fsspec.implementations.local import LocalFileSystem

            file_sys = LocalFileSystem()
            lpath = self.sess._model_path  # pylint: disable=protected-access
            file_sys.copy(lpath, str(path))

        return


class ModelReturn(BaseModel):
    onnx_model: Optional[OnnxModel] = None
    data_schema: DataSchema

    model_config = ConfigDict(frozen=False, protected_namespaces=("protect_",))


class TorchSaveArgs(BaseModel):
    """Torch save arguments.

    Args:
        as_state_dict:
            Indicates to save the torch model in state_dict format. If True, the model
            architecture will need to be provided at load time.
    """

    as_state_dict: bool = False


class TorchOnnxArgs(BaseModel):
    """Optional arguments to pass to torch when converting to onnx

    Args:
        input_names:
            Optional list containing input names for model inputs.
        output_names:
            Optional list containing output names for model outputs.
        dynamic_axes:
            Optional PyTorch attribute that defines dynamic axes
        constant_folding:
            Whether to use constant folding optimization. Default is True
    """

    input_names: List[str]
    output_names: List[str]
    dynamic_axes: Optional[Dict[str, Dict[int, str]]] = None
    do_constant_folding: bool = True
    export_params: bool = True
    verbose: bool = False
    options: Optional[Dict[str, Any]] = None


class HuggingFaceOnnxArgs(BaseModel):
    """Optional Args to use with a huggingface model

    Args:
        ort_type:
            Optimum onnx class name
        provider:
            Onnx runtime provider to use
        config:
            Optional optimum config to use
    """

    ort_type: str
    provider: str = "CPUExecutionProvider"
    quantize: bool = False
    config: Optional[Any] = None

    @field_validator("ort_type", mode="before")
    @classmethod
    def check_ort_type(cls, ort_type: str) -> str:
        """Validates onnx runtime model type"""
        if ort_type not in list(HuggingFaceORTModel):
            raise ValueError(f"Optimum model type {ort_type} is not supported")
        return ort_type

    @field_validator("config", mode="before")
    @classmethod
    def check_config(cls, config: Optional[Any] = None) -> Optional[Any]:
        """Check that optimum config is valid"""

        if config is None:
            return config

        from optimum.onnxruntime import (
            AutoQuantizationConfig,
            ORTConfig,
            QuantizationConfig,
        )

        assert isinstance(
            config,
            (
                AutoQuantizationConfig,
                ORTConfig,
                QuantizationConfig,
            ),
        ), "config must be a valid optimum config"

        return config


class ModelCardMetadata(BaseModel):
    """Create modelcard metadata

    Args:
        interface_type:
            Type of interface
        description:
            Description for your model
        data_schema:
            Data schema for your model
        runcard_uid:
            RunCard associated with the ModelCard
        pipelinecard_uid:
            Associated PipelineCard
        auditcard_uid:
            Associated AuditCard
    """

    interface_type: str = ""
    description: Description = Description()
    data_schema: DataSchema = DataSchema()
    runcard_uid: Optional[str] = None
    pipelinecard_uid: Optional[str] = None
    auditcard_uid: Optional[str] = None

    model_config = ConfigDict(protected_namespaces=("protect_",))


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
    """Model metadata associated with all registered models

    Args:
        model_name:
            Name of model
        model_class:
            Name of model class
        model_type:
            Type of model
        model_interface:
            Type of interface
        onnx_uri:
            URI to onnx model
        onnx_version:
            Version of onnx model
        model_uri:
            URI to model
        model_version:
            Version of model
        model_repository:
            Model repository
        sample_data_uri:
            URI to sample data
        opsml_version:
            Opsml version
        data_schema:
            Data schema for model
        preprocessor_uri: (only present if preprocessor is used)
            URI to preprocessor
        preprocessor_name: (only present if preprocessor is used)
            Name of preprocessor
        quantized_model_uri: (only present if huggingface model is quantized)
            URI to huggingface quantized onnx model
        tokenizer_uri: (only present if huggingface tokenizer is used)
            URI to tokenizer
        tokenizer_name: (only present if huggingface is used)
            Name of tokenizer
        feature_extractor_uri: (only present if huggingface feature extractor is used)
            URI to feature extractor
        feature_extractor_name: (only present if huggingface feature_extractor is used)
            Name of feature extractor
    """

    model_name: str
    model_class: str
    model_type: str
    model_interface: str
    onnx_uri: Optional[str] = None
    onnx_version: Optional[str] = None
    model_uri: str
    model_version: str
    model_repository: str
    sample_data_uri: str
    opsml_version: str = __version__
    data_schema: DataSchema

    model_config = ConfigDict(
        protected_namespaces=("protect_",),
        extra="allow",
    )


# Sklearn protocol stub
class BaseEstimator(Protocol): ...


# Onnx protocol stubs
class Graph:
    @property
    def output(self) -> Any: ...

    @property
    def input(self) -> Any: ...


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


class ModelType:
    @staticmethod
    def get_type() -> str:
        raise NotImplementedError

    @staticmethod
    def validate(model_class_name: str) -> bool:
        raise NotImplementedError


class SklearnPipeline(ModelType):
    @staticmethod
    def get_type() -> str:
        return TrainedModelType.SKLEARN_PIPELINE.value

    @staticmethod
    def validate(model_class_name: str) -> bool:
        return model_class_name == "Pipeline"


class SklearnCalibratedClassifier(ModelType):
    @staticmethod
    def get_type() -> str:
        return TrainedModelType.CALIBRATED_CLASSIFIER.value

    @staticmethod
    def validate(model_class_name: str) -> bool:
        return model_class_name == "CalibratedClassifierCV"


class SklearnStackingEstimator(ModelType):
    @staticmethod
    def get_type() -> str:
        return TrainedModelType.STACKING_ESTIMATOR.value

    @staticmethod
    def validate(model_class_name: str) -> bool:
        return model_class_name in ["StackingRegressor", "StackingClassifier"]


class LightGBMRegressor(ModelType):
    @staticmethod
    def get_type() -> str:
        return TrainedModelType.LGBM_REGRESSOR.value

    @staticmethod
    def validate(model_class_name: str) -> bool:
        return model_class_name == "LGBMRegressor"


class LightGBMClassifier(ModelType):
    @staticmethod
    def get_type() -> str:
        return TrainedModelType.LGBM_CLASSIFIER.value

    @staticmethod
    def validate(model_class_name: str) -> bool:
        return model_class_name == "LGBMClassifier"


class XGBRegressor(ModelType):
    @staticmethod
    def get_type() -> str:
        return TrainedModelType.XGB_REGRESSOR.value

    @staticmethod
    def validate(model_class_name: str) -> bool:
        return model_class_name == "XGBRegressor"


class XGBClassifier(ModelType):
    @staticmethod
    def get_type() -> str:
        return TrainedModelType.XGB_CLASSIFIER.value

    @staticmethod
    def validate(model_class_name: str) -> bool:
        return model_class_name == "XGBClassifier"


class LightGBMBooster(ModelType):
    @staticmethod
    def get_type() -> str:
        return TrainedModelType.LGBM_BOOSTER.value

    @staticmethod
    def validate(model_class_name: str) -> bool:
        return model_class_name == "Booster"


class ModelCard(Protocol):
    @property
    def metadata(self) -> ModelCardMetadata: ...

    @property
    def model(self) -> Any: ...

    @property
    def to_onnx(self) -> bool: ...
