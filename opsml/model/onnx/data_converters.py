# pylint: disable=[import-outside-toplevel,import-error]
"""Code for generating Onnx Models"""
# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import Any, Dict, List, Optional, Tuple, cast

from opsml.model.interfaces.base import ModelInterface
from opsml.model.utils.data_helper import FloatTypeConverter, ModelDataHelper
from opsml.types import (
    AVAILABLE_MODEL_TYPES,
    AllowedDataType,
    Feature,
    OnnxModel,
    TrainedModelType,
)

# attempt to load get_skl2onnx_onnx_tensor_spec if skl2onnx is installed
# this is checked during model conversion
try:
    from opsml.model.utils.skl2onnx_data_types import get_skl2onnx_onnx_tensor_spec
except ModuleNotFoundError:
    pass

ModelConvertOutput = Tuple[OnnxModel, Dict[str, Feature], Optional[Dict[str, Feature]]]


# lgb and xgb need to be converted to float32
# sklearn pipeline needs to be converted to float32 (some features)
# stacking regressor needs to be converted to float32 (all features)
class DataConverter:
    def __init__(self, model_interface: ModelInterface, data_helper: ModelDataHelper):
        """
        DataConverter for for Numpy arrays and non deep-learning estimators

        Args:
            model_info
                `ModelInfo` class containing model-related information

        """
        self.data_helper = data_helper
        self.interface = model_interface
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

    def get_onnx_data_types(self) -> List[Any]:
        """Infers data types from training data"""

        return ["None"]

    def _get_onnx_dataframe_schema(self) -> List[Any]:
        """Creates an Onnx feature spec from a pandas dataframe"""

        inputs = []
        for key, val in self.data_helper.feature_types:
            spec = get_skl2onnx_onnx_tensor_spec(dtype=str(val), input_shape=[1])
            inputs.append((key, spec))
        return inputs

    @staticmethod
    def validate(data_type: str, model_type: str, model_class: str) -> bool:
        """Validate data and model types"""
        raise NotImplementedError


class NumpyOnnxConverter(DataConverter):
    def get_onnx_data_types(self) -> List[Any]:
        """Infers data types from training data"""

        dtype = self.data_helper.dtypes[0]
        shape = cast(Tuple[int, ...], self.data_helper.shape[1:])
        spec = get_skl2onnx_onnx_tensor_spec(dtype=dtype, input_shape=shape)

        return [(self.input_name, spec)]

    @staticmethod
    def validate(data_type: str, model_type: str, model_class: str) -> bool:
        if data_type == AllowedDataType.NUMPY:
            if model_class in AVAILABLE_MODEL_TYPES and model_class not in [
                TrainedModelType.TF_KERAS,
                TrainedModelType.PYTORCH,
                TrainedModelType.TRANSFORMERS,
            ]:
                return True
        return False


class PandasOnnxConverter(DataConverter):
    """
    DataConverter for Sklearn estimators that receive a pandas DataFrame as
    as sample Data. Model is trained with numpy, but original data is in DataFrame
    format
    """

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

    @staticmethod
    def validate(data_type: str, model_type: str, model_class: str) -> bool:
        model_match = (
            model_class
            in [
                TrainedModelType.SKLEARN_ESTIMATOR,
                TrainedModelType.LGBM_BOOSTER,
            ]
            and model_type != TrainedModelType.SKLEARN_PIPELINE
        )
        return data_type == AllowedDataType.PANDAS and model_match


class PandasPipelineOnnxConverter(DataConverter):
    """
    DataConverter for Sklearn Pipelines that receive pandas DataFrames as
    inputs
    """

    def get_onnx_data_types(self) -> List[Any]:
        return self._get_onnx_dataframe_schema()

    @staticmethod
    def validate(data_type: str, model_type: str, model_class: str) -> bool:
        model_match = (
            model_class == TrainedModelType.SKLEARN_ESTIMATOR and model_type == TrainedModelType.SKLEARN_PIPELINE
        )
        return data_type == AllowedDataType.PANDAS and model_match


class TensorflowDictOnnxConverter(DataConverter):
    """
    DataConverter for TensorFlow/Keras models trained with dictionaries, such as
    with multi-input models
    """

    def get_onnx_data_types(self) -> List[Any]:
        """
        Takes multi input model spec and gets input shape and type for tensorspec
        """
        import tensorflow as tf

        assert isinstance(self.interface.model, tf.keras.Model)
        spec = []
        for input_ in self.interface.model.inputs:
            shape_, dtype = list(input_.shape), input_.dtype
            shape_[0] = None
            input_name = getattr(input_, "name", "inputs")
            spec.append(tf.TensorSpec(shape_, dtype, name=input_name))

        return spec

    @staticmethod
    def validate(data_type: str, model_type: str, model_class: str) -> bool:
        return data_type == AllowedDataType.DICT and model_class == TrainedModelType.TF_KERAS


class TensorflowNumpyOnnxConverter(DataConverter):
    """DataConverter for TensorFlow/Keras models trained with arrays"""

    def get_onnx_data_types(self) -> List[Any]:
        """
        Takes model spec and gets input shape and type for
        tensorspec
        """
        import tensorflow as tf

        assert isinstance(self.interface.model, tf.keras.Model)

        input_ = self.interface.model.inputs[0]
        shape_, dtype = list(input_.shape), input_.dtype
        shape_[0] = None
        self.input_name = getattr(input_, "name", "inputs")

        return [tf.TensorSpec(shape_, dtype, name=self.input_name)]

    @staticmethod
    def validate(data_type: str, model_type: str, model_class: str) -> bool:
        data_match = data_type in (AllowedDataType.TENSORFLOW_TENSOR, AllowedDataType.NUMPY)

        return data_match and model_class == TrainedModelType.TF_KERAS


class OnnxDataConverter:
    def __init__(self, model_interface: ModelInterface, data_helper: ModelDataHelper):
        self.converter = self._get_converter(model_interface=model_interface, data_helper=data_helper)

    def _get_converter(self, model_interface: ModelInterface, data_helper: ModelDataHelper) -> DataConverter:
        converter = next(
            (
                converter
                for converter in DataConverter.__subclasses__()
                if converter.validate(
                    model_type=model_interface.model_type,
                    data_type=model_interface.data_type,
                    model_class=model_interface.model_class,
                )
            ),
            DataConverter,
        )

        return converter(model_interface=model_interface, data_helper=data_helper)

    def get_data_types(self) -> List[Any]:
        """Takes input data sample and model type and converts data to onnx format"""

        return self.converter.get_onnx_data_types()
