from typing import Any, Dict, List, Union, cast

from numpy.typing import NDArray

from opsml.helpers.logging import ArtifactLogger
from opsml.helpers.utils import get_class_name
from opsml.model.utils.types import TrainedModelType, ValidModelInput
from opsml.registry.data.types import AllowedDataType
from opsml.registry.cards.supported_models import HuggingFaceModel, PytorchModel, LightningModel, SamplePrediction
from opsml.model.utils.huggingface_types import GENERATION_TYPES

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
    def _get_pipeline_prediction(self, model: HuggingFaceModel) -> List[Dict[str, Any]]:
        pred = model.get_sample_prediction()

        if isinstance(pred.prediction, dict):
            return [pred.prediction]

        return cast(List[Dict[str, Any]], pred.prediction)

    def _process_tensor(self, pred: SamplePrediction) -> NDArray[Any]:
        """Processes huggingface model that outputs a torch or tensorflow tensor

        Args:
            pred:
                SamplePrediction
        Returns:
            Numpy array of predictions
        """
        if pred.prediction_type == AllowedDataType.TORCH_TENSOR:
            return pred.prediction.detach().numpy()

        return pred.prediction.numpy()

    def _process_modeloutput(self, pred: SamplePrediction) -> Dict[str, Any]:
        """Processes huggingface model that outputs a class of type `ModelOuput`

        Args:
            pred:
                SamplePrediction
        Returns:
            Dictionary of predictions
        """
        predictions = {}
        for key, value in pred.prediction.items():
            pred_class = get_class_name(value)

            if pred_class == AllowedDataType.TORCH_TENSOR:
                predictions[key] = value.detach().numpy()
            elif pred_class == AllowedDataType.TENSORFLOW_TENSOR:
                predictions[key] = value.numpy()
            else:
                predictions[key] = value

        return predictions

    def _process_hidden_state(self, pred: SamplePrediction) -> NDArray[Any]:
        """Processes huggingface model that outputs a hidden state

        Args:
            pred:
                SamplePrediction
        Returns:
            Numpy array of predictions
        """
        for method in pred.prediction.__dir__():
            if "last_hidden_state" in method:
                hidden_state = getattr(pred.prediction, method)
                pred_class = get_class_name(hidden_state)

                if pred_class == AllowedDataType.TORCH_TENSOR:
                    return hidden_state.detach().numpy()
                return hidden_state.numpy()

    def _get_prediction(self, model: HuggingFaceModel):
        from transformers.utils import ModelOutput

        try:
            pred = model.get_sample_prediction()

            if pred.prediction_type in [
                AllowedDataType.TORCH_TENSOR,
                AllowedDataType.TENSORFLOW_TENSOR,
            ]:
                predictions = self._process_tensor(pred)

            # check for different output types

            elif isinstance(pred.prediction, ModelOutput):
                predictions = self._process_modeloutput

            else:
                for method in pred.prediction.__dir__():
                    if "last_hidden_state" in method:
                        hidden_state = getattr(predictions, method)
                        pred_class = get_class_name(hidden_state)

                        if pred_class == AllowedDataType.TORCH_TENSOR:
                            predictions = hidden_state.detach().numpy()
                        else:
                            predictions = hidden_state.numpy()
                        break

            return predictions

        except Exception as error:
            logger.error("Failed to determine prediction output. Defaulting to placeholder. {}", error)
            raise error

    def get_prediction(self, model: HuggingFaceModel) -> Union[List[Dict[str, Any]], NDArray[Any]]:
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

        if self.model.is_pipeline:
            return self._get_pipeline_prediction(model)

        else:
            pass

        if self.model.task_type in GENERATION_TYPES:
            return self._generate_prediction(model)

        if "Pipeline" in self.model_type:
            return self._get_pipeline_prediction(model)

        predictions = self._generate_prediction(model)
        if predictions is not None:
            return predictions

        return self._functional_prediction(model)

    @staticmethod
    def validate(model_class: str) -> bool:
        return model_class == TrainedModelType.TRANSFORMERS
