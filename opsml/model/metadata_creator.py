# pylint: disable=no-member,broad-exception-caught
# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import Any, Dict

from opsml.helpers.logging import ArtifactLogger
from opsml.model.interfaces.base import ModelInterface
from opsml.model.utils.data_helper import get_model_data
from opsml.types import (
    AllowedDataType,
    DataSchema,
    Feature,
    ModelReturn,
    TrainedModelType,
)

logger = ArtifactLogger.get_logger()


class _ModelMetadataCreator:
    def __init__(self, model_interface: ModelInterface):
        """
        Args:
            model_interface:
                Interface to model
        """
        self.interface = model_interface

    @property
    def model(self) -> Any:
        """Return model from model interface"""
        if self.interface.model_class == TrainedModelType.PYTORCH_LIGHTNING:
            assert self.interface.model is not None, "No Trainer provided"
            assert self.interface.model.model is not None, "No model found in Trainer"
            return self.interface.model.model
        return self.interface.model

    @staticmethod
    def validate(to_onnx: bool) -> bool:
        raise NotImplementedError


class _TrainedModelMetadataCreator(_ModelMetadataCreator):
    def _get_input_schema(self) -> Dict[str, Feature]:
        try:
            model_data = get_model_data(
                data_type=self.interface.data_type,
                input_data=self.interface.sample_data,
            )

            return model_data.feature_dict
        except Exception as error:
            logger.error(
                """Failed to determine input type. This is expected for custom subclasses or unsupported data types. 
                Defaulting to placeholder. {}""",
                error,
            )

            return {"placeholder": Feature(feature_type="str", shape=[1])}

    def _get_output_schema(self) -> Dict[str, Feature]:
        try:
            sample_prediction = self.interface.get_sample_prediction()

            output_data = get_model_data(
                input_data=sample_prediction.prediction,
                data_type=sample_prediction.prediction_type,
            )

            # pandas will use column names as features
            if sample_prediction.prediction_type != AllowedDataType.PANDAS:
                output_data.features = ["outputs"]

            return output_data.feature_dict

        except Exception as error:
            logger.error("Failed to determine prediction output. Defaulting to placeholder. {}", error)

            return {"placeholder": Feature(feature_type="str", shape=[1])}

    def get_model_metadata(self) -> ModelReturn:
        output_features = self._get_output_schema()
        input_features = self._get_input_schema()

        return ModelReturn(
            data_schema=DataSchema(
                input_features=input_features,
                output_features=output_features,
                data_type=self.interface.data_type,
            )
        )

    @staticmethod
    def validate(to_onnx: bool) -> bool:
        if not to_onnx:
            return True
        return False
