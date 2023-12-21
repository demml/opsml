# pylint: disable=no-member,broad-exception-caught
# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import Any, Dict

from opsml.helpers.logging import ArtifactLogger
from opsml.registry.model.interfaces import ModelInterface
from opsml.registry.model.utils.data_helper import get_model_data
from opsml.registry.types import DataDict, Feature, ModelReturn, TrainedModelType
from opsml.registry.types.data import AllowedDataType

logger = ArtifactLogger.get_logger()


class _ModelCreator:
    def __init__(self, model_interface: ModelInterface):
        """
        Args:
            Model:
                Model to convert (BaseEstimator, Pipeline, StackingRegressor, Booster)
            input_data:
                Sample of data used to train model (pd.DataFrame, np.ndarray, dict of np.ndarray)
            onnx_args:
                Specific args for Pytorch onnx conversion. The won't be passed for most models
            onnx_model_def:
                Optional `OnnxModelDefinition`
        """
        self.interface = model_interface

    @property
    def model(self) -> Any:
        """Return model from modelcard"""
        if self.interface.model.model_class == TrainedModelType.PYTORCH_LIGHTNING:
            return self.interface.model.model
        return self.interface.model

    def create_model(self) -> ModelReturn:
        raise NotImplementedError

    @staticmethod
    def validate(to_onnx: bool) -> bool:
        raise NotImplementedError


class _TrainedModelMetadataCreator(_ModelCreator):
    """Creates metadata to deploy a trained model"""

    def _get_input_schema(self) -> Dict[str, Feature]:
        model_data = get_model_data(
            data_type=self.interface.data_type,
            input_data=self.interface.sample_data,
        )

        return model_data.feature_dict

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

    def create_model(self) -> ModelReturn:
        output_features = self._get_output_schema()
        input_features = self._get_input_schema()

        return ModelReturn(
            data_schema=DataDict(
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


class _OnnxModelCreator(_ModelCreator):
    def __init__(self, model_interface: ModelInterface):
        """
        Instantiates OnnxModelCreator that is used for converting models to Onnx

        Args:
            Model:
                Model to convert (BaseEstimator, Pipeline, StackingRegressor, Booster)
            input_data:
                Sample of data used to train model (pd.DataFrame, np.ndarray, dict of np.ndarray)
            onnx_args:
                Specific args for Pytorch onnx conversion. The won't be passed for most models
            onnx_model_def:
                Optional `OnnxModelDefinition`
        """

        super().__init__(model_interface=model_interface)
        self.onnx_data_type = self.get_onnx_data_type()

    def get_onnx_data_type(self) -> str:
        """
        Gets the current data type base on model type.
        Currently only sklearn pipeline supports pandas dataframes.
        All others support numpy arrays. This is needed for API signature
        creation when loading model predictors.

        Returns:
            data type
        """

        # Onnx supports dataframe schemas for pipelines
        # re-work this
        if self.interface.model_class in [
            TrainedModelType.TF_KERAS,
            TrainedModelType.PYTORCH,
        ]:
            return AllowedDataType(self.interface.data_type).value

        if (
            self.interface.model_class == TrainedModelType.SKLEARN_ESTIMATOR
            and self.interface.model_type == TrainedModelType.SKLEARN_PIPELINE
        ):
            return AllowedDataType(self.interface.data_type).value

        return AllowedDataType.NUMPY.value

    def create_model(self) -> ModelReturn:
        """
        Create model card from current model and sample data

        Returns
            `ModelReturn`
        """
        from opsml.registry.model.model_converters import OnnxModelConverter

        model_data = get_model_data(
            data_type=self.interface.data_type,
            input_data=self.interface.sample_data,
        )
        onnx_model_return = OnnxModelConverter.convert_model(modelcard=self.interface, data_helper=model_data)
        onnx_model_return.model_type = self.interface.model_type
        onnx_model_return.api_data_schema.model_data_schema.data_type = self.onnx_data_type

        # add onnx version
        return onnx_model_return

    #
    @staticmethod
    def validate(to_onnx: bool) -> bool:
        if to_onnx:
            return True
        return False


def create_model(model_interface: ModelInterface, to_onnx: bool = False) -> ModelReturn:
    """
    Validates and selects s `ModeCreator` subclass and creates a `ModelReturn`

    Args:
        modelcard:
            ModelCard

    Returns:
        `ModelReturn`
    """

    creator = next(creator for creator in _ModelCreator.__subclasses__() if creator.validate(to_onnx=to_onnx))

    return creator(model_interface).create_model()
