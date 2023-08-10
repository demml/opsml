# pylint: disable=[import-outside-toplevel,import-error]
"""Code for generating Onnx Models"""
# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import Any, Dict, List, Optional, Tuple, cast

import numpy as np
from numpy.typing import NDArray

from opsml.model.model_info import FloatTypeConverter, ModelData, ModelInfo
from opsml.model.onnx_data_types import get_onnx_tensor_spec
from opsml.model.types import (
    AVAILABLE_MODEL_TYPES,
    DataDtypes,
    ExtraOnnxArgs,
    Feature,
    InputDataType,
    OnnxModelDefinition,
    OnnxModelType,
)

ModelConvertOutput = Tuple[OnnxModelDefinition, Dict[str, Feature], Optional[Dict[str, Feature]]]


# lgb and xgb need to be converted to float32
# sklearn pipeline needs to be converted to float32 (some features)
# stacking regressor needs to be converted to float32 (all features)
class DataConverter:
    def __init__(self, model_info: ModelInfo):
        """
        DataConverter for for Numpy arrays and non deep-learning estimators

        Args:
            model_info
                `ModelInfo` class containing model-related information

        """
        self.model_info = model_info
        self.input_name = "predict"

    @property
    def model_data(self) -> ModelData:
        return self.model_info.model_data

    def convert_to_float(self, convert_all: bool):
        """
        Converts either all non-float32 numeric types to Float32 or
        converts Float64 types to Float32. Skl2Onnx does not support Float64 for some estimator types.

        Args:
            convert_all:
                Boolean indicating whether to convert all columns to Float32

        """
        self.model_data.data = FloatTypeConverter(
            convert_all=convert_all,
        ).convert_to_float(data=self.model_data.data)

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

        inputs = []
        for key, val in self.model_data.feature_types:
            spec = get_onnx_tensor_spec(dtype=str(val), input_shape=[1])
            inputs.append((key, spec))
        return inputs

    def _get_py_dataframe_schema(self) -> Dict[str, Feature]:
        """Creates feature dictionary based on dataframe schema"""

        feature_dict: Dict[str, Feature] = {}
        for feature, feature_type in self.model_data.feature_types:
            feature_dict[feature] = self.model_data.get_feature_info(
                type_=str(feature_type),
                shape=[None, 1],
            )

        return feature_dict

    @staticmethod
    def validate(model_info: ModelInfo) -> bool:
        """Validate data and model types"""
        raise NotImplementedError


class NumpyOnnxConverter(DataConverter):
    def get_onnx_data_types(self) -> List[Any]:
        """Infers data types from training data"""

        dtype = self.model_data.dtypes[0]
        shape = cast(Tuple[int, ...], self.model_data.shape[1:])
        spec = get_onnx_tensor_spec(dtype=dtype, input_shape=shape)

        return [(self.input_name, spec)]

    def get_data_schema(self) -> Optional[Dict[str, Feature]]:
        return None

    def convert_data_to_onnx(self) -> Dict[str, NDArray]:
        return {self.input_name: self.model_data.data}

    @staticmethod
    def validate(model_info: ModelInfo) -> bool:
        if model_info.data_type == InputDataType.NUMPY_ARRAY.value:
            if model_info.model_type in AVAILABLE_MODEL_TYPES and model_info.model_type not in [
                OnnxModelType.TF_KERAS,
                OnnxModelType.PYTORCH,
                OnnxModelType.TRANSFORMER,
            ]:
                return True
        return False


class PandasOnnxConverter(DataConverter):
    """
    DataConverter for Sklearn estimators that receive a pandas DataFrame as
    as sample Data. Model is trained with numpy, but original data is in DataFrame
    format
    """

    def get_data_schema(self) -> Optional[Dict[str, Feature]]:
        return self._get_py_dataframe_schema()

    def get_onnx_data_types(self) -> List[Any]:
        """
        Creates a single type spec for a pandas dataframe.
        This is used for models that supply a dataframe, but are trained with an array.

        Example:
            # X_train is a dataframe
            reg = lgb.LGBMClassifier(n_estimators=3)
            reg.fit(X_train.to_numpy(), y_train)

        """
        input_shape = cast(Tuple[int, ...], self.model_data.shape[1:])
        dtype = self.model_data.dtypes[0]
        spec = get_onnx_tensor_spec(dtype=dtype, input_shape=input_shape)
        return [(self.input_name, spec)]

    def convert_data_to_onnx(self) -> Dict[str, Any]:
        return {self.input_name: self.model_data.to_numpy()}

    @staticmethod
    def validate(model_info: ModelInfo) -> bool:
        return (
            model_info.data_type == InputDataType.PANDAS_DATAFRAME.value
            and model_info.model_type != OnnxModelType.SKLEARN_PIPELINE
        )


