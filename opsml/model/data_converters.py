# pylint: disable=[import-outside-toplevel,import-error]
"""Code for generating Onnx Models"""
# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import Any, Dict, List, Optional, Tuple, cast

import numpy as np
from numpy.typing import NDArray

from opsml.model.data_helper import FloatTypeConverter, ModelDataHelper
from opsml.model.types import (
    AVAILABLE_MODEL_TYPES,
    DataDtypes,
    ExtraOnnxArgs,
    Feature,
    ModelCard,
    OnnxModelDefinition,
    TrainedModelType,
)
from opsml.registry.data.types import AllowedDataType

# attempt to load get_skl2onnx_onnx_tensor_spec if skl2onnx is installed
# this is checked during model conversion
try:
    from opsml.model.sklearn.skl2onnx_data_types import get_skl2onnx_onnx_tensor_spec
except ModuleNotFoundError:
    pass

ModelConvertOutput = Tuple[OnnxModelDefinition, Dict[str, Feature], Optional[Dict[str, Feature]]]


# lgb and xgb need to be converted to float32
# sklearn pipeline needs to be converted to float32 (some features)
# stacking regressor needs to be converted to float32 (all features)
class DataConverter:
    def __init__(self, modelcard: ModelCard, data_helper: ModelDataHelper):
        """
        DataConverter for for Numpy arrays and non deep-learning estimators

        Args:
            model_info
                `ModelInfo` class containing model-related information

        """
        self.data_helper = data_helper
        self.card = modelcard
        self.input_name = "predict"

    def convert_to_float(self, convert_all: bool) -> None:
        """
        Converts either all non-float32 numeric types to Float32 or
        converts Float64 types to Float32. Skl2Onnx does not support Float64 for some estimator types.

        Args:
            convert_all:
                Boolean indicating whether to convert all columns to Float32

        """
        self.data_helper.data = FloatTypeConverter(
            convert_all=convert_all,
        ).convert_to_float(data=self.data_helper.data)

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
        for key, val in self.data_helper.feature_types:
            spec = get_skl2onnx_onnx_tensor_spec(dtype=str(val), input_shape=[1])
            inputs.append((key, spec))
        return inputs

    def _get_py_dataframe_schema(self) -> Dict[str, Feature]:
        """Creates feature dictionary based on dataframe schema"""

        feature_dict: Dict[str, Feature] = {}
        for feature, feature_type in self.data_helper.feature_types:
            feature_dict[feature] = self.data_helper.get_feature_info(
                type_=str(feature_type),
                shape=[None, 1],
            )

        return feature_dict

    @staticmethod
    def validate(data_type: str, model_type: str) -> bool:
        """Validate data and model types"""
        raise NotImplementedError


