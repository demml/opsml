# pylint: disable=[import-outside-toplevel,import-error,no-name-in-module]

"""Code for generating Onnx Models"""
# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import re
import tempfile
import warnings
from collections import OrderedDict
from functools import reduce
from typing import Any, Dict, List, Optional, Tuple, Union, cast

import numpy as np
from google.protobuf.internal.containers import RepeatedCompositeFieldContainer
from numpy.typing import NDArray

from opsml.helpers.logging import ArtifactLogger
from opsml.helpers.utils import OpsmlImportExceptions
from opsml.model.data_converters import OnnxDataConverter
from opsml.model.data_helper import ModelDataHelper
from opsml.model.model_types import ModelType
from opsml.model.registry_updaters import OnnxRegistryUpdater
from opsml.model.types import (
    LIGHTGBM_SUPPORTED_MODEL_TYPES,
    SKLEARN_SUPPORTED_MODEL_TYPES,
    UPDATE_REGISTRY_MODELS,
    ApiDataSchemas,
    BaseEstimator,
    DataDict,
    ExtraOnnxArgs,
    Feature,
    ModelCard,
    ModelProto,
    ModelReturn,
    OnnxDataProto,
    OnnxModelDefinition,
    TrainedModelType,
)

logger = ArtifactLogger.get_logger()


try:
    import onnx
    import onnxruntime as rt

except ModuleNotFoundError as import_error:
    logger.error(
        """Failed to import onnx and onnxruntime. Please install onnx and onnxruntime via opsml extras
        If you wish to convert your model to onnx"""
    )
    raise import_error


