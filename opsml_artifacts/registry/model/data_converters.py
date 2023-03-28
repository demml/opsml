# pylint: disable=[import-outside-toplevel,import-error]
"""Code for generating Onnx Models"""
from typing import Any, Dict, List, Optional, Tuple, cast

import numpy as np
import pandas as pd
from numpy.typing import NDArray

from opsml_artifacts.helpers.logging import ArtifactLogger
from opsml_artifacts.registry.model.types import (
    AVAILABLE_MODEL_TYPES,
    DataDtypes,
    Feature,
    InputDataType,
    ModelDefinition,
    ModelInfo,
    OnnxModelType,
    TorchOnnxArgs,
    get_onnx_tensor_spec,
    ModelData,
)
from opsml_artifacts.registry.model.utils import (
    FloatTypeConverter,
    get_dtype_shape,
    get_feature_info,
)

logger = ArtifactLogger.get_logger(__name__)

ModelConvertOutput = Tuple[ModelDefinition, Dict[str, Feature], Optional[Dict[str, Feature]]]


# lgb and xgb need to be converted to float32
# skearn pipeline needs to be converted to float32
# stacking regressor needs to be converted to float32


class DataConverter:
    def __init__(self, model_info: ModelInfo):
        """DataConverter for for Numpy arrays and non deep-learning estimators

        Args:
            model_info: ModelInfo class containing model-related information

        """

        self.model_info = model_info
        self.input_name = "inputs"

    @property
    def data(self):
        return self.model_info.input_data

    @data.setter
    def data(self, data: ModelData):
        self.model_info.input_data = data

    def convert_to_float(self, convert_all: bool):
        """Converts either all non-float32 numeric types to Float32 or
        converts Float64 types to Float32. Skl2Onnx does not support Float64 for some estimator types.

        Args:
            all (boolean): Boolean indicating whether to convert all columns to Float32

        """
        self.data = FloatTypeConverter(
            convert_all=convert_all,
        ).convert_to_float(data=self.data)

    def get_data_schema(self) -> Optional[Dict[str, Feature]]:
        """Gets schema from data.
        Reproduces onnx_data_types in some instances
        """
        raise NotImplementedError

    def get_onnx_data_types(self) -> List[Any]:
        """Infers data types from training data"""

        raise NotImplementedError

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

    @staticmethod
    def validate(model_info: ModelInfo) -> bool:
        """Validate data and model types"""
        raise NotImplementedError


class NumpyOnnxConverter(DataConverter):
    def get_onnx_data_types(self) -> List[Any]:
        """Infers data types from training data"""

        dtype, shape = get_dtype_shape(data=self.data)
        spec = get_onnx_tensor_spec(dtype=dtype, input_shape=shape)
        return [(self.input_name, spec)]

    def get_data_schema(self) -> Optional[Dict[str, Feature]]:
        return None

    def convert_data_to_onnx(self) -> Dict[str, NDArray]:
        return {self.input_name: self.data}

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
    """DataConverter for Sklearn estimators that receive a pandas DataFrame as
    as sample Data.
    """

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
        input_shape = self.data.shape[1:]
        dtype = str(self.data.to_numpy().dtype)

        spec = get_onnx_tensor_spec(dtype=dtype, input_shape=input_shape)

        return [(self.input_name, spec)]

    def convert_data_to_onnx(self) -> Dict[str, Any]:
        return {self.input_name: self.data.to_numpy()}

    @staticmethod
    def validate(model_info: ModelInfo) -> bool:

        return (
            model_info.data_type == InputDataType.PANDAS_DATAFRAME.value
            and model_info.model_type != OnnxModelType.SKLEARN_PIPELINE
        )


class PandasPipelineOnnxConverter(DataConverter):
    """DataConverter for Sklearn Pipelines that receive pandas DataFrames as
    inputs
    """

    def get_data_schema(self) -> Optional[Dict[str, Feature]]:
        return self._get_py_dataframe_schema()

    def get_onnx_data_types(self) -> List[Any]:
        return self._get_onnx_dataframe_schema()

    def convert_data_to_onnx(self) -> Dict[str, Any]:

        """Converts pandas dataframe associated with SKLearn pipeline"""

        data_columns = self.data.columns
        rows_shape = self.data.shape[0]
        dtypes = self.data.dtypes

        inputs = {col: self.data[col].values for col in data_columns}

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
    """DataConverter for TensorFlow/Keras models trained with dictionaries, such as
    with multi-input models
    """

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
        for key, val in self.data.items():
            onnx_data[key] = val.astype(np.float32)
        return onnx_data

    @staticmethod
    def validate(model_info: ModelInfo) -> bool:
        return model_info.data_type == InputDataType.DICT.value and model_info.model_type == OnnxModelType.TF_KERAS


class TensorflowNumpyOnnxConverter(DataConverter):
    """DataConverter for TensorFlow/Keras models trained with arrays"""

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
        return {self.input_name: self.data.astype(np.float32)}

    @staticmethod
    def validate(model_info: ModelInfo) -> bool:
        return (
            model_info.data_type == InputDataType.NUMPY_ARRAY.value and model_info.model_type == OnnxModelType.TF_KERAS
        )


class PyTorchOnnxDataConverter(DataConverter):
    """DataConverter for Pytorch models trained with arrays"""

    def __init__(self, model_info: ModelInfo):
        super().__init__(model_info=model_info)

        self.input_name = self._get_input_name()

    def _get_input_name(self) -> str:
        args = cast(TorchOnnxArgs, self.model_info.additional_model_args)
        return args.input_names[0]

    def get_onnx_data_types(self) -> List[Any]:
        """Infers data types from training data"""

        dtype, shape = get_dtype_shape(data=self.data)
        spec = get_onnx_tensor_spec(dtype=dtype, input_shape=shape)
        return [(self.input_name, spec)]

    def get_data_schema(self) -> Optional[Dict[str, Feature]]:
        return None

    def convert_data_to_onnx(self) -> Dict[str, Any]:
        return {self.input_name: self.data.astype(np.float32)}

    @staticmethod
    def validate(model_info: ModelInfo) -> bool:
        return (
            model_info.data_type == InputDataType.NUMPY_ARRAY.value and model_info.model_type == OnnxModelType.PYTORCH
        )


class PyTorchOnnxDictConverter(DataConverter):

    """DataConverter for Pytorch models trained with dictionary inputs, such as with
    HuggingFace language models that accept input_ids, token_type_ids and
    attention_mask.
    """

    def __init__(self, model_info: ModelInfo):
        super().__init__(model_info=model_info)

        self.input_names = self._get_input_names()

    def _get_input_names(self) -> List[str]:
        args = cast(TorchOnnxArgs, self.model_info.additional_model_args)
        return args.input_names

    def get_data_schema(self) -> Optional[Dict[str, Feature]]:
        return None

    def get_onnx_data_types(self) -> List[Any]:
        specs = []

        for input_ in self.input_names:
            data = self.data[input_]
            dtype, shape = get_dtype_shape(data=data)
            spec = get_onnx_tensor_spec(dtype=dtype, input_shape=shape)
            specs.append((input_, spec))

        return specs

    def convert_data_to_onnx(self) -> Dict[str, Any]:
        """Convert Pytorch dictionary sample to onnx format"""

        onnx_data = {}
        for key, val in self.data.items():
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
