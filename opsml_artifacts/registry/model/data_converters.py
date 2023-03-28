# pylint: disable=[import-outside-toplevel,import-error]
"""Code for generating Onnx Models"""
from typing import Any, Dict, List, Optional, Tuple, Union, cast

from numpy.typing import NDArray
import numpy as np
import pandas as pd

from opsml_artifacts.helpers.logging import ArtifactLogger
from opsml_artifacts.registry.model.types import (
    AVAILABLE_MODEL_TYPES,
    Feature,
    ModelDefinition,
    OnnxModelType,
    TorchOnnxArgs,
    DataDtypes,
    get_onnx_tensor_spec,
    ModelData,
    InputDataType,
    ModelInfo,
)

logger = ArtifactLogger.get_logger(__name__)

ModelConvertOutput = Tuple[ModelDefinition, Dict[str, Feature], Optional[Dict[str, Feature]]]


def get_dtype_shape(data: NDArray):

    return str(data.dtype), data.shape[1:]


def get_feature_info(type_: str, shape: List[Optional[int]]) -> Feature:
    if "int" in type_:
        return Feature(feature_type="INT", shape=shape)
    elif "float" in type_:
        return Feature(feature_type="FLOAT", shape=shape)
    else:
        return Feature(feature_type="STR", shape=shape)


class DataConverter:
    def __init__(self, model_info: ModelInfo):

        self.model_info = model_info
        self.input_name = "inputs"

    def get_data_schema(self) -> Optional[Dict[str, Feature]]:
        """Gets schema from data.
        Reproduces onnx_data_types in some instances
        """
        raise NotImplementedError

    def get_onnx_data_types(self) -> List[Any]:
        """Infers data types from training data"""

        dtype, shape = get_dtype_shape(data=self.model_info.input_data)
        spec = get_onnx_tensor_spec(dtype=dtype, input_shape=shape)
        return [(self.input_name, spec)]

    def convert_data_to_onnx(self) -> Dict[str, Any]:
        """Converts data to onnx schema"""
        raise NotImplementedError

    def _get_onnx_dataframe_schema(self) -> List[Any]:
        """Creates an Onnx feature spec from a pandas dataframe"""

        data = cast(pd.DataFrame, self.model_info.input_data)

        inputs = []
        for key, val in zip(data.columns, data.dtypes):
            spec = get_onnx_tensor_spec(dtype=str(val), input_shape=[1])
            inputs.append((key, spec))
        return inputs

    def _get_py_dataframe_schema(self) -> Dict[str, Feature]:
        """Creates feature dictionary based on dataframe schema"""

        data = cast(pd.DataFrame, self.model_info.input_data)

        feature_dict: Dict[str, Feature] = {}
        for feature, feature_type in zip(data.columns, data.dtypes):
            feature_dict[feature] = get_feature_info(type_=str(feature_type), shape=[None, 1])

        return feature_dict

    def convert_float64_to_float32(self):
        data = self.model_info.input_data
        if isinstance(data, pd.DataFrame):
            for feature, feature_type in zip(data.columns, data.dtypes):
                if DataDtypes.FLOAT64 in str(feature_type):
                    data[feature] = data[feature].astype(np.float32)

        elif isinstance(data, np.ndarray):
            dtype = str(data.dtype)
            if dtype == DataDtypes.FLOAT64:
                self.model_info.input_data = data.astype(np.float32, copy=False)

        elif isinstance(data, dict):
            for key, value in data.items():
                dtype = str(value.dtype)
                if dtype == DataDtypes.FLOAT64:
                    self.model_info.input_data[key] = data.astype(np.float32, copy=False)

    def convert_all_to_float32(self):
        data = self.model_info.input_data
        if isinstance(data, pd.DataFrame):
            for feature, feature_type in zip(data.columns, data.dtypes):
                if str(feature_type) != DataDtypes.STRING:
                    data[feature] = data[feature].astype(np.float32)

        elif isinstance(data, np.ndarray):
            dtype = str(data.dtype)
            if dtype != DataDtypes.STRING:
                self.model_info.input_data = data.astype(np.float32, copy=False)

        elif isinstance(data, dict):
            for key, value in data.items():
                dtype = str(value.dtype)
                if dtype != DataDtypes.STRING:
                    self.model_info.input_data[key] = data.astype(np.float32, copy=False)

    @staticmethod
    def validate(model_info: ModelInfo) -> bool:
        """Validate data and model types"""
        raise NotImplementedError


