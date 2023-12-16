from typing import Any, Dict, List, Union, cast

from numpy.typing import NDArray

from opsml.helpers.logging import ArtifactLogger
from opsml.model.utils.types import TrainedModelType, ValidModelInput
from opsml.registry.data.types import AllowedDataType
from opsml.registry.cards.supported_models import HuggingFaceModel, PytorchModel, LightningModel

logger = ArtifactLogger.get_logger()


class PredictHelper:
    def __init__(self, sample_data_type: str, model_type: str):
        """Instantiates predictor helper class for getting model predictions."""
        self.data_type = sample_data_type
        self.model_type = model_type

    def get_prediction(self, model: Any, inputs: ValidModelInput) -> Any:
        """
        Generate predictions from model
        Args:
            model:
                Trained model
            inputs:
                Dictionary of inputs
        Returns:
            Predictions
        """

        return model.predict(inputs)

    @staticmethod
    def validate(model_class: str) -> bool:
        return model_class not in [
            TrainedModelType.PYTORCH,
            TrainedModelType.PYTORCH_LIGHTNING,
            TrainedModelType.TRANSFORMERS,
        ]

    @staticmethod
    def get_model_prediction(
        model: Any,
        inputs: ValidModelInput,
        sample_data_type: str,
        model_class: str,
        model_type: str,
    ) -> Any:
        """Get model predictions for a given model"""
        predict_helper = next(
            (
                helper
                for helper in PredictHelper.__subclasses__()
                if helper.validate(
                    model_class,
                )
            ),
            PredictHelper,
        )

        return predict_helper(
            sample_data_type,
            model_type,
        ).get_prediction(model, inputs)


class TorchPredictHelper(PredictHelper):
    def get_prediction(self, model: PytorchModel) -> NDArray[Any]:
        import torch

        try:
            predictions = model.get_sample_prediction()

            if isinstance(predictions, dict):
                return {key: value.detach().numpy() for key, value in predictions.items()}

            if isinstance(predictions, tuple):
                for value in predictions:
                    if isinstance(value, torch.Tensor):
                        return value.detach().numpy()

            return predictions.detach().numpy()

        except TypeError as error:
            logger.error("{}. Falling back to model functional call", error)
            raise error

    @staticmethod
    def validate(model_class: str) -> bool:
        return model_class == TrainedModelType.PYTORCH or model_class == TrainedModelType.PYTORCH_LIGHTNING


class HuggingFacePredictHelper(PredictHelper):
    def _generate_prediction(self, model: HuggingFaceModel) -> NDArray[Any]:
        # cant use getattr
        # most models have a generate method even if they don't support it
        try:
            if self.data_type in [AllowedDataType.DICT, AllowedDataType.TRANSFORMER_BATCH]:
                predictions = model.generate(**model.sample_data)
            else:
                predictions = model.generate(model.sample_data)

            return predictions.detach().numpy()

        except Exception:
            return None

    def _functional_prediction(self, model: HuggingFaceModel) -> NDArray[Any]:
        import torch

        try:
            if self.data_type in [AllowedDataType.DICT, AllowedDataType.TRANSFORMER_BATCH]:
                predictions = model(**model.sample_data)
            else:
                predictions = model(model.sample_data)

            if isinstance(predictions, torch.Tensor):
                predictions = predictions.detach.numpy()

            else:
                for method in predictions.__dir__():
                    if "last_hidden_state" in method:
                        predictions = getattr(predictions, method).detach().numpy()
                        break

            return predictions

        except Exception as error:
            logger.error("Failed to determine prediction output. Defaulting to placeholder. {}", error)
            raise error

    def _get_pipeline_prediction(self, model: HuggingFaceModel) -> List[Dict[str, Any]]:
        predictions = model.model(model.sample_data)
        return cast(List[Dict[str, Any]], predictions)

    def get_prediction(self, model: Any, inputs: ValidModelInput) -> Union[List[Dict[str, Any]], NDArray[Any]]:
        """
        Get prediction from model
        Args:
            model:
                Trained model
            inputs:
                Dictionary of inputs
            sample_data_type:
                Type of sample data
        Returns:
            Dictionary of predictions
        """

        if "Pipeline" in self.model_type:
            return self._get_pipeline_prediction(model, inputs)

        predictions = self._generate_prediction(model, inputs)
        if predictions is not None:
            return predictions

        return self._functional_prediction(model, inputs)

    @staticmethod
    def validate(model_class: str) -> bool:
        return model_class == TrainedModelType.TRANSFORMERS
