# pylint: disable=no-member,broad-exception-caught
# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import textwrap
from typing import Any, Dict, Optional

import numpy as np

from opsml.helpers.logging import ArtifactLogger
from opsml.model.data_helper import get_model_data
from opsml.model.types import (
    ApiDataSchemas,
    DataDict,
    Feature,
    ModelCard,
    ModelReturn,
    TrainedModelType,
)
from opsml.registry.data.types import AllowedDataType, get_class_name

logger = ArtifactLogger.get_logger()


class ModelCreator:
    def __init__(self, modelcard: ModelCard):
        """
        Args:
            Model:
                Model to convert (BaseEstimator, Pipeline, StackingRegressor, Booster)
            input_data:
                Sample of data used to train model (pd.DataFrame, np.ndarray, dict of np.ndarray)
            additional_onnx_args:
                Specific args for Pytorch onnx conversion. The won't be passed for most models
            onnx_model_def:
                Optional `OnnxModelDefinition`
        """
        self.card = modelcard

    @property
    def model(self) -> Any:
        """Return model from modelcard"""
        if self.card.metadata.model_class == TrainedModelType.PYTORCH_LIGHTNING:
            return self.card.trained_model.model
        return self.card.trained_model

    def create_model(self) -> ModelReturn:
        raise NotImplementedError

    @staticmethod
    def validate(to_onnx: bool) -> bool:
        raise NotImplementedError


class TrainedModelMetadataCreator(ModelCreator):
    """Creates metadata to deploy a trained model"""

    def _get_input_schema(self) -> Dict[str, Feature]:
        model_data = get_model_data(
            data_type=self.card.metadata.sample_data_type,
            input_data=self.card.sample_input_data,
        )

        return model_data.feature_dict

    def _get_prediction_type(self, predictions: Any) -> Dict[str, Feature]:
        model_data = get_model_data(
            input_data=predictions,
            data_type=get_class_name(predictions),
        )

        # pandas will use column names as features
        if self.card.metadata.sample_data_type != AllowedDataType.PANDAS:
            model_data.features = ["outputs"]

        return model_data.feature_dict

    def _predict_prediction(self) -> Dict[str, Feature]:
        """Test default predict method leveraged by most ml libraries"""
        predictions = self.card.trained_model.predict(self.card.sample_input_data)
        return self._get_prediction_type(predictions=predictions)

    def _torch_prediction(self) -> Dict[str, Feature]:  # pragma: no cover
        """Tests generate method commonly used with huggingface models.
        If generate fails, prediction will fall back to normal functional call.
        """

        try:
            if self.card.metadata.sample_data_type in [AllowedDataType.DICT, AllowedDataType.TRANSFORMER_BATCH]:
                predictions = self.model(**self.card.sample_input_data)
            else:
                predictions = self.model(self.card.sample_input_data)

            return self._get_prediction_type(predictions=predictions.detach().numpy())

        except TypeError as error:
            logger.error("{}. Falling back to model functional call", error)
            raise error

    def _generate_prediction(self) -> Optional[Dict[str, Feature]]:  # pragma: no cover
        """Test generate method commonly used with huggingface models"""

        try:
            if self.card.metadata.sample_data_type in [AllowedDataType.DICT, AllowedDataType.TRANSFORMER_BATCH]:
                predictions = self.model.generate(**self.card.sample_input_data)
            else:
                predictions = self.model.generate(self.card.sample_input_data)

            return self._get_prediction_type(predictions=predictions.detach().numpy())

        except Exception:
            return None

    def _transformers_prediction(self) -> Dict[str, Feature]:  # pragma: no cover
        """Get predictions for huggingface transformers models"""
        predictions = self._generate_prediction()

        if predictions is not None:
            return predictions

        return self._functional_prediction()

    def _functional_prediction(self) -> Dict[str, Feature]:
        import torch

        try:
            if self.card.metadata.sample_data_type in [AllowedDataType.DICT, AllowedDataType.TRANSFORMER_BATCH]:
                predictions = self.model(**self.card.sample_input_data)
            else:
                predictions = self.model(self.card.sample_input_data)

            if isinstance(predictions, torch.Tensor):
                predictions = predictions.detach.numpy()

            else:
                for method in self.model.__dir__():
                    if "last_hidden_state" in method:
                        predictions = getattr(predictions, method).detach().numpy()

            return self._get_prediction_type(predictions=predictions)

        except Exception as error:
            logger.error("Failed to determine prediction output. Defaulting to placeholder. {}", error)
            raise error

        # try functional call

    def _get_output_schema(self) -> Dict[str, Feature]:
        try:
            if hasattr(self.card.trained_model, "predict"):
                return self._predict_prediction()

            if (
                self.card.metadata.model_class == TrainedModelType.PYTORCH
                or self.card.metadata.model_class == TrainedModelType.PYTORCH_LIGHTNING
            ):
                return self._torch_prediction()

            if self.card.metadata.model_class == TrainedModelType.TRANSFORMERS:
                return self._transformers_prediction()

        except Exception as error:
            logger.error("Failed to determine prediction output. Defaulting to placeholder. {}", error)

        return {"placeholder": Feature(feature_type="str", shape=[1])}

    def create_model(self) -> ModelReturn:
        # make predictions first in case of column type switching for input cols
        output_features = self._get_output_schema()

        # this will convert categorical to string
        input_features = self._get_input_schema()

        api_schema = ApiDataSchemas(
            model_data_schema=DataDict(
                input_features=input_features,
                output_features=output_features,
                data_type=self.card.metadata.sample_data_type,
            )
        )

        return ModelReturn(
            api_data_schema=api_schema,
            model_type=self.card.metadata.model_type,
        )

    @staticmethod
    def validate(to_onnx: bool) -> bool:
        if not to_onnx:
            return True
        return False