class ModelConverter:
    def __init__(self, modelcard: ModelCard, data_helper: ModelDataHelper):
        self.card = modelcard
        self.data_helper = data_helper
        self.data_converter = OnnxDataConverter(
            modelcard=modelcard,
            data_helper=data_helper,
        )

    @property
    def model_type(self) -> str:
        return self.card.metadata.model_type

    @property
    def trained_model(self) -> Any:
        return self.card.trained_model

    @property
    def onnx_model_def(self) -> Optional[OnnxModelDefinition]:
        return self.card.metadata.onnx_model_def

    @property
    def is_sklearn_classifier(self) -> bool:
        """Checks if model is a classifier"""

        from sklearn.base import is_classifier

        return bool(is_classifier(self.trained_model))

    def update_onnx_registries(self) -> bool:
        return OnnxRegistryUpdater.update_onnx_registry(
            model_estimator_name=self.model_type,
        )

    def convert_model(self, initial_types: List[Any]) -> ModelProto:
        """Converts a model to onnx format

        Returns
            Encrypted model definition
        """
        raise NotImplementedError

    def get_data_types(self) -> Tuple[List[Any], Optional[Dict[str, Feature]]]:
        """Converts data for onnx

        Returns
            Encrypted model definition
        """

        if self.model_type in [*SKLEARN_SUPPORTED_MODEL_TYPES, *LIGHTGBM_SUPPORTED_MODEL_TYPES]:
            OpsmlImportExceptions.try_skl2onnx_imports()

        elif self.model_type == TrainedModelType.TF_KERAS:
            OpsmlImportExceptions.try_tf2onnx_imports()

        return self.data_converter.get_data_types()

    def _raise_shape_mismatch(self, onnx_shape: Tuple[int, ...], pred_shape: Tuple[int, ...]) -> None:
        raise ValueError(
            f"""Onnx and model prediction shape mismatch. \n
                Onnx prediction shape: {onnx_shape} \n
                Model prediction shape: {pred_shape}
            """
        )

    def _validate_pred_arrays(self, onnx_preds: NDArray[Any], model_preds: NDArray[Any]) -> bool:
        """
        Validates onnx and original model predictions. Checks whether average diff between model and onnx
        is <= .001.

        Args:
            onnx_preds:
                Array of onnx model predictions
            model_preds:
                Array of model predictions
        Returns:
            bool indicating if onnx model prediction is close to original model
        """

        if model_preds.ndim != onnx_preds.ndim:
            if model_preds.ndim < onnx_preds.ndim:
                # onnx tends to add an extra dim
                if onnx_preds.shape[0] == 1:
                    onnx_preds = onnx_preds[0]
                else:
                    self._raise_shape_mismatch(onnx_preds.shape, model_preds.shape)
            else:
                self._raise_shape_mismatch(onnx_preds.shape, model_preds.shape)

        # assert shapes match
        assert onnx_preds.shape == model_preds.shape

        diff = np.sum(abs(np.around(onnx_preds, 4) - np.around(model_preds, 4)))
        n_values = reduce((lambda x, y: x * y), model_preds.shape)
        avg_diff = np.divide(diff, n_values)

        # check if raw diff value is less than a certain amount
        if avg_diff <= 0.001:
            return True

        return False

    def _predictions_close(
        self,
        onnx_preds: List[Union[float, int, NDArray[Any]]],
        model_preds: Union[List[Union[float, int]], Union[float, int], NDArray[Any]],
    ) -> bool:  # pragma: no cover
        """Checks if model and onnx predictions are close

        Args:
            onnx_preds:
                Onnx model predictions
            model_preds:
                Model predictions
        Returns:
            Bool indicating if onnx and original model predictions are close
        """

        if isinstance(onnx_preds, list) and isinstance(model_preds, list):
            valid_list = []
            for onnx_pred, model_pred in zip(onnx_preds, model_preds):
                valid = np.sum(np.abs(onnx_pred - model_pred)) <= 0.001
                valid_list.append(valid)
            return all(valid_list)

        if isinstance(model_preds, np.ndarray):
            onnx_pred = onnx_preds[0]
            if isinstance(onnx_pred, np.ndarray):
                return self._validate_pred_arrays(onnx_pred, model_preds)
            raise ValueError("Model and onnx predictions should both be of type NDArray")

        valid_list = [np.sum(np.abs(onnx_preds[0] - model_preds)) <= 0.001]
        return all(valid_list)

    def validate_model(self, onnx_model: ModelProto) -> None:
        """Validates an onnx model on training data"""
        inputs = self.data_converter.convert_data()
        model_preds = self.trained_model.predict(self.data_helper.data)

        logger.info("Validating converted onnx model")
        sess = self._create_onnx_session(onnx_model=onnx_model)

        onnx_preds = sess.run(None, inputs)
        if not self._predictions_close(onnx_preds=onnx_preds, model_preds=model_preds):
            raise ValueError("Model prediction validation failed")

        logger.info("Onnx model validated")

    def _get_data_elem_type(self, sig: Any) -> int:
        return int(sig.type.tensor_type.elem_type)

    def _parse_onnx_signature(self, signature: RepeatedCompositeFieldContainer) -> Dict[str, Feature]:  # type: ignore[type-arg]
        feature_dict = {}

        for sig in signature:
            data_type = self._get_data_elem_type(sig=sig)
            shape_dims = sig.type.tensor_type.shape.dim

            dim_shape = [dim.dim_value for dim in shape_dims]
            if dim_shape:
                dim_shape[0] = None  # set None for dynamic batch size

            if sig.name == "variable":
                name = "value"
            else:
                name = sig.name

            feature_dict[name] = Feature(
                feature_type=OnnxDataProto(data_type).name,
                shape=dim_shape,
            )

        return feature_dict

    def create_feature_dict(self, onnx_model: ModelProto) -> Tuple[Dict[str, Feature], Dict[str, Feature]]:
        """Creates feature dictionary from onnx model

        Args:
            onnx_model:
                Onnx model
        Returns:
            Tuple of input and output feature dictionaries
        """
        input_dict = self._parse_onnx_signature(onnx_model.graph.input)
        output_dict = self._parse_onnx_signature(onnx_model.graph.output)

        return input_dict, output_dict

    def create_model_def(self, onnx_model: ModelProto) -> OnnxModelDefinition:
        """Creates Model definition

        Args:
            onnx_model:
                Onnx model
        """

        return OnnxModelDefinition(
            onnx_version=onnx.__version__,  # type: ignore
            model_bytes=onnx_model.SerializeToString(),
        )

    def _create_onnx_model(
        self, initial_types: List[Any]
    ) -> Tuple[OnnxModelDefinition, Dict[str, Feature], Dict[str, Feature]]:
        """Creates onnx model, validates it, and creates an onnx feature dictionary

        Args:
            initial_types:
                Initial types for onnx model

        Returns:
            Tuple containing onnx model, input features, and output features
        """

        onnx_model = self.convert_model(initial_types=initial_types)
        input_onnx_features, output_onnx_features = self.create_feature_dict(onnx_model=onnx_model)
        model_def = self.create_model_def(onnx_model=onnx_model)

        return model_def, input_onnx_features, output_onnx_features

    def _load_onnx_model(self) -> Tuple[OnnxModelDefinition, Dict[str, Feature], Dict[str, Feature]]:
        """
        Loads onnx model from model definition

        Returns:
            Tuple containing onnx model definition, input features, and output features
        """
        assert isinstance(self.onnx_model_def, OnnxModelDefinition)
        onnx_model = onnx.load_from_string(self.onnx_model_def.model_bytes)
        input_onnx_features, output_onnx_features = self.create_feature_dict(onnx_model=cast(ModelProto, onnx_model))

        return self.onnx_model_def, input_onnx_features, output_onnx_features

    def convert(self) -> ModelReturn:
        """Converts model to onnx model, validates it, and creates an
        onnx feature dictionary

        Returns:
            ModelReturn object containing model definition and api data schema
        """
        initial_types, data_schema = self.get_data_types()

        if self.onnx_model_def is None:
            model_def, input_onnx_features, output_onnx_features = self._create_onnx_model(initial_types)

        else:
            model_def, input_onnx_features, output_onnx_features = self._load_onnx_model()

        schema = ApiDataSchemas(
            model_data_schema=DataDict(
                input_features=input_onnx_features,
                output_features=output_onnx_features,
            ),
            input_data_schema=data_schema,
        )

        return ModelReturn(model_definition=model_def, api_data_schema=schema)

    def _create_onnx_session(self, onnx_model: ModelProto) -> rt.InferenceSession:
        return rt.InferenceSession(
            path_or_bytes=onnx_model.SerializeToString(),
            providers=rt.get_available_providers(),  # failure when not setting default providers as of rt 1.16
        )

    @staticmethod
    def validate(model_type: str) -> bool:
        """validates model base class"""
        raise NotImplementedError


