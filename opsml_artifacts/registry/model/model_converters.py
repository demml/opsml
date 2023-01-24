# pylint: disable=import-outside-toplevel
# break this out into separate files at some point (data_converter.py, model_converter.py)
"""Code for generating Onnx Models"""
from typing import Any, Dict, List, Optional, Tuple, Union, cast

import numpy as np
import onnxruntime as rt
import pandas as pd
from cryptography.fernet import Fernet
from google.protobuf.pyext._message import RepeatedCompositeContainer  # type:ignore
from onnx.onnx_ml_pb2 import ModelProto  # pylint: disable=no-name-in-module
from pyshipt_logging import ShiptLogging

from opsml_artifacts.registry.model.data_converters import OnnxDataConverter
from opsml_artifacts.registry.model.registry_updaters import OnnxRegistryUpdater
from opsml_artifacts.registry.model.types import (
    LIGHTGBM_SUPPORTED_MODEL_TYPES,
    SKLEARN_SUPPORTED_MODEL_TYPES,
    UPDATE_REGISTRY_MODELS,
    Feature,
    ModelDefinition,
    OnnxDataProto,
    OnnxModelType,
)

# Get logger
logger = ShiptLogging.get_logger(__name__)

ModelConvertOutput = Tuple[
    ModelDefinition,
    Dict[str, Feature],
    Dict[str, Feature],
    Optional[Dict[str, Feature]],
]


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
        self.data_converter = OnnxDataConverter(
            input_data=input_data,
            model_type=model_type,
            model=model,
        )

    def update_onnx_registries(self):
        OnnxRegistryUpdater.update_onnx_registry(model_estimator_name=self.model_type)

    def convert_model(self) -> Tuple[ModelProto, Optional[Dict[str, Feature]]]:
        """Converts a model to onnx format

        Returns
            Encrypted model definition and feature dictionary
        """
        raise NotImplementedError

    def _predictions_close(
        self,
        onnx_preds: List[Any],
        model_preds: Union[List[Any], Union[float, int]],
    ) -> bool:
        if not isinstance(model_preds, list):
            model_preds = cast(Union[float, int], model_preds)
            valid_list = [np.sum(abs(onnx_preds[0] - model_preds)) <= 0.001]
        else:
            valid_list = []
            for onnx_pred, model_pred in zip(onnx_preds, model_preds):
                valid = np.sum(abs(onnx_pred - model_pred)) <= 0.001
                valid_list.append(valid)

        return all(valid_list)

    def validate_model(self, onnx_model: ModelProto) -> None:
        """Validates an onnx model on training data"""
        inputs = self.data_converter.convert_data()

        # Get original prediction
        model_preds = self.model.predict(self.input_data)

        logger.info("Validating converted onnx model")
        sess = rt.InferenceSession(onnx_model.SerializeToString())
        onnx_preds = sess.run(None, inputs)

        if not self._predictions_close(onnx_preds=onnx_preds, model_preds=model_preds):
            raise ValueError("Model prediction validation failed")

        logger.info("Onnx model validated")

    def get_data_types(self) -> Tuple[List[Any], Optional[Dict[str, Feature]]]:
        return self.data_converter.get_data_types()

    def _get_data_elem_type(self, sig: Any) -> int:
        return sig.type.tensor_type.elem_type

    def _get_shape_dims(self, shape_dims: List[Any]) -> Tuple[Optional[int], Optional[int]]:
        row = shape_dims[0].dim_value
        col = shape_dims[1].dim_value

        if row == 0:
            row = None

        return row, col

    def _parse_onnx_sigature(self, signature: RepeatedCompositeContainer):
        feature_dict = {}

        for sig in signature:

            data_type = self._get_data_elem_type(sig=sig)
            shape_dims = sig.type.tensor_type.shape.dim
            row, col = self._get_shape_dims(shape_dims)

            feature_dict[sig.name] = Feature(
                feature_type=OnnxDataProto(data_type).name,
                shape=[row, col],
            )
        return feature_dict

    def create_feature_dict(self, onnx_model: ModelProto) -> Tuple[Dict[str, Feature], Dict[str, Feature]]:

        input_dict = self._parse_onnx_sigature(onnx_model.graph.input)
        output_dict = self._parse_onnx_sigature(onnx_model.graph.output)

        return input_dict, output_dict

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

    def convert(self) -> ModelConvertOutput:
        """Converts model to onnx model, validates it, and create an
        onnx feature dictionary

        Returns:
            Onnx ModelDefinition and Dictionary of Onnx features
        """
        onnx_model, data_schema = self.convert_model()
        model_def = self.encrypt_model(onnx_model=onnx_model)
        input_onnx_features, output_onnx_features = self.create_feature_dict(onnx_model=onnx_model)

        return model_def, input_onnx_features, output_onnx_features, data_schema

    @staticmethod
    def validate(model_type: str) -> bool:
        """validates model base class"""
        raise NotImplementedError