class NumpyOnnxConverter(DataConverter):
    def get_data_schema(self) -> Optional[Dict[str, Feature]]:
        return None

    def convert_data_to_onnx(self) -> Dict[str, Any]:
        return {self.input_name: self.model_info.input_data}

    @staticmethod
    def validate(model_info: ModelInfo) -> bool:
        if model_info.data_type == InputDataType.NUMPY_ARRAY.value:

            if model_info.model_type in AVAILABLE_MODEL_TYPES and model_info.model_type not in [
                OnnxModelType.TF_KERAS,
                OnnxModelType.PYTORCH,
            ]:
                return True
        return False


class PandasOnnxConverter(DataConverter):
    def get_data_schema(self) -> Optional[Dict[str, Feature]]:
        return self._get_py_dataframe_schema()

    def get_onnx_data_types(self) -> List[Any]:
        """Creates a single type spec for a pandas dataframe.
        This is used for models that supply a dataframe, but are trained with an array.

        Example:
            # X_train is a dataframe
            reg = lgb.LGBMClassifier(n_estimators=3)
            reg.fit(X_train.to_numpy(), y_train)

        """
        data = cast(pd.DataFrame, self.model_info.input_data)
        input_shape = data.shape[1:]
        dtype = str(data.to_numpy().dtype)

        spec = get_onnx_tensor_spec(dtype=dtype, input_shape=input_shape)

        return [(self.input_name, spec)]

    def convert_data_to_onnx(self) -> Dict[str, Any]:
        data = cast(pd.DataFrame, self.model_info.input_data)
        return {self.input_name: data.to_numpy()}

    @staticmethod
    def validate(model_info: ModelInfo) -> bool:

        return (
            model_info.data_type == InputDataType.PANDAS_DATAFRAME.value
            and model_info.model_type != OnnxModelType.SKLEARN_PIPELINE
        )


class PandasPipelineOnnxConverter(DataConverter):
    def get_data_schema(self) -> Optional[Dict[str, Feature]]:
        return self._get_py_dataframe_schema()

    def get_onnx_data_types(self) -> List[Any]:
        return self._get_onnx_dataframe_schema()

    def convert_data_to_onnx(self) -> Dict[str, Any]:

        """Converts pandas dataframe associated with SKLearn pipeline"""

        data = cast(pd.DataFrame, self.model_info.input_data)

        data_columns = data.columns
        rows_shape = data.shape[0]
        dtypes = data.dtypes

        inputs = {col: data[col].values for col in data_columns}

        # refactor later
        for col, col_type in zip(data_columns, dtypes):
            if DataDtypes.INT32 in str(col_type):
                inputs[col] = inputs[col].astype(np.int32)
            elif DataDtypes.INT64 in str(col_type):
                inputs[col] = inputs[col].astype(np.int64)
            elif DataDtypes.FLOAT32 in str(col_type):
                inputs[col] = inputs[col].astype(np.float32)
            elif DataDtypes.FLOAT64 in str(col_type):
                inputs[col] = inputs[col].astype(np.float64)

        for col in inputs:
            inputs[col] = inputs[col].reshape((rows_shape, 1))

        return inputs

    @staticmethod
    def validate(model_info: ModelInfo) -> bool:
        return (
            model_info.data_type == InputDataType.PANDAS_DATAFRAME.value
            and model_info.model_type == OnnxModelType.SKLEARN_PIPELINE
        )


class TensorflowDictOnnxConverter(DataConverter):
    def get_data_schema(self) -> Optional[Dict[str, Feature]]:
        return None

    def get_onnx_data_types(self) -> List[Any]:
        """Takes multi input model spec and gets input shape and type for
        tensorspec
        """
        import tensorflow as tf

        model = cast(tf.keras.Model, self.model_info.model)
        spec = []
        for input_ in model.inputs:
            shape_, dtype = list(input_.shape), input_.dtype
            shape_[0] = None
            input_name = getattr(input_, "name", "inputs")
            spec.append(tf.TensorSpec(shape_, dtype, name=input_name))
        return spec

    def convert_data_to_onnx(self) -> Dict[str, Any]:

        onnx_data = {}
        for key, val in self.model_info.input_data.items():
            onnx_data[key] = val.astype(np.float32)
        return onnx_data

    @staticmethod
    def validate(model_info: ModelInfo) -> bool:
        return model_info.data_type == InputDataType.DICT.value and model_info.model_type == OnnxModelType.TF_KERAS


