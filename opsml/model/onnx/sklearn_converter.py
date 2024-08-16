# pylint: disable=[import-outside-toplevel,import-error,no-name-in-module]

"""Code for generating Onnx Models"""
# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import re
import warnings
from typing import Any, Dict, List, Optional, cast

from onnx import ModelProto

from opsml.helpers.logging import ArtifactLogger
from opsml.model.onnx.base_converter import _ModelConverter
from opsml.model.onnx.registry_updaters import OnnxRegistryUpdater
from opsml.model.utils.data_helper import FloatTypeConverter
from opsml.types import (
    SKLEARN_SUPPORTED_MODEL_TYPES,
    UPDATE_REGISTRY_MODELS,
    BaseEstimator,
    ModelType,
    TrainedModelType,
)

logger = ArtifactLogger.get_logger()


class _SklearnOnnxModel(_ModelConverter):
    """Class for converting sklearn models to onnx format"""

    @property
    def _is_stacking_estimator(self) -> bool:
        return self.model_type in (TrainedModelType.STACKING_REGRESSOR, TrainedModelType.STACKING_CLASSIFIER)

    @property
    def _is_calibrated_classifier(self) -> bool:
        return self.model_type == TrainedModelType.CALIBRATED_CLASSIFIER

    @property
    def _is_pipeline(self) -> bool:
        return self.model_type == TrainedModelType.SKLEARN_PIPELINE

    def _update_onnx_registries_pipelines(self) -> bool:
        updated = False

        for model_step in self.trained_model.steps:
            estimator_name = model_step[1].__class__.__name__

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
            estimator_name = estimator.__class__.__name__
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
            self.data_helper.data = FloatTypeConverter(convert_all=True).convert_to_float(data=self.data_helper.data)

        elif not self._is_pipeline and self.data_helper.num_dtypes > 1:
            self.data_helper.data = FloatTypeConverter(convert_all=True).convert_to_float(data=self.data_helper.data)

        else:
            logger.warning("Converting all float64 data to float32")
            self.data_helper.data = FloatTypeConverter(convert_all=False).convert_to_float(data=self.data_helper.data)

    def prepare_registries_and_data(self) -> None:
        """Updates sklearn onnx registries and convert data to float32"""

        self.update_sklearn_onnx_registries()
        self._convert_data_for_onnx()

    def get_data_types(self) -> List[Any]:
        """Converts data for sklearn onnx models"""

        self.prepare_registries_and_data()
        return super().get_data_types()

    @property
    def options(self) -> Optional[Dict[str, Any]]:
        """Sets onnx options for model conversion

        Our inference implementation uses triton for onnx hosting which does not support sequence output
        for classification models (skl2onnx default). This defaults all sklearn classifiers to an array output
        """

        if hasattr(self.interface, "onnx_args"):
            add_model_args = self.interface.onnx_args
            options = getattr(add_model_args, "options", None)
        else:
            options = None

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
                    target_opset={
                        "": 19,
                        "ai.onnx.ml": 3,
                    },  # need to pin since skl2onnx is not in sync with latest onnx release
                    # opset 19/3 is the latest supported by skl2onnx (onnx v 1.14.1)
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

        logger.info("Staring conversion of sklearn model to ONNX")
        onnx_model = self._convert_sklearn(initial_types=initial_types)
        return onnx_model

    @staticmethod
    def validate(model_class: str) -> bool:
        return model_class in SKLEARN_SUPPORTED_MODEL_TYPES
