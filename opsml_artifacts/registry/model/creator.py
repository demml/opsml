from typing import Any, Union

import numpy as np
import pandas as pd

from opsml_artifacts.registry.model.model_converters import OnnxModelConverter
from opsml_artifacts.registry.model.model_types import ModelType, OnnxModelType
from opsml_artifacts.registry.model.types import InputDataType, OnnxModelReturn


class OnnxModelCreator:
    def __init__(
        self,
        model: Any,
        input_data: Union[pd.DataFrame, np.ndarray],
    ):

        """Instantiates OnnxModelCreator that is used for converting models to Onnx

        Args:
            Model (BaseEstimator, Pipeline, StackingRegressor, Booster): Model to convert
            input_data (pd.DataFrame, np.ndarray): Sample of data used to train model
        """
        self.model = model
        self.input_data = input_data
        self.model_class = self._get_model_class_name()
        self.model_type = self.get_onnx_model_type()
        self.data_type = self.get_input_data_type(input_data=input_data)

    def get_input_data_type(self, input_data: Union[pd.DataFrame, np.ndarray]) -> str:

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
        if self.model_type == OnnxModelType.SKLEARN_PIPELINE:
            return InputDataType(type(input_data)).name

        return InputDataType.NUMPY_ARRAY.name

    def _get_model_class_name(self):
        if "keras.engine" in self.model.__str__():
            return "keras"
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
        model_definition, feature_dict, data_schema = OnnxModelConverter(
            model=self.model,
            input_data=self.input_data,
            model_type=self.model_type,
        ).convert_model()

        return OnnxModelReturn(
            model_definition=model_definition,
            feature_dict=feature_dict,
            data_schema=data_schema,
            model_type=self.model_type,
            data_type=self.data_type,
        )

        # return ModelCard(
        #   name=model_name.lower(),
        #   team=team.lower(),
        #   model_type=self.model_type,
        #   data_schema=data_schema,
        #   user_email=user_email.lower(),
        #   onnx_model_def=model_definition,
        #   data_card_uid=registered_data_uid,
        #   onnx_model_data=DataDict(
        #       data_type=self.data_type,
        #       features=feature_dict,
        #   ),


#
