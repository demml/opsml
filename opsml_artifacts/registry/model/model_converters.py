# pylint: disable=import-outside-toplevel
# break this out into separate files at some point (data_converter.py, model_converter.py)
"""Code for generating Onnx Models"""
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import onnxruntime as rt
import pandas as pd
from cryptography.fernet import Fernet
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

ModelConvertOutput = Tuple[ModelDefinition, Dict[str, Feature], Optional[Dict[str, str]]]


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

    def update_onnx_registries(self):
        OnnxRegistryUpdater.update_onnx_registry(model_estimator_name=self.model_type)

    def convert_model(self) -> Tuple[ModelProto, Optional[Dict[str, str]]]:
        """Converts a model to onnx format

        Returns
            Encrypted model definition and feature dictionary
        """
        raise NotImplementedError

    def validate_model(self, onnx_model: ModelProto) -> None:
        """Validates an onnx model on training data"""
        inputs = OnnxDataConverter.convert_data(
            input_data=self.input_data,
            model_type=self.model_type,
        )

        logger.info("Validating converted onnx model")
        sess = rt.InferenceSession(onnx_model.SerializeToString())
        pred_onx = np.ravel(sess.run(None, inputs))[0]
        logger.info("Test Onnx prediction: %s", pred_onx)

    def get_data_types(self) -> Tuple[List[Any], Optional[Dict[str, str]]]:
        return OnnxDataConverter.get_data_types(
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

    def convert(self) -> ModelConvertOutput:
        """Converts model to onnx model, validates it, and create an
        onnx feature dictionary

        Returns:
            Onnx ModelDefinition and Dictionary of Onnx features
        """
        onnx_model, data_schema = self.convert_model()
        model_def = self.encrypt_model(onnx_model=onnx_model)
        features = self.create_feature_dict(onnx_model=onnx_model)

        return model_def, features, data_schema

    @staticmethod
    def validate(model_type: str) -> bool:
        """validates model base class"""
        raise NotImplementedError


class SklearnOnnxModel(ModelConverter):
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

    def convert_model(self) -> Tuple[ModelProto, Optional[Dict[str, str]]]:

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
    def convert_model(self) -> Tuple[ModelProto, Optional[Dict[str, str]]]:

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


class OnnxModelConverter:
    def __init__(
        self,
        model: Any,
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