class SklearnOnnxModel(ModelConverter):
    """Class for converting sklearn models to onnx format"""

    @property
    def _is_stacking_estimator(self) -> bool:
        return self.model_type == TrainedModelType.STACKING_ESTIMATOR

    @property
    def _is_calibrated_classifier(self) -> bool:
        return self.card.metadata.model_class.lower() == TrainedModelType.CALIBRATED_CLASSIFIER

    @property
    def _is_pipeline(self) -> bool:
        return self.model_type == TrainedModelType.SKLEARN_PIPELINE

    def _update_onnx_registries_pipelines(self) -> bool:
        updated = False

        for model_step in self.trained_model.steps:
            estimator_name = model_step[1].__class__.__name__.lower()

            if estimator_name == TrainedModelType.CALIBRATED_CLASSIFIER:
                updated = self._update_onnx_registries_calibrated_classifier(estimator=model_step[1].estimator)

            # check if estimator is calibrated
            elif estimator_name in UPDATE_REGISTRY_MODELS:
                OnnxRegistryUpdater.update_onnx_registry(
                    model_estimator_name=estimator_name,
                )
                updated = True
        return updated

    def _update_onnx_registries_stacking(self) -> bool:
        updated = False
        for estimator in [
            *self.trained_model.estimators_,
            self.trained_model.final_estimator,
        ]:
            estimator_name = estimator.__class__.__name__.lower()
            if estimator_name in UPDATE_REGISTRY_MODELS:
                OnnxRegistryUpdater.update_onnx_registry(
                    model_estimator_name=estimator_name,
                )
                updated = True
        return updated

    def _update_onnx_registries_calibrated_classifier(self, estimator: Optional[BaseEstimator] = None) -> bool:
        updated = False

        if estimator is None:
            estimator = self.trained_model.estimator

        model_type = next(
            (
                model_type
                for model_type in ModelType.__subclasses__()
                if model_type.validate(model_class_name=estimator.__class__.__name__)
            )
        )
        estimator_type = model_type.get_type()

        if estimator_type in UPDATE_REGISTRY_MODELS:
            OnnxRegistryUpdater.update_onnx_registry(
                model_estimator_name=estimator_type,
            )
            updated = True

        return updated

    def update_sklearn_onnx_registries(self) -> bool:
        if self._is_pipeline:
            return self._update_onnx_registries_pipelines()

        if self._is_stacking_estimator:
            return self._update_onnx_registries_stacking()

        if self._is_calibrated_classifier:
            return self._update_onnx_registries_calibrated_classifier()

        return self.update_onnx_registries()

    def _convert_data_for_onnx(self) -> None:
        """
        Converts float64 or all data to float32 depending on Sklearn estimator type
        Because Stacking and Pipeline estimators have intermediate output nodes, Onnx will
        typically inject Float32 for these outputs (it infers these at creation). In addition,
        skl2onnx does not handle Float64 for some model types (some classifiers). Because of this,
        all Float64 types are converted to Float32 for all models.
        """

        if self.data_helper.all_features_float32:
            pass

        elif self._is_stacking_estimator:
            logger.warning("Converting all numeric data to float32 for Sklearn Stacking")
            self.data_converter.converter.convert_to_float(convert_all=True)

        elif not self._is_pipeline and self.data_helper.num_dtypes > 1:
            self.data_converter.converter.convert_to_float(convert_all=True)

        else:
            logger.warning("Converting all float64 data to float32")
            self.data_converter.converter.convert_to_float(convert_all=False)

    def prepare_registries_and_data(self) -> None:
        """Updates sklearn onnx registries and convert data to float32"""

        self.update_sklearn_onnx_registries()
        self._convert_data_for_onnx()

    def get_data_types(self) -> Tuple[List[Any], Optional[Dict[str, Feature]]]:
        """Converts data for sklearn onnx models"""
        self.prepare_registries_and_data()
        return super().get_data_types()

    @property
    def options(self) -> Optional[Dict[str, Any]]:
        """Sets onnx options for model conversion

        Our inference implementation uses triton for onnx hosting which does not support sequence output
        for classification models (skl2onnx default). This defaults all sklearn classifiers to an array output
        """
        add_model_args = self.card.metadata.additional_onnx_args
        options = getattr(add_model_args, "options", None)

        if self.is_sklearn_classifier and options is None:
            return {"zipmap": False}
        return options

    def _convert_sklearn(self, initial_types: List[Any]) -> ModelProto:
        """Converts an sklearn model to onnx using skl2onnx library

        Args:
            initial_types:
                List of data types the onnx model should expect
        Returns:
            `ModelProto`
        """
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            from skl2onnx import convert_sklearn

        try:
            return cast(
                ModelProto,
                convert_sklearn(
                    model=self.trained_model,
                    initial_types=initial_types,
                    options=self.options,
                ),
            )
        except NameError as name_error:
            # There may be a small amount of instances where a sklearn classifier does
            # not support zipmap as a default option (LinearSVC). This catches those errors
            if re.search("Option 'zipmap' not in", str(name_error), re.IGNORECASE):
                logger.info("Zipmap not supported for classifier")
                return cast(ModelProto, convert_sklearn(model=self.trained_model, initial_types=initial_types))
            raise name_error

    def convert_model(self, initial_types: List[Any]) -> ModelProto:
        """Converts sklearn model to ONNX ModelProto"""

        onnx_model = self._convert_sklearn(initial_types=initial_types)

        self.validate_model(onnx_model=onnx_model)
        return onnx_model

    @staticmethod
    def validate(model_type: str) -> bool:
        return model_type in SKLEARN_SUPPORTED_MODEL_TYPES


