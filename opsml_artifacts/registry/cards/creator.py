from typing import Optional, Union

from sklearn.base import BaseEstimator
from sklearn.ensemble import StackingRegressor
from sklearn.pipeline import Pipeline
import pandas as pd
import numpy as np

from opsml_artifacts.registry.model.model_converters import OnnxModelConverter
from opsml_artifacts.registry.model.model_types import ModelType, OnnxModelType
from opsml_artifacts.registry.model.types import DataDict, InputDataType
from opsml_artifacts.registry.cards.card import ModelCard


class ModelCardCreator:
    def __init__(
        self,
        model: Union[BaseEstimator, Pipeline, StackingRegressor],
        input_data: Union[pd.DataFrame, np.ndarray],
    ):

        """Instantiates ModelCardCreator that is used for converting models to Onnx and creating model cards

        Args:
            Model (BaseEstimator, Pipeline, StackingRegressor): Model to convert
            input_data (pd.DataFrame, np.ndarray): Sample of data used to train model
        """
        self.model = model
        self.input_data = input_data
        self.model_type = self.get_onnx_model_type()
        self.data_type = self.get_data_type(input_data=input_data)

    def get_data_type(self, input_data: Union[pd.DataFrame, np.ndarray]) -> str:

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

    def get_onnx_model_type(self) -> str:
        model_class_name = self.model.__class__.__name__
        model_type = next(
            (
                model_type
                for model_type in ModelType.__subclasses__()
                if model_type.validate(model_class_name=model_class_name)
            )
        )

        return model_type.get_type()

    def create_model_card(
        self,
        model_name: str,
        team: str,
        user_email: str,
        registered_data_uid: Optional[str] = None,
    ) -> ModelCard:
        """Create model card from current model and sample data

        Args:
            model_name (str): What to name the model
            team (str): Team name
            user_email (str): Email to associate with the model
            registered_data_uid (str): Uid associated with registered data card.
            A ModelCard can be created, but not registered without a DataCard uid.
        Returns
            ModelCard

        """
        model_definition, feature_dict, data_schema = OnnxModelConverter(
            model=self.model,
            input_data=self.input_data,
            model_type=self.model_type,
        ).convert_model()

        return ModelCard(
            name=model_name.lower(),
            team=team.lower(),
            model_type=self.model_type,
            data_schema=data_schema,
            user_email=user_email.lower(),
            onnx_model_def=model_definition,
            data_card_uid=registered_data_uid,
            onnx_model_data=DataDict(
                data_type=self.data_type,
                features=feature_dict,
            ),
        )
