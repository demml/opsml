# pylint: disable=no-member,broad-exception-caught
# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import Any, Dict, Optional
import textwrap
import numpy as np
from opsml.helpers.logging import ArtifactLogger
from opsml.model.model_converters import OnnxModelConverter
from opsml.model.model_info import ModelInfo, get_model_data
from opsml.model.model_types import ModelType, OnnxModelType
from opsml.model.types import (
    ApiDataSchemas,
    DataDict,
    ExtraOnnxArgs,
    Feature,
    InputData,
    InputDataType,
    ModelReturn,
    OnnxModelDefinition,
)

logger = ArtifactLogger.get_logger()


class ModelCreator:
    def __init__(
        self,
        model: Any,
        input_data: InputData,
        additional_onnx_args: Optional[ExtraOnnxArgs] = None,
        onnx_model_def: Optional[OnnxModelDefinition] = None,
    ):
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
        self.model = model
        self.input_data = input_data
        self.model_class = self._get_model_class_name()
        self.additional_model_args = additional_onnx_args
        self.onnx_model_def = onnx_model_def
        self.input_data_type = type(self.input_data)
        self.model_type = self.get_model_type()

    def _get_model_class_name(self):
        """Gets class name from model"""

        if "keras.engine" in str(self.model):
            return OnnxModelType.TF_KERAS.value

        if "torch" in str(self.model.__class__.__bases__):
            return OnnxModelType.PYTORCH.value

        # for transformer models from huggingface
        if "transformers.models" in str(self.model.__class__.__bases__):
            return OnnxModelType.TRANSFORMER.value

        return self.model.__class__.__name__

    def get_model_type(self) -> str:
        model_type = next(
            (
                model_type
                for model_type in ModelType.__subclasses__()
                if model_type.validate(model_class_name=self.model_class)
            )
        )
        return model_type.get_type()

    def create_model(self) -> ModelReturn:
        raise NotImplementedError

    @staticmethod
    def validate(to_onnx: bool) -> bool:
        raise NotImplementedError


class TrainedModelMetadataCreator(ModelCreator):
    """Creates metadata to deploy a trained model"""

    def _get_input_schema(self) -> Dict[str, Feature]:
        model_data = get_model_data(
            data_type=self.input_data_type,
            input_data=self.input_data,
        )

        return model_data.feature_dict

    def _get_prediction_type(self, predictions: Any) -> Dict[str, Feature]:
        model_data = get_model_data(
            input_data=predictions,
            data_type=type(predictions),
        )

        model_data.features = ["outputs"]

        return model_data.feature_dict

    def _predict_prediction(self) -> Dict[str, Feature]:
        """Test default predict method leveraged by most ml libraries"""
        predictions = self.model.predict(self.input_data)
        return self._get_prediction_type(predictions=predictions)

    def _generate_prediction(self) -> Dict[str, Feature]:
        """Tests generate method commonly used with huggingface models.
        If generate fails, prediction will fall back to normal functional call.
        """
        import torch

        try:
            if isinstance(self.input_data, np.ndarray):
                array_input = torch.from_numpy(self.input_data)
                predictions = self.model.generate(array_input)

            elif isinstance(self.input_data, dict):
                dict_input: Dict[str, torch.Tensor] = {
                    key: torch.from_numpy(val) for key, val in self.input_data.items()
                }
                predictions = self.model.generate(**dict_input)

            if isinstance(predictions, torch.Tensor):
                predictions = predictions.numpy()

            return self._get_prediction_type(predictions=predictions)

        except TypeError as error:
            logger.error("{}. Falling back to model functional call", error)

        return self._functional_prediction()

    def _functional_prediction(self) -> Dict[str, Feature]:
        """Calls the model directly using functional call"""
        import torch

        if isinstance(self.input_data, np.ndarray):
            array_input = torch.from_numpy(self.input_data)
            predictions = self.model(array_input)

        elif isinstance(self.input_data, dict):
            dict_input: Dict[str, torch.Tensor] = {key: torch.from_numpy(val) for key, val in self.input_data.items()}
            predictions = self.model(**dict_input)

        if isinstance(predictions, torch.Tensor):
            predictions = predictions.numpy()

        # assumes model predictions can be retrieved via hidden state
        else:
            predictions = predictions.last_hidden_state.detach().numpy()

        return self._get_prediction_type(predictions=predictions)

    def _get_output_schema(self) -> Dict[str, Feature]:
        try:
            if hasattr(self.model, "predict"):
                return self._predict_prediction()

            # huggingface/pytorch
            # Majority of huggingface models have generate method but may raise error
            if hasattr(self.model, "generate"):
                return self._generate_prediction()

            return self._functional_prediction()

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
                data_type=InputDataType(type(self.input_data)).name,
            )
        )

        return ModelReturn(api_data_schema=api_schema, model_type=self.model_type)

    @staticmethod
    def validate(to_onnx: bool) -> bool:
        if not to_onnx:
            return True
        return False