class LightGBMBoosterOnnxModel(ModelConverter):
    def convert_model(self, initial_types: List[Any]) -> ModelProto:
        """Converts sklearn model to ONNX ModelProto"""
        from onnxmltools import convert_lightgbm

        onnx_model = convert_lightgbm(model=self.trained_model, initial_types=initial_types)
        self.validate_model(onnx_model=onnx_model)

        return cast(ModelProto, onnx_model)

    @staticmethod
    def validate(model_type: str) -> bool:
        return model_type in LIGHTGBM_SUPPORTED_MODEL_TYPES


class TensorflowKerasOnnxModel(ModelConverter):
    def _get_onnx_model_from_tuple(self, model: Any) -> Any:
        if isinstance(model, tuple):
            return model[0]
        return model

    def convert_model(self, initial_types: List[Any]) -> ModelProto:
        """Converts a tensorflow keras model"""

        import tf2onnx

        onnx_model, _ = tf2onnx.convert.from_keras(self.trained_model, initial_types, opset=13)
        self.validate_model(onnx_model=onnx_model)

        return cast(ModelProto, onnx_model)

    @staticmethod
    def validate(model_type: str) -> bool:
        return model_type in TrainedModelType.TF_KERAS


class PytorchArgBuilder:
    def __init__(
        self,
        input_data: Union[NDArray[Any], Dict[str, NDArray[Any]]],
    ):
        self.input_data = input_data

    def _get_input_names(self) -> List[str]:
        if isinstance(self.input_data, dict):
            return list(self.input_data.keys())

        return ["predict"]

    def _get_output_names(self) -> List[str]:
        return ["output"]

    def get_args(self) -> ExtraOnnxArgs:
        input_names = self._get_input_names()
        output_names = self._get_output_names()

        return ExtraOnnxArgs(
            input_names=input_names,
            output_names=output_names,
        )