class TensorflowNumpyOnnxConverter(DataConverter):
    def get_data_schema(self) -> Optional[Dict[str, Feature]]:
        return None

    def get_onnx_data_types(self) -> List[Any]:
        """Takes model spec and gets input shape and type for
        tensorspec
        """
        import tensorflow as tf

        model = cast(tf.keras.Model, self.model_info.model)
        input_ = model.inputs[0]
        shape_, dtype = list(input_.shape), input_.dtype
        shape_[0] = None
        self.input_name = getattr(input_, "name", "inputs")

        return [tf.TensorSpec(shape_, dtype, name=self.input_name)]

    def convert_data_to_onnx(self) -> Dict[str, Any]:
        return {self.input_name: self.model_info.input_data.astype(np.float32)}

    @staticmethod
    def validate(model_info: ModelInfo) -> bool:
        return (
            model_info.data_type == InputDataType.NUMPY_ARRAY.value and model_info.model_type == OnnxModelType.TF_KERAS
        )


class PyTorchOnnxDataConverter(DataConverter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.input_name = self.additional_model_args.input_names[0]

    def get_data_schema(self) -> Optional[Dict[str, Feature]]:
        return None

    def convert_data_to_onnx(self) -> Dict[str, Any]:
        return {self.input_name: self.model_info.input_data.astype(np.float32)}

    @staticmethod
    def validate(model_info: ModelInfo) -> bool:
        return (
            model_info.data_type == InputDataType.NUMPY_ARRAY.value and model_info.model_type == OnnxModelType.PYTORCH
        )


class PyTorchOnnxDictConverter(DataConverter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.input_names = self.additional_model_args.input_names

    def get_data_schema(self) -> Optional[Dict[str, Feature]]:
        return None

    def get_onnx_data_types(self) -> List[Any]:
        specs = []

        for input_ in self.input_names:
            data = self.model_info.input_data[input_]
            dtype, shape = get_dtype_shape(data=data)
            spec = get_onnx_tensor_spec(dtype=dtype, input_shape=shape)
            specs.append((input_, spec))

        return specs

    def convert_data_to_onnx(self) -> Dict[str, Any]:
        """Convert Pytorch dictionary sample to onnx format"""

        onnx_data = {}
        for key, val in self.model_info.input_data.items():
            dtype, _ = get_dtype_shape(data=val)

            if DataDtypes.INT32 in dtype:
                onnx_data[key] = val.astype(np.int32)
            elif DataDtypes.INT64 in dtype:
                onnx_data[key] = val.astype(np.int64)
            elif DataDtypes.FLOAT32 in dtype:
                onnx_data[key] = val.astype(np.float32)
            else:
                onnx_data[key] = val.astype(np.float64)

        return onnx_data

    @staticmethod
    def validate(model_info: ModelInfo) -> bool:
        return model_info.data_type == InputDataType.DICT.value and model_info.model_type == OnnxModelType.PYTORCH


class OnnxDataConverter:
    def __init__(self, model_info: ModelInfo):

        self.model_info = model_info
        self.converter = self._get_converter()

    def _get_converter(self):

        converter = next(
            (
                converter
                for converter in DataConverter.__subclasses__()
                if converter.validate(model_info=self.model_info)
            )
        )

        return converter(model_info=self.model_info)

    def convert_data(self) -> Dict[str, Any]:
        """Takes input data sample and model type and converts data to onnx format"""

        return self.converter.convert_data_to_onnx()

    def get_data_types(self) -> Tuple[List[Any], Optional[Dict[str, Feature]]]:
        """Takes input data sample and model type and converts data to onnx format"""

        onnx_types = self.converter.get_onnx_data_types()
        py_data_types = self.converter.get_data_schema()
        return onnx_types, py_data_types