class OnnxModelCreator(ModelCreator):
    def __init__(
        self,
        model: Any,
        input_data: InputData,
        additional_onnx_args: Optional[ExtraOnnxArgs] = None,
        onnx_model_def: Optional[OnnxModelDefinition] = None,
    ):
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

        super().__init__(
            model=model,
            input_data=input_data,
            additional_onnx_args=additional_onnx_args,
            onnx_model_def=onnx_model_def,
        )
        self.onnx_data_type = self.get_onnx_data_type(input_data=input_data)

    def get_onnx_data_type(self, input_data: Any) -> str:
        """
        Gets the current data type base on model type.
        Currently only sklearn pipeline supports pandas dataframes.
        All others support numpy arrays. This is needed for API signature
        creation when loading model predictors.

        Args:
            input_data:
                Sample of data used to train model

        Returns:
            data type
        """

        # Onnx supports dataframe schemas for pipelines
        # re-work this
        if self.model_type in [
            OnnxModelType.SKLEARN_PIPELINE,
            OnnxModelType.TF_KERAS,
            OnnxModelType.PYTORCH,
        ]:
            return InputDataType(type(input_data)).name

        return InputDataType.NUMPY_ARRAY.name

    def create_model(self) -> ModelReturn:
        """
        Create model card from current model and sample data

        Returns
            `ModelReturn`
        """

        try:
            model_data = get_model_data(
                data_type=self.input_data_type,
                input_data=self.input_data,
            )
            model_info = ModelInfo(
                model=self.model,
                model_data=model_data,
                model_type=self.model_type,
                model_class=self.model_class,
                data_type=self.input_data_type,
                additional_model_args=self.additional_model_args,
                onnx_model_def=self.onnx_model_def,
            )

            onnx_model_return = OnnxModelConverter(model_info=model_info).convert_model()
            onnx_model_return.model_type = self.model_type
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

    @staticmethod
    def validate(to_onnx: bool) -> bool:
        if to_onnx:
            return True
        return False


def create_model(
    model: Any,
    input_data: InputData,
    to_onnx: bool,
    additional_onnx_args: Optional[ExtraOnnxArgs] = None,
    onnx_model_def: Optional[OnnxModelDefinition] = None,
) -> ModelReturn:
    """
    Validates and selects s `ModeCreator` subclass and creates a `ModelReturn`

    Args:
            model:
                Model to convert (BaseEstimator, Pipeline, StackingRegressor, Booster)
            input_data:
                Sample of data used to train model (pd.DataFrame, np.ndarray, dict of np.ndarray)
            additional_onnx_args:
                Specific args for Pytorch onnx conversion. The won't be passed for most models
            to_onnx:
                Whether to use Onnx creator or not
            onnx_model_def:
                Optional onnx model def. This is primarily used for bring your own onnx models

    Returns:
        `ModelReturn`
    """

    creator = next(
        creator
        for creator in ModelCreator.__subclasses__()
        if creator.validate(
            to_onnx=to_onnx,
        )
    )

    return creator(
        model=model,
        input_data=input_data,
        additional_onnx_args=additional_onnx_args,
        onnx_model_def=onnx_model_def,
    ).create_model()
