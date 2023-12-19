# pylint: disable=no-member,broad-exception-caught
# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import textwrap
from typing import Any, Dict

from opsml.helpers.logging import ArtifactLogger
from opsml.helpers.utils import get_class_name
from opsml.registry.cards.model import ModelCard
from opsml.registry.model.utils.data_helper import get_model_data
from opsml.registry.model.utils.model_predict_helper import PredictHelper
from opsml.registry.types import (
    ApiDataSchemas,
    DataDict,
    Feature,
    ModelReturn,
    TrainedModelType,
)
from opsml.registry.types.data import AllowedDataType

logger = ArtifactLogger.get_logger()


class ModelCreator:
    def __init__(self, modelcard: ModelCard):
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
        self.card = modelcard

    @property
    def model(self) -> Any:
        """Return model from modelcard"""
        if self.card.model.model_class == TrainedModelType.PYTORCH_LIGHTNING:
            return self.card.model.model
        return self.card.model

    def create_model(self) -> ModelReturn:
        raise NotImplementedError

    @staticmethod
    def validate(to_onnx: bool) -> bool:
        raise NotImplementedError


class TrainedModelMetadataCreator(ModelCreator):
    """Creates metadata to deploy a trained model"""

    def _get_input_schema(self) -> Dict[str, Feature]:
        model_data = get_model_data(
            data_type=self.card.model.data_type,
            input_data=self.card.model.sample_data,
        )

        return model_data.feature_dict

    def _get_output_schema(self) -> Dict[str, Feature]:
        try:
            sample_prediction = self.card.model.get_sample_prediction()
            processed_prediction = PredictHelper.process_model_prediction(model=self.card.model)

            output_data = get_model_data(
                input_data=processed_prediction,
                data_type=sample_prediction.prediction_type,
            )

            # pandas will use column names as features
            if self.card.model.data_type != AllowedDataType.PANDAS:
                output_data.features = ["outputs"]
                print(output_data.feature_dict)

            print(output_data.feature_dict)
            print()
            return output_data.feature_dict

        except Exception as error:
            logger.error("Failed to determine prediction output. Defaulting to placeholder. {}", error)

        return {"placeholder": Feature(feature_type="str", shape=[1])}

    def create_model(self) -> ModelReturn:
        # make predictions first in case of column type switching for input cols
        output_features = self._get_output_schema()

        # this will convert categorical to string
        input_features = self._get_input_schema()

        print(input_features)
        print()
        print(output_features)
        a

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
            onnx_args:
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
        if self.card.model.model_type in [
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
        from opsml.registry.model.model_converters import OnnxModelConverter

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