class PandasPipelineOnnxConverter(DataConverter):
    """
    DataConverter for Sklearn Pipelines that receive pandas DataFrames as
    inputs
    """

    def get_data_schema(self) -> Optional[Dict[str, Feature]]:
        return self._get_py_dataframe_schema()

    def get_onnx_data_types(self) -> List[Any]:
        return self._get_onnx_dataframe_schema()

    def convert_data_to_onnx(self) -> Dict[str, Any]:
        """Converts pandas dataframe associated with SKLearn pipeline"""

        rows_shape = self.model_data.shape[0]
        inputs = self.model_data.dataframe_record()

        # refactor later
        for col, col_type in self.model_data.feature_types:
            if DataDtypes.INT32 in col_type:
                inputs[col] = inputs[col].astype(np.int32)
            elif DataDtypes.INT64 in col_type:
                inputs[col] = inputs[col].astype(np.int64)
            elif DataDtypes.FLOAT32 in col_type:
                inputs[col] = inputs[col].astype(np.float32)
            elif DataDtypes.FLOAT64 in col_type:
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
    """
    DataConverter for TensorFlow/Keras models trained with dictionaries, such as
    with multi-input models
    """

    def get_data_schema(self) -> Optional[Dict[str, Feature]]:
        return None

    def get_onnx_data_types(self) -> List[Any]:
        """
        Takes multi input model spec and gets input shape and type for tensorspec
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
        for key, val in self.model_data.data.items():
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
        """
        Takes model spec and gets input shape and type for
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
        return {self.input_name: self.model_data.data.astype(np.float32)}

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
        args = cast(ExtraOnnxArgs, self.model_info.additional_model_args)
        return args.input_names[0]

    def get_onnx_data_types(self) -> List[Any]:
        """Infers data types from training data"""

        shape = cast(Tuple[int, ...], self.model_data.shape[1:])
        dtype = self.model_data.dtypes[0]
        spec = get_onnx_tensor_spec(dtype=dtype, input_shape=shape)
        return [(self.input_name, spec)]

    def get_data_schema(self) -> Optional[Dict[str, Feature]]:
        return None

    def convert_data_to_onnx(self) -> Dict[str, Any]:
        return {self.input_name: self.model_data.data}

    @staticmethod
    def validate(model_info: ModelInfo) -> bool:
        return model_info.data_type == InputDataType.NUMPY_ARRAY.value and model_info.model_type in [
            OnnxModelType.PYTORCH,
            OnnxModelType.TRANSFORMER,
        ]


class PyTorchOnnxDictConverter(DataConverter):

    """
    DataConverter for Pytorch models trained with dictionary inputs, such as with
    HuggingFace language models that accept input_ids, token_type_ids and
    attention_mask.
    """

    def __init__(self, model_info: ModelInfo):
        super().__init__(model_info=model_info)

        self.input_names = self._get_input_names()

    def _get_input_names(self) -> List[str]:
        args = cast(ExtraOnnxArgs, self.model_info.additional_model_args)
        return args.input_names

    def get_data_schema(self) -> Optional[Dict[str, Feature]]:
        return None

    def get_onnx_data_types(self) -> List[Any]:
        specs = []

        zipped = zip(
            self.input_names,
            self.model_data.shape,
            self.model_data.dtypes,
        )

        for feature, shape, dtype in zipped:
            shape = cast(Tuple[int, ...], shape)
            spec = get_onnx_tensor_spec(dtype=dtype, input_shape=shape[1:])
            specs.append((feature, spec))

        return specs

    def convert_data_to_onnx(self) -> Dict[str, Any]:
        """Convert Pytorch dictionary sample to onnx format"""

        onnx_data = {}
        for key, val in self.model_data.data.items():
            dtype = str(val.dtype)

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
        return model_info.data_type == InputDataType.DICT.value and model_info.model_type in [
            OnnxModelType.PYTORCH,
            OnnxModelType.TRANSFORMER,
        ]


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
