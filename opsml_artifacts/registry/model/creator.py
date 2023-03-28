from typing import Any, Dict, Optional, cast

import numpy as np

from opsml_artifacts.registry.model.model_converters import OnnxModelConverter
from opsml_artifacts.registry.model.model_types import ModelType, OnnxModelType
from opsml_artifacts.registry.model.types import (
    InputDataType,
    ModelData,
    ModelInfo,
    OnnxModelReturn,
    TorchOnnxArgs,
)


class OnnxModelCreator:
    def __init__(
        self,
        model: Any,
        input_data: ModelData,
        additional_onnx_args: Optional[TorchOnnxArgs] = None,
    ):

        """Instantiates OnnxModelCreator that is used for converting models to Onnx

        Args:
            Model (BaseEstimator, Pipeline, StackingRegressor, Booster): Model to convert
            input_data (pd.DataFrame, np.ndarray): Sample of data used to train model
        """
        self.model = model
        self.input_data = self._get_one_sample(input_data)
        self.model_class = self._get_model_class_name()
        self.model_type = self.get_onnx_model_type()
        self.onnx_data_type = self.get_input_data_type(input_data=input_data)
        self.additional_model_args = additional_onnx_args
        self.input_data_type = type(self.input_data)

    def _get_one_sample(self, input_data: ModelData) -> ModelData:

        """Parses input data and returns a single record to be used during ONNX conversion and validation"""

        if not isinstance(input_data, InputDataType.DICT.value):
            return input_data[0:1]

        sample_dict = cast(Dict[str, np.ndarray], {})
        for key in cast(Dict[str, np.ndarray], input_data).keys():
            sample_dict[key] = input_data[key][0:1]

        return sample_dict

    def get_input_data_type(self, input_data: ModelData) -> str:

        """Gets the current data type base on model type.
        Currently only sklearn pipeline supports pandas dataframes.
        All others support numpy arrays. This is needed for API signature
        creation when loading model predictors.

        Args:
            input_data (pd.DataFrame, np.ndarray): Sample of data used to train model

        Returns:
            data type (str)
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

    def get_onnx_model_type(self) -> str:

        model_type = next(
            (
                model_type
                for model_type in ModelType.__subclasses__()
                if model_type.validate(model_class_name=self.model_class)
            )
        )

        return model_type.get_type()

    def create_onnx_model(self) -> OnnxModelReturn:
        """Create model card from current model and sample data

        Returns
            OnnxModelReturn
        """

        model_info = ModelInfo(
            model=self.model,
            input_data=self.input_data,
            model_type=self.model_type,
            data_type=self.input_data_type,
            additional_model_args=self.additional_model_args,
        )
        # create ModelInfo class?
        onnx_model_return = OnnxModelConverter(model_info=model_info).convert_model()

        onnx_model_return.model_type = self.model_type
        onnx_model_return.data_type = self.onnx_data_type

        # add onnx version
        return onnx_model_return
