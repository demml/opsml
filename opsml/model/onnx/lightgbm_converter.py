# pylint: disable=[import-outside-toplevel,import-error,no-name-in-module]

"""Code for generating Onnx Models"""
# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import Any, List, cast

from onnx import ModelProto

from opsml.helpers.logging import ArtifactLogger
from opsml.model.onnx.base_converter import _ModelConverter
from opsml.types import LIGHTGBM_SUPPORTED_MODEL_TYPES

logger = ArtifactLogger.get_logger()


class _LightGBMBoosterOnnxModel(_ModelConverter):
    def convert_model(self, initial_types: List[Any]) -> ModelProto:
        """Converts lightgbm model to ONNX ModelProto"""
        from onnxmltools import convert_lightgbm

        logger.info("Staring conversion of LightGBM model to ONNX")

        onnx_model = convert_lightgbm(model=self.trained_model, initial_types=initial_types)

        return cast(ModelProto, onnx_model)

    @staticmethod
    def validate(model_class: str) -> bool:
        return model_class in LIGHTGBM_SUPPORTED_MODEL_TYPES