class OnnxModelCreator(ModelCreator):
    def __init__(self, modelcard: ModelCard):
        """
        Instantiates OnnxModelCreator that is used for converting models to Onnx

        Args:
            Model:
                Model to convert (BaseEstimator, Pipeline, StackingRegressor, Booster)
            input_data:
                Sample of data used to train model (pd.DataFrame, np.ndarray, dict of np.ndarray)
            additional_onnx_args:
                Specific args for Pytorch onnx conversion. The won't be passed for most models
            onnx_model_def:
                Optional `OnnxModelDefinition`
        """

        super().__init__(modelcard=modelcard)
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
        if self.card.metadata.model_type in [
            TrainedModelType.SKLEARN_PIPELINE,
            TrainedModelType.TF_KERAS,
            TrainedModelType.PYTORCH,
        ]:
            return AllowedDataType(self.card.metadata.sample_data_type).value

        return AllowedDataType.NUMPY.value

    def create_model(self) -> ModelReturn:
        """
        Create model card from current model and sample data

        Returns
            `ModelReturn`
        """
        from opsml.model.model_converters import OnnxModelConverter

        try:
            model_data = get_model_data(
                data_type=self.card.metadata.sample_data_type,
                input_data=self.card.sample_input_data,
            )

            onnx_model_return = OnnxModelConverter.convert_model(
                modelcard=self.card,
                data_helper=model_data,
            )
            onnx_model_return.model_type = self.card.metadata.model_type
            onnx_model_return.api_data_schema.model_data_schema.data_type = self.onnx_data_type

            # add onnx version
            return onnx_model_return
        except Exception as exc:
            logger.error("Failed to convert model to onnx. {}", exc)
            raise ValueError(
                textwrap.dedent(
                    f"""
               Failed to convert model to onnx format. If you'd like to turn onnx conversion off
               set to_onnx=False in the ModelCard. If you wish to provide your own onnx definition,
               please refer to https://github.com/shipt/opsml/blob/main/docs/docs/cards/onnx.md.
               Error: {exc}
               """
                )
            ) from exc

    #
    @staticmethod
    def validate(to_onnx: bool) -> bool:
        if to_onnx:
            return True
        return False


def create_model(modelcard: ModelCard) -> ModelReturn:
    """
    Validates and selects s `ModeCreator` subclass and creates a `ModelReturn`

    Args:
        modelcard:
            ModelCard

    Returns:
        `ModelReturn`
    """

    creator = next(creator for creator in ModelCreator.__subclasses__() if creator.validate(to_onnx=modelcard.to_onnx))

    return creator(modelcard=modelcard).create_model()
