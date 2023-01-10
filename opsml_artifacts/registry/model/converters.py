# pylint: disable=import-outside-toplevel
"""Code for generating Onnx Models"""
from typing import Any, Dict, List, Tuple, Union, cast

import numpy as np
import onnxruntime as rt
import pandas as pd
from cryptography.fernet import Fernet
from onnx.onnx_ml_pb2 import ModelProto  # pylint: disable=no-name-in-module
from pyshipt_logging import ShiptLogging
from skl2onnx.common.data_types import (
    FloatTensorType,
    Int32TensorType,
    Int64TensorType,
    StringTensorType,
)
from sklearn.base import BaseEstimator
from sklearn.ensemble import StackingRegressor
from sklearn.pipeline import Pipeline

from opsml_artifacts.registry.model.base_models import (
    Feature,
    ModelDefinition,
    OnnxDataProto,
    OnnxModelType,
)
from opsml_artifacts.registry.model.onnx_registry import OnnxRegistryUpdater

# Get logger
logger = ShiptLogging.get_logger(__name__)
onnx_model_types = set(model_type.value for model_type in OnnxModelType)


class DataConverter:
    def __init__(self, data: Union[pd.DataFrame, np.ndarray]):
        self.data = data

    def get_onnx_data_types(self) -> List[Any]:
        """Infers data types from training data"""
        return ["placeholder"]

    def convert_data_to_onnx(self) -> Dict[str, Any]:
        """Converts data to onnx schema"""
        return {"placeholder": "placeholder"}

    def _convert_dataframe_schema(self) -> List[Any]:
        self.data = cast(pd.DataFrame, self.data)

        inputs = []
        for key, val in zip(self.data.columns, self.data.dtypes):
            if "int64" in str(val):
                tensor = Int64TensorType([None, 1])
            elif "int32" in str(val):
                tensor = Int32TensorType([None, 1])
            elif "float" in str(val):
                tensor = FloatTensorType([None, 1])
            else:
                tensor = StringTensorType([None, 1])
            inputs.append((key, tensor))
        return inputs

    @staticmethod
    def validate(data_type: type, model_type: str) -> bool:
        "Validate data"

        return True


class NumpyOnnxConverter(DataConverter):
    def get_onnx_data_types(self) -> List[Any]:
        return [("inputs", FloatTensorType([None, self.data.shape[1]]))]

    def convert_data_to_onnx(self) -> Dict[str, Any]:
        return {"inputs": self.data.astype(np.float32)[:1]}

    @staticmethod
    def validate(data_type: type, model_type: str) -> bool:
        if data_type == np.ndarray and model_type == OnnxModelType.SKLEARN_ESTIMATOR.value:
            return True
        return False


class PandasOnnxConverter(DataConverter):
    def get_onnx_data_types(self) -> List[Any]:
        return self._convert_dataframe_schema()

    def convert_data_to_onnx(self) -> Dict[str, Any]:
        self.data = cast(pd.DataFrame, self.data)
        return {"inputs": self.data.to_numpy().astype(np.float32)[:1]}

    @staticmethod
    def validate(data_type: type, model_type: str) -> bool:
        if data_type == pd.DataFrame and model_type == OnnxModelType.SKLEARN_ESTIMATOR.value:
            return True
        return False


class PandasPipelineOnnxConverter(DataConverter):
    def get_onnx_data_types(self) -> List[Any]:
        return self._convert_dataframe_schema()

    def convert_data_to_onnx(self) -> Dict[str, Any]:

        """Converts pandas dataframe associated with SKLearn pipeline"""

        self.data = cast(pd.DataFrame, self.data)

        inputs = {col: self.data[col].values for col in self.data.columns}

        for col, col_type in zip(self.data.columns, self.data.dtypes):
            if "int32" in str(col_type):
                inputs[col] = inputs[col].astype(np.int32)
            elif "int64" in str(col_type):
                inputs[col] = inputs[col].astype(np.int64)
            elif "float" in str(col_type):
                inputs[col] = inputs[col].astype(np.float32)

        for col in inputs:
            inputs[col] = inputs[col].reshape((self.data.shape[0], 1))

        return inputs

    @staticmethod
    def validate(data_type: type, model_type: str) -> bool:
        if data_type == pd.DataFrame and model_type == OnnxModelType.SKLEARN_PIPELINE.value:
            return True
        return False


class OnnxDataConverter:
    @staticmethod
    def convert_data(
        input_data: Union[pd.DataFrame, np.ndarray],
        model_type: str,
    ) -> Dict[str, Any]:
        """Takes input data sample and model type and converts data to onnx format"""

        data_type = type(input_data)
        converter = next(
            (
                converter
                for converter in DataConverter.__subclasses__()
                if converter.validate(data_type=data_type, model_type=model_type)
            )
        )

        return converter(data=input_data).convert_data_to_onnx()

    @staticmethod
    def get_onnx_data_types(
        input_data: Union[pd.DataFrame, np.ndarray],
        model_type: str,
    ) -> List[Any]:
        """Takes input data sample and model type and converts data to onnx format"""

        data_type = type(input_data)
        converter = next(
            (
                converter
                for converter in DataConverter.__subclasses__()
                if converter.validate(data_type=data_type, model_type=model_type)
            )
        )

        return converter(data=input_data).get_onnx_data_types()


