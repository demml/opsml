# pylint: disable=[import-outside-toplevel,import-error,no-name-in-module]

"""Code for generating Onnx Models"""
# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import Any, List, cast

from onnx import ModelProto

from opsml.helpers.logging import ArtifactLogger
from opsml.model.interfaces.tf import TensorFlowModel
from opsml.model.onnx.base_converter import _ModelConverter
from opsml.types import TrainedModelType

logger = ArtifactLogger.get_logger()


class _TensorflowKerasOnnxModel(_ModelConverter):
    @property
    def interface(self) -> TensorFlowModel:
        return cast(TensorFlowModel, self._interface)

    def _get_onnx_model_from_tuple(self, model: Any) -> Any:
        if isinstance(model, tuple):
            return model[0]
        return model

    def convert_model(self, initial_types: List[Any]) -> ModelProto:
        """Converts a tensorflow keras model"""
        logger.info("Staring conversion of TensorFlow model to ONNX")

        import tf2onnx

        onnx_model, _ = tf2onnx.convert.from_keras(self.trained_model, initial_types)

        return cast(ModelProto, onnx_model)

    @staticmethod
    def validate(model_class: str) -> bool:
        return model_class in TrainedModelType.TF_KERAS