class NumpyOnnxConverter(DataConverter):
    def get_onnx_data_types(self) -> List[Any]:
        """Infers data types from training data"""

        dtype = self.data_helper.dtypes[0]
        shape = cast(Tuple[int, ...], self.data_helper.shape[1:])
        spec = get_skl2onnx_onnx_tensor_spec(dtype=dtype, input_shape=shape)

        return [(self.input_name, spec)]

    def get_data_schema(self) -> Optional[Dict[str, Feature]]:
        return None

    def convert_data_to_onnx(self) -> Dict[str, NDArray[Any]]:
        return {self.input_name: self.data_helper.data}

    @staticmethod
    def validate(data_type: str, model_type: str) -> bool:
        if data_type == AllowedDataType.NUMPY:
            if model_type in AVAILABLE_MODEL_TYPES and model_type not in [
                TrainedModelType.TF_KERAS,
                TrainedModelType.PYTORCH,
                TrainedModelType.TRANSFORMER,
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
        This is used for models that supply a dataframe, but are trained with a numpy array.
        Onnx will expect an array.

        Example:
            # X_train is a dataframe
            reg = lgb.LGBMClassifier(n_estimators=3)
            reg.fit(X_train.to_numpy(), y_train)

        """
        input_shape = cast(Tuple[int, ...], self.data_helper.shape[1:])
        dtype = self.data_helper.dtypes[0]
        spec = get_skl2onnx_onnx_tensor_spec(dtype=dtype, input_shape=input_shape)
        return [(self.input_name, spec)]

    def convert_data_to_onnx(self) -> Dict[str, Any]:
        return {self.input_name: self.data_helper.to_numpy()}

    @staticmethod
    def validate(data_type: str, model_type: str) -> bool:
        return data_type == AllowedDataType.PANDAS and model_type != TrainedModelType.SKLEARN_PIPELINE


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

        rows_shape = self.data_helper.shape[0]
        inputs = self.data_helper.dataframe_record()

        # refactor later
        for col, col_type in self.data_helper.feature_types:
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
    def validate(data_type: str, model_type: str) -> bool:
        return data_type == AllowedDataType.PANDAS and model_type == TrainedModelType.SKLEARN_PIPELINE


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

        assert isinstance(self.card.trained_model, tf.keras.Model)
        spec = []
        for input_ in self.card.trained_model.inputs:
            shape_, dtype = list(input_.shape), input_.dtype
            shape_[0] = None
            input_name = getattr(input_, "name", "inputs")
            spec.append(tf.TensorSpec(shape_, dtype, name=input_name))

        return spec

    def convert_data_to_onnx(self) -> Dict[str, Any]:
        onnx_data = {}
        assert isinstance(self.data_helper.data, dict)
        for key, val in self.data_helper.data.items():
            onnx_data[key] = val.astype(np.float32)
        return onnx_data

    @staticmethod
    def validate(data_type: str, model_type: str) -> bool:
        return data_type == AllowedDataType.DICT and model_type == TrainedModelType.TF_KERAS


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

        assert isinstance(self.card.trained_model, tf.keras.Model)
        # model = cast(tf.keras.Model, self.card.trained_model)
        input_ = self.card.trained_model.inputs[0]
        shape_, dtype = list(input_.shape), input_.dtype
        shape_[0] = None
        self.input_name = getattr(input_, "name", "inputs")

        return [tf.TensorSpec(shape_, dtype, name=self.input_name)]

    def convert_data_to_onnx(self) -> Dict[str, Any]:
        return {self.input_name: self.data_helper.data.astype(np.float32)}

    @staticmethod
    def validate(data_type: str, model_type: str) -> bool:
        return data_type == AllowedDataType.NUMPY and model_type == TrainedModelType.TF_KERAS


class PyTorchOnnxDataConverter(DataConverter):
    """DataConverter for Pytorch models trained with arrays"""

    def __init__(self, modelcard: ModelCard, data_helper: ModelDataHelper):
        super().__init__(modelcard=modelcard, data_helper=data_helper)

        self.input_name = self._get_input_name()

    def _get_input_name(self) -> str:
        assert isinstance(self.card.metadata.additional_onnx_args, ExtraOnnxArgs)
        return self.card.metadata.additional_onnx_args.input_names[0]

    def get_onnx_data_types(self) -> List[Any]:
        """Infers data types from training data"""

        shape = cast(Tuple[int, ...], self.data_helper.shape[1:])
        dtype = self.data_helper.dtypes[0]

        return [(self.input_name, shape, dtype)]

    def get_data_schema(self) -> Optional[Dict[str, Feature]]:
        return None

    def convert_data_to_onnx(self) -> Dict[str, Any]:
        return {self.input_name: self.data_helper.data}

    @staticmethod
    def validate(data_type: str, model_type: str) -> bool:
        return data_type == AllowedDataType.NUMPY and model_type in [
            TrainedModelType.PYTORCH,
            TrainedModelType.TRANSFORMER,
        ]


class PyTorchOnnxDictConverter(DataConverter):

    """
    DataConverter for Pytorch models trained with dictionary inputs, such as with
    HuggingFace language models that accept input_ids, token_type_ids and
    attention_mask.
    """

    def __init__(self, modelcard: ModelCard, data_helper: ModelDataHelper):
        super().__init__(modelcard=modelcard, data_helper=data_helper)

        self.input_names = self._get_input_names()

    def _get_input_names(self) -> List[str]:
        assert isinstance(self.card.metadata.additional_onnx_args, ExtraOnnxArgs)
        return self.card.metadata.additional_onnx_args.input_names

    def get_data_schema(self) -> Optional[Dict[str, Feature]]:
        return None

    def get_onnx_data_types(self) -> List[Any]:
        zipped = zip(
            self.input_names,
            self.data_helper.shape,
            self.data_helper.dtypes,
        )

        return list([zipped])

    def convert_data_to_onnx(self) -> Dict[str, Any]:
        """Convert Pytorch dictionary sample to onnx format"""

        onnx_data = {}
        for key, val in self.data_helper.data.items():
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
    def validate(data_type: str, model_type: str) -> bool:
        return data_type == AllowedDataType.DICT and model_type in [
            TrainedModelType.PYTORCH,
            TrainedModelType.TRANSFORMER,
        ]


class OnnxDataConverter:
    def __init__(self, modelcard: ModelCard, data_helper: ModelDataHelper):
        self.converter = self._get_converter(modelcard=modelcard, data_helper=data_helper)

    def _get_converter(self, modelcard: ModelCard, data_helper: ModelDataHelper) -> DataConverter:
        converter = next(
            (
                converter
                for converter in DataConverter.__subclasses__()
                if converter.validate(
                    model_type=modelcard.metadata.model_type,
                    data_type=modelcard.metadata.sample_data_type,
                )
            )
        )

        return converter(modelcard=modelcard, data_helper=data_helper)

    def convert_data(self) -> Dict[str, Any]:
        """Takes input data sample and model type and converts data to onnx format"""

        return self.converter.convert_data_to_onnx()

    def get_data_types(self) -> Tuple[List[Any], Optional[Dict[str, Feature]]]:
        """Takes input data sample and model type and converts data to onnx format"""

        onnx_types = self.converter.get_onnx_data_types()
        py_data_types = self.converter.get_data_schema()
        return onnx_types, py_data_types
