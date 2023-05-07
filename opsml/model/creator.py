from typing import Any, Dict, Optional, cast

import numpy as np

from opsml.model.model_converters import OnnxModelConverter
from opsml.model.model_info import ModelInfo, get_model_data
from opsml.model.model_types import ModelType, OnnxModelType
from opsml.model.types import (
    ApiDataSchemas,
    DataDict,
    Feature,
    InputData,
    InputDataType,
    ModelReturn,
    TorchOnnxArgs,
)


class ModelCreator:
    def __init__(
        self,
        model: Any,
        input_data: InputData,
        additional_onnx_args: Optional[TorchOnnxArgs] = None,
    ):
        """
        Args:
            Model:
                Model to convert (BaseEstimator, Pipeline, StackingRegressor, Booster)
            input_data:
                Sample of data used to train model (pd.DataFrame, np.ndarray, dict of np.ndarray)
            additional_onnx_args:
                Specific args for Pytorch onnx conversion. The won't be passed for most models
        """
        self.model = model
        self.input_data = self._get_one_sample(input_data)
        self.model_class = self._get_model_class_name()
        self.additional_model_args = additional_onnx_args
        self.input_data_type = type(self.input_data)
        self.model_type = self.get_model_type()

    def _get_one_sample(self, input_data: InputData) -> InputData:  # fix the any types later
        """Parses input data and returns a single record to be used during ONNX conversion and validation"""

        if not isinstance(input_data, InputDataType.DICT.value):
            return input_data[0:1]

        sample_dict = cast(Dict[str, np.ndarray], {})
        for key in cast(Dict[str, np.ndarray], input_data).keys():
            sample_dict[key] = input_data[key][0:1]

        return sample_dict

    def _get_model_class_name(self):
        """Gets class name from model"""

        if "keras.engine" in str(self.model):
            return OnnxModelType.TF_KERAS.value

        if "torch" in str(self.model.__class__.__bases__):
            return OnnxModelType.PYTORCH.value

        # for transformer models from huggingface
        if "transformers.models" in str(self.model.__class__.__bases__):
            return OnnxModelType.PYTORCH.value

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

        return model_data.feaure_dict

    def _get_prediction_type(self, predictions: Any) -> Dict[str, Feature]:
        model_data = get_model_data(
            input_data=predictions,
            data_type=type(predictions),
        )

        return model_data.feaure_dict

    def _get_output_schema(self) -> Dict[str, Feature]:
        if hasattr(self.model, "predict"):
            predictions = self.model.predict(self.input_data)
            return self._get_prediction_type(predictions=predictions)

    def create_model(self) -> ModelReturn:
        input_features = self._get_input_schema()
        output_features = self._get_output_schema()

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
        additional_onnx_args: Optional[TorchOnnxArgs] = None,
    ):
        """
        Instantiates OnnxModelCreator that is used for converting models to Onnx

        Args:
            Model:
                Model to convert (BaseEstimator, Pipeline, StackingRegressor, Booster)
            input_data:
                Sample of data used to train model (pd.DataFrame, np.ndarray, dict of np.ndarray)
        """

        super().__init__(
            model=model,
            input_data=input_data,
            additional_onnx_args=additional_onnx_args,
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

        model_data = get_model_data(
            data_type=self.input_data_type,
            input_data=self.input_data,
        )
        model_info = ModelInfo(
            model=self.model,
            model_data=model_data,
            model_type=self.model_type,
            data_type=self.input_data_type,
            additional_model_args=self.additional_model_args,
        )

        onnx_model_return = OnnxModelConverter(model_info=model_info).convert_model()
        onnx_model_return.model_type = self.model_type
        onnx_model_return.api_data_schema.model_data_schema.data_type = self.onnx_data_type

        # add onnx version
        return onnx_model_return

    @staticmethod
    def validate(to_onnx: bool) -> bool:
        if to_onnx:
            return True
        return False


def create_model(
    model: Any,
    input_data: InputData,
    to_onnx: bool,
    additional_onnx_args: Optional[TorchOnnxArgs] = None,
) -> ModelReturn:
    """
    Validates and selects s `ModeCreator` subclass and creates a `ModelReturn`

    Args:
            Model:
                Model to convert (BaseEstimator, Pipeline, StackingRegressor, Booster)
            input_data:
                Sample of data used to train model (pd.DataFrame, np.ndarray, dict of np.ndarray)
            additional_onnx_args:
                Specific args for Pytorch onnx conversion. The won't be passed for most models
            to_onnx:
                Whether to use Onnx creator or not

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
    ).create_model()