class ModelConverter:
    def __init__(
        self,
        model: Any,
        input_data: Any,
        model_type: str,
    ):
        self.model = model
        self.input_data = input_data
        self.model_type = model_type
        self.update_onnx_registries()

    def update_onnx_registries(self):
        model_estimator_name = self.model.__class__.__name__.lower()
        OnnxRegistryUpdater.update_onnx_registry(
            model_estimator_name=model_estimator_name,
        )

    def convert(self) -> Tuple[ModelDefinition, Dict[str, Feature]]:
        """Converts a model to onnx format

        Returns
            Encrypted model definition and feature dictionary
        """
        model_def = ModelDefinition(model_bytes=b"placeholder", encrypt_key=b"placeholder")
        dict_ = {"placeholder": Feature(feature_type="placeholder", shape=[10])}
        return (model_def, dict_)

    def validate_model(self, onnx_model: ModelProto) -> None:
        """Validates an onnx model on training data"""
        inputs = OnnxDataConverter.convert_data(
            input_data=self.input_data,
            model_type=self.model_type,
        )

        logger.info("Validating converted onnx model")
        sess = rt.InferenceSession(onnx_model.SerializeToString())
        pred_onx = np.ravel(sess.run(None, inputs))[0]
        logger.info(pred_onx)

    def get_initial_types(self) -> List[Any]:
        return OnnxDataConverter.get_onnx_data_types(
            input_data=self.input_data,
            model_type=self.model_type,
        )

    def create_feature_dict(self, onnx_model: ModelProto) -> Dict[str, Feature]:
        feature_dict = {}
        for input_ in onnx_model.graph.input:
            data_type = input_.type.tensor_type.elem_type
            row = input_.type.tensor_type.shape.dim[0].dim_value
            col = input_.type.tensor_type.shape.dim[1].dim_value

            # default to None for a model with varying length input
            if row == 0:
                row = None

            feature_dict[input_.name] = Feature(
                feature_type=OnnxDataProto(data_type).name,
                shape=[row, col],
            )

        return feature_dict

    def encrypt_model(self, onnx_model: ModelProto) -> ModelDefinition:
        """Encrypts an Onnx model

        Args:
            onnx_model (ModelProto): Onnx model
        """
        key = Fernet.generate_key()  # this is your "password"
        cipher_suite = Fernet(key)
        encoded_text = cipher_suite.encrypt(
            onnx_model.SerializeToString(),
        )
        return ModelDefinition(
            model_bytes=encoded_text,
            encrypt_key=key,
        )

    @staticmethod
    def validate(model_type: str) -> bool:
        """validates model base class"""

        return True


class SklearnOnnxModel(ModelConverter):
    def convert_model(self) -> ModelProto:
        """Converts sklearn model to ONNX ModelProto"""
        from skl2onnx import convert_sklearn

        initial_types = self.get_initial_types()
        onnx_model = convert_sklearn(
            model=self.model,
            initial_types=initial_types,
        )

        self.validate_model(onnx_model=onnx_model)

        return onnx_model

    def convert(self) -> Tuple[ModelDefinition, Dict[str, Feature]]:
        """Converts model to onnx model, validates it, and create an
        onnx feature dictionary

        Returns:
            Onnx ModelDefinition and Dictionary of Onnx features
        """
        onnx_model = self.convert_model()
        model_def = self.encrypt_model(onnx_model=onnx_model)
        features = self.create_feature_dict(onnx_model=onnx_model)

        return model_def, features

    @staticmethod
    def validate(model_type: str) -> bool:
        if model_type in onnx_model_types:
            return True
        return False


class OnnxModelConverter:
    def __init__(
        self,
        model: Union[BaseEstimator, Pipeline, StackingRegressor],
        input_data: Union[pd.DataFrame, np.ndarray],
        model_type: str,
    ):
        self.model = model
        self.data = input_data
        self.model_type = model_type

        """Instantiates a helper class to convert machine learning models and their input data
        to onnx format for interoperability.

        Args:
            model (BaseEstimator, Pipeline): A machine learning model or pipeline to convert.
            Currently accepted types are any Sklearn model flavor, lightgbm and xgboost
            (sklearn flavors, e.g., LGBRegressor), as well as Sklearn pipelines.
            input_data (pd.DataFrame, np.ndarray): Sample model input data.

    """

    def convert_model(self) -> Tuple[ModelDefinition, Dict[str, Feature]]:

        converter = next(
            (
                converter
                for converter in ModelConverter.__subclasses__()
                if converter.validate(
                    model_type=self.model_type,
                )
            )
        )

        return converter(
            model=self.model,
            input_data=self.data,
            model_type=self.model_type,
        ).convert()
