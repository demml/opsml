from typing import Any, Dict, List, Union, cast

from numpy.typing import NDArray

from opsml.helpers.logging import ArtifactLogger
from opsml.registry.data.types import AllowedDataType
from opsml.registry.cards.supported_models import (
    HuggingFaceModel,
    PytorchModel,
    LightningModel,
    SamplePrediction,
    SklearnModel,
    LightGBMBoosterModel,
    XGBoostModel,
    TensorflowModel,
)

logger = ArtifactLogger.get_logger()


class PredictHelper:
    def process_prediction(self, model: Any) -> Any:
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

        raise NotImplementedError

    @staticmethod
    def validate(model: Any) -> bool:
        raise NotImplementedError

    @staticmethod
    def process_model_prediction(model: Any) -> Any:
        """Get model predictions for a given model"""
        predict_helper = next(
            (helper for helper in PredictHelper.__subclasses__() if helper.validate(model)),
            ClassicPredictHelper,
        )

        return predict_helper().process_prediction(model)


class ClassicPredictHelper(PredictHelper):
    """Predict helper used for models that implement `predict` method"""

    def process_prediction(
        self,
        model: Union[TensorflowModel, XGBoostModel, LightGBMBoosterModel, SklearnModel],
    ) -> SamplePrediction:
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

        return model.get_sample_prediction()

    @staticmethod
    def validate(model: Union[TensorflowModel, XGBoostModel, LightGBMBoosterModel, SklearnModel]) -> bool:
        return isinstance(model, (TensorflowModel, XGBoostModel, LightGBMBoosterModel, SklearnModel))


class TorchPredictHelper(PredictHelper):
    def process_prediction(self, model: PytorchModel) -> NDArray[Any]:
        return model.get_sample_prediction()

    @staticmethod
    def validate(model: Union[PytorchModel, LightningModel]) -> bool:
        return isinstance(model, (PytorchModel, LightningModel))


class HuggingFacePredictHelper(PredictHelper):
    def _process_pipeline_prediction(self, model: HuggingFaceModel) -> List[Dict[str, Any]]:
        pred = model.get_sample_prediction()

        if isinstance(pred.prediction, dict):
            return [pred.prediction]

        return cast(List[Dict[str, Any]], pred.prediction)

    def _process_modeloutput(self, pred: SamplePrediction) -> Dict[str, Any]:
        """Processes huggingface model that outputs a class of type `ModelOutput`

        Args:
            pred:
                SamplePrediction
        Returns:
            Dictionary of predictions
        """

        # convert to dict
        predictions = {}
        for key, value in pred.prediction.items():
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
                return getattr(pred.prediction, method)

    def _process_prediction(self, model: HuggingFaceModel):
        from transformers.utils import ModelOutput

        try:
            pred = model.get_sample_prediction()

            if pred.prediction_type in [
                AllowedDataType.TORCH_TENSOR,
                AllowedDataType.TENSORFLOW_TENSOR,
            ]:
                predictions = pred

            # check for different output types
            elif isinstance(pred.prediction, ModelOutput):
                predictions = self._process_modeloutput(pred)

            else:
                predictions = self._process_hidden_state(pred)

            return predictions

        except Exception as error:
            logger.error("Failed to coerce huggingface model outputs. {}", error)
            raise error

    def process_prediction(self, model: HuggingFaceModel) -> Union[List[Dict[str, Any]], NDArray[Any]]:
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

        if model.is_pipeline:
            return self._process_pipeline_prediction(model)

        return self._process_prediction(model)

    @staticmethod
    def validate(model: HuggingFaceModel) -> bool:
        return isinstance(model, HuggingFaceModel)