class PyTorchOnnxModel(ModelConverter):
    def __init__(self, modelcard: ModelCard, data_helper: ModelDataHelper):
        modelcard.metadata.additional_onnx_args = self._get_additional_model_args(
            additional_onnx_args=modelcard.metadata.additional_onnx_args,
            input_data=data_helper.data,
        )
        super().__init__(modelcard=modelcard, data_helper=data_helper)

    def _get_additional_model_args(
        self,
        input_data: Any,
        additional_onnx_args: Optional[ExtraOnnxArgs] = None,
    ) -> ExtraOnnxArgs:
        """Passes or creates ExtraOnnxArgs needed for Onnx model conversion"""

        if additional_onnx_args is None:
            return PytorchArgBuilder(input_data=input_data).get_args()
        return additional_onnx_args

    def _post_process_prediction(self, predictions: Any) -> NDArray[Any]:
        """Parse pytorch predictions"""

        if hasattr(predictions, "logits"):
            return predictions.logits.detach().numpy()  # type: ignore
        if hasattr(predictions, "detach"):
            return predictions.detach().numpy()  # type: ignore
        if hasattr(predictions, "last_hidden_state"):
            return predictions.last_hidden_state.detach().numpy()  # type: ignore

        # for vision model
        if isinstance(predictions, OrderedDict):
            return predictions["out"].detach().numpy()  # type: ignore

        return predictions.numpy()  # type: ignore

    def _model_predict(self) -> NDArray[Any]:
        """Generate prediction for pytorch model using sample data"""

        torch_data = self._get_torch_data()

        if isinstance(torch_data, tuple):
            pred = self.trained_model(*torch_data)

        elif isinstance(torch_data, dict):
            pred = self.trained_model(**torch_data)

        else:
            pred = self.trained_model(torch_data)

        return self._post_process_prediction(predictions=pred)

    def validate_model(self, onnx_model: ModelProto) -> None:
        """Validates an onnx model on sample data"""
        inputs = self.data_converter.convert_data()
        model_preds = self._model_predict()

        logger.info("Validating converted onnx model")
        sess = self._create_onnx_session(onnx_model=onnx_model)

        onnx_preds = sess.run(None, inputs)

        if not self._predictions_close(
            onnx_preds=onnx_preds,
            model_preds=model_preds,
        ):
            logger.error("Onnx prediction validation failed")
            raise ValueError("Model prediction validation failed")

        logger.info("Onnx model validated")

    def _get_torch_data(self) -> Any:
        import torch

        if isinstance(self.data_helper.data, tuple):
            return tuple(torch.from_numpy(data) for data in self.data_helper.data)  # pylint: disable=no-member

        if isinstance(self.data_helper.data, dict):
            return {
                name: torch.from_numpy(data)  # pylint: disable=no-member
                for name, data in self.data_helper.data.items()
            }

        return torch.from_numpy(self.data_helper.data)  # pylint: disable=no-member

    def _get_onnx_model(self) -> ModelProto:
        """Converts Pytorch model into Onnx model through torch.onnx.export method"""

        import torch

        arg_data = self._get_torch_data()

        assert isinstance(self.card.metadata.additional_onnx_args, ExtraOnnxArgs)
        with tempfile.TemporaryDirectory() as tmp_dir:
            filename = f"{tmp_dir}/model.onnx"
            self.trained_model.eval()  # force model into evaluation mode
            torch.onnx.export(
                model=self.trained_model,
                args=arg_data,
                f=filename,
                **self.card.metadata.additional_onnx_args.model_dump(exclude={"options"}),
            )
            onnx.checker.check_model(filename)
            model = onnx.load(filename)

        return cast(ModelProto, model)

    def convert_model(self, initial_types: List[Any]) -> ModelProto:
        """Converts a tensorflow keras model"""

        onnx_model = self._get_onnx_model()
        self.validate_model(onnx_model=onnx_model)

        return onnx_model

    @staticmethod
    def validate(model_type: str) -> bool:
        return model_type in [
            TrainedModelType.PYTORCH,
            TrainedModelType.TRANSFORMER,
        ]


class OnnxModelConverter:
    @staticmethod
    def convert_model(modelcard: ModelCard, data_helper: ModelDataHelper) -> ModelReturn:
        """
        Instantiates a helper class to convert machine learning models and their input
        data to onnx format for interoperability.


        Args:
            modelcard:
                ModelCard class containing model-specific information for Onnx conversion
            data_helper:
                ModelDataHelper class containing model-specific information for Onnx conversion

        """

        converter = next(
            (
                converter
                for converter in ModelConverter.__subclasses__()
                if converter.validate(model_type=modelcard.metadata.model_type)
            )
        )

        return converter(
            modelcard=modelcard,
            data_helper=data_helper,
        ).convert()