class SklearnOnnxModel(ModelConverter):
    def _get_shape_dims(self, shape_dims: List[Any]) -> Tuple[Optional[int], Optional[int]]:

        if len(shape_dims) == 0:
            return None, None

        row = shape_dims[0].dim_value

        if row == 0:
            row = None

        if len(shape_dims) > 1:
            col = shape_dims[1].dim_value

        else:
            col = 1

        return row, col

    def _is_stacking_estimator(self):
        return self.model_type == OnnxModelType.STACKING_ESTIMATOR

    def _is_pipeline(self):
        return self.model_type == OnnxModelType.SKLEARN_PIPELINE

    def _update_onnx_registries_pipelines(self):
        for model_step in self.model.steps:
            estimator_name = model_step[1].__class__.__name__.lower()
            if estimator_name in UPDATE_REGISTRY_MODELS:
                OnnxRegistryUpdater.update_onnx_registry(
                    model_estimator_name=estimator_name,
                )

    def _update_onnx_registries_stacking(self):
        for estimator in [*self.model.estimators_, self.model.final_estimator]:
            estimator_name = estimator.__class__.__name__.lower()
            if estimator_name in UPDATE_REGISTRY_MODELS:
                OnnxRegistryUpdater.update_onnx_registry(
                    model_estimator_name=estimator_name,
                )

    def update_sklearn_onnx_registries(self):
        if self._is_pipeline():
            return self._update_onnx_registries_pipelines()
        if self._is_stacking_estimator():
            return self._update_onnx_registries_stacking()
        return self.update_onnx_registries()

    def convert_model(self) -> Tuple[ModelProto, Optional[Dict[str, Feature]]]:

        """Converts sklearn model to ONNX ModelProto"""
        from skl2onnx import convert_sklearn

        self.update_sklearn_onnx_registries()
        initial_types, data_schema = self.get_data_types()
        onnx_model = convert_sklearn(
            model=self.model,
            initial_types=initial_types,
        )

        self.validate_model(onnx_model=onnx_model)

        return onnx_model, data_schema

    @staticmethod
    def validate(model_type: str) -> bool:
        return model_type in SKLEARN_SUPPORTED_MODEL_TYPES


class LighGBMBoosterOnnxModel(ModelConverter):
    def convert_model(self) -> Tuple[ModelProto, Optional[Dict[str, Feature]]]:

        """Converts sklearn model to ONNX ModelProto"""
        from onnxmltools import convert_lightgbm

        initial_types, data_schema = self.get_data_types()
        onnx_model = convert_lightgbm(
            model=self.model,
            initial_types=initial_types,
        )

        self.validate_model(onnx_model=onnx_model)

        return onnx_model, data_schema

    @staticmethod
    def validate(model_type: str) -> bool:
        return model_type in LIGHTGBM_SUPPORTED_MODEL_TYPES


class TensorflowKerasOnnxModel(ModelConverter):
    def _get_onnx_model_from_tuple(self, model: Any):
        if isinstance(model, tuple):
            return model[0]
        return model

    def convert_model(self) -> Tuple[ModelProto, Optional[Dict[str, Feature]]]:
        """Converts a tensorflow keras model"""

        import tf2onnx

        initial_types, data_schema = self.get_data_types()
        onnx_model, _ = tf2onnx.convert.from_keras(self.model, initial_types, opset=13)
        self.validate_model(onnx_model=onnx_model)

        return onnx_model, data_schema

    @staticmethod
    def validate(model_type: str) -> bool:
        return model_type in OnnxModelType.TF_KERAS


class OnnxModelConverter:
    def __init__(
        self,
        model: Any,
        input_data: Union[pd.DataFrame, np.ndarray, Dict[str, np.ndarray]],
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

    def convert_model(self) -> ModelConvertOutput:

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
