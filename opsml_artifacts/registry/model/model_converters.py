# pylint: disable=[import-outside-toplevel,import-error]

"""Code for generating Onnx Models"""
import tempfile
from typing import Any, Dict, List, Optional, Tuple, Union, cast
import numpy as np
from numpy.typing import NDArray
import onnx
import onnxruntime as rt
import pandas as pd
from google.protobuf.internal.containers import RepeatedCompositeFieldContainer
from onnx.onnx_ml_pb2 import ModelProto  # pylint: disable=no-name-in-module

from opsml_artifacts.helpers.logging import ArtifactLogger
from opsml_artifacts.registry.model.data_converters import OnnxDataConverter
from opsml_artifacts.registry.model.registry_updaters import OnnxRegistryUpdater
from opsml_artifacts.registry.model.types import (
    LIGHTGBM_SUPPORTED_MODEL_TYPES,
    SKLEARN_SUPPORTED_MODEL_TYPES,
    UPDATE_REGISTRY_MODELS,
    Feature,
    ModelDefinition,
    OnnxDataProto,
    OnnxModelReturn,
    OnnxModelType,
    TorchOnnxArgs,
    ModelInfo,
)

ONNX_VERSION = onnx.__version__
logger = ArtifactLogger.get_logger(__name__)


class ModelConverter:
    def __init__(self, model_info: ModelInfo):

        self.model_info = model_info
        self.data_converter = OnnxDataConverter(model_info=model_info)

    def update_onnx_registries(self) -> bool:
        return OnnxRegistryUpdater.update_onnx_registry(model_estimator_name=self.model_info.model_type)

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

        model_preds = self.model_info.model.predict(self.model_info.input_data)

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

    def _parse_onnx_sigature(self, signature: RepeatedCompositeFieldContainer):
        feature_dict = {}

        for sig in signature:

            data_type = self._get_data_elem_type(sig=sig)
            shape_dims = sig.type.tensor_type.shape.dim
            dim_shape = [dim.dim_value for dim in shape_dims]
            if dim_shape:
                dim_shape[0] = None  # set None for dynamic batch size

            feature_dict[sig.name] = Feature(
                feature_type=OnnxDataProto(data_type).name,
                shape=dim_shape,
            )
        return feature_dict

    def create_feature_dict(self, onnx_model: ModelProto) -> Tuple[Dict[str, Feature], Dict[str, Feature]]:

        input_dict = self._parse_onnx_sigature(onnx_model.graph.input)
        output_dict = self._parse_onnx_sigature(onnx_model.graph.output)

        return input_dict, output_dict

    def create_model_def(self, onnx_model: ModelProto) -> ModelDefinition:
        """Creates Model definition

        Args:
            onnx_model (ModelProto): Onnx model
        """
        return ModelDefinition(
            onnx_version=ONNX_VERSION,
            model_bytes=onnx_model.SerializeToString(),
        )

    def convert(self) -> OnnxModelReturn:
        """Converts model to onnx model, validates it, and create an
        onnx feature dictionary

        Returns:
            Onnx ModelDefinition and Dictionary of Onnx features
        """
        onnx_model, data_schema = self.convert_model()
        model_def = self.create_model_def(onnx_model=onnx_model)
        input_onnx_features, output_onnx_features = self.create_feature_dict(onnx_model=onnx_model)

        return OnnxModelReturn(
            model_definition=model_def,
            onnx_input_features=input_onnx_features,
            onnx_output_features=output_onnx_features,
            data_schema=data_schema,
        )

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
        return self.model_info.model_type == OnnxModelType.STACKING_ESTIMATOR

    def _is_pipeline(self):
        return self.model_info.model_type == OnnxModelType.SKLEARN_PIPELINE

    def _update_onnx_registries_pipelines(self):
        updated = False
        for model_step in self.model_info.model.steps:
            estimator_name = model_step[1].__class__.__name__.lower()
            if estimator_name in UPDATE_REGISTRY_MODELS:
                OnnxRegistryUpdater.update_onnx_registry(
                    model_estimator_name=estimator_name,
                )
                updated = True
        return updated

    def _update_onnx_registries_stacking(self):
        updated = False
        for estimator in [
            *self.model_info.model.estimators_,
            self.model_info.model.final_estimator,
        ]:
            estimator_name = estimator.__class__.__name__.lower()
            if estimator_name in UPDATE_REGISTRY_MODELS:
                OnnxRegistryUpdater.update_onnx_registry(
                    model_estimator_name=estimator_name,
                )
                updated = True
        return updated

    def update_sklearn_onnx_registries(self) -> bool:
        if self._is_pipeline():
            return self._update_onnx_registries_pipelines()
        if self._is_stacking_estimator():
            return self._update_onnx_registries_stacking()
        return self.update_onnx_registries()

    def _convert_data_for_onnx(self):
        if self._is_stacking_estimator():
            logger.warning("Converting all numeric data to float32 for Sklearn Stacking")
            self.data_converter.converter.convert_all_to_float32()

        else:
            logger.warning("Converting all float64 data to float32 for Sklearn Pipeline")
            self.data_converter.converter.convert_float64_to_float32()  # lgb and xgb onnx do not support float64 (in intermediate nodes)

    def convert_model(self) -> Tuple[ModelProto, Optional[Dict[str, Feature]]]:

        """Converts sklearn model to ONNX ModelProto"""
        from skl2onnx import convert_sklearn

        updated = self.update_sklearn_onnx_registries()

        if updated:
            self._convert_data_for_onnx()

        initial_types, data_schema = self.get_data_types()

        onnx_model = convert_sklearn(
            model=self.model_info.model,
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
            model=self.model_info.model,
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
        onnx_model, _ = tf2onnx.convert.from_keras(
            self.model_info.model,
            initial_types,
            opset=13,
        )
        self.validate_model(onnx_model=onnx_model)

        return onnx_model, data_schema

    @staticmethod
    def validate(model_type: str) -> bool:
        return model_type in OnnxModelType.TF_KERAS


class PytorchArgBuilder:
    def __init__(
        self,
        input_data: Union[NDArray, Dict[str, NDArray]],
    ):
        self.input_data = input_data

    def _get_input_names(self) -> List[str]:
        if isinstance(self.model_info.input_data, dict):
            return [input_name for input_name in self.model_info.input_data.keys()]

        return ["input"]

    def _get_output_names(self) -> List[str]:
        return ["output"]

    def get_args(self) -> TorchOnnxArgs:
        input_names = self._get_input_names()
        output_names = self._get_output_names()

        return TorchOnnxArgs(
            input_names=input_names,
            output_names=output_names,
        )


class PyTorchOnnxModel(ModelConverter):
    def __init__(self, model_info: ModelInfo):

        additional_args = self._get_additional_model_args(
            additional_onnx_args=model_info.additional_model_args,
            input_data=model_info.input_data,
        )
        model_info.additional_model_args = additional_args

        super().__init__(model_info=model_info)

    def _get_additional_model_args(
        self,
        input_data: Any,
        additional_onnx_args: Optional[TorchOnnxArgs] = None,
    ):
        """Passes or creates TorchOnnxArgs needed for Onnx model conversion"""

        if additional_onnx_args is None:
            return PytorchArgBuilder(input_data=input_data).get_args()
        return additional_onnx_args

    def _predictions_close(
        self,
        onnx_preds: List[Any],
        model_preds: NDArray,
    ) -> bool:

        valid_list = [np.sum(abs(onnx_preds[0] - model_preds)) <= 0.001]

        return all(valid_list)

    def _post_process_prediction(self, predictions: Any) -> NDArray:
        """Parse pytorch predictions"""

        if hasattr(predictions, "logits"):
            return predictions.logits.detach().numpy()
        return predictions.detach().numpy()

    def _model_predict(self) -> NDArray:
        """Generate prediction for pytorch model using sample data"""

        torch_data = self._get_torch_data()

        if isinstance(torch_data, tuple):
            pred = self.model_info.model(*torch_data)

        elif isinstance(torch_data, dict):
            pred = self.model_info.model(**torch_data)

        else:
            pred = self.model_info.model(torch_data)

        return self._post_process_prediction(predictions=pred)

    def validate_model(self, onnx_model: ModelProto) -> None:

        """Validates an onnx model on sample data"""
        inputs = self.data_converter.convert_data()
        model_preds = self._model_predict()

        logger.info("Validating converted onnx model")

        model_string = onnx_model.SerializeToString()
        sess = rt.InferenceSession(model_string)
        onnx_preds = sess.run(None, inputs)

        if not self._predictions_close(
            onnx_preds=onnx_preds,
            model_preds=model_preds,
        ):
            raise ValueError("Model prediction validation failed")

        logger.info("Onnx model validated")

    def _get_torch_data(self) -> Any:
        import torch

        if isinstance(self.model_info.input_data, tuple):
            return tuple(torch.from_numpy(data) for data in self.model_info.input_data)

        if isinstance(self.model_info.input_data, dict):
            return {
                name: torch.from_numpy(data) for name, data in self.model_info.input_data.items()
            }  # pylint: disable=no-member

        return torch.from_numpy(self.model_info.input_data)  # pylint: disable=no-member

    def _get_onnx_model(self) -> ModelProto:
        """Converts Pytorch model into Onnx model through torch.onnx.export method"""

        import torch

        arg_data = self._get_torch_data()
        with tempfile.TemporaryDirectory() as tmp_dir:
            filename = f"{tmp_dir}/model.onnx"
            self.model_info.model.eval()  # force model into evaluation mode
            torch.onnx.export(
                model=self.model_info.model,
                args=arg_data,
                f=filename,
                **self.model_info.additional_model_args.to_dict(),
            )
            onnx.checker.check_model(filename)
            model = onnx.load(filename)
        return model

    def convert_model(self) -> Tuple[ModelProto, Optional[Dict[str, Feature]]]:
        """Converts a tensorflow keras model"""

        _, data_schema = self.get_data_types()
        onnx_model = self._get_onnx_model()
        self.validate_model(onnx_model=onnx_model)

        return onnx_model, data_schema

    @staticmethod
    def validate(model_type: str) -> bool:
        return model_type in OnnxModelType.PYTORCH


class OnnxModelConverter:
    def __init__(self, model_info: ModelInfo):
        """Instantiates a helper class to convert machine learning models and their input data
        to onnx format for interoperability.

        Args:
            model_info (ModelInfo): ModelInfo class containing model-specific information for Onnx conversion

        """
        self.model_info = model_info

    def convert_model(self) -> OnnxModelReturn:

        converter = next(
            (
                converter
                for converter in ModelConverter.__subclasses__()
                if converter.validate(model_type=self.model_info.model_type)
            )
        )

        return converter(model_info=self.model_info).convert()
