from typing import Any, Dict, Optional

from pydantic import model_validator

from opsml.helpers.utils import get_class_name
from opsml.registry.model.interfaces.base import SamplePrediction, get_model_args
from opsml.registry.model.interfaces.pytorch import PyTorchModel
from opsml.registry.types import (
    CommonKwargs,
    TorchOnnxArgs,
    TrainedModelType,
)

try:
    from lightning import Trainer

    class LightningModel(PyTorchModel):
        """Model interface for Pytorch Lightning models.

        Args:
            model:
                Torch lightning model
            preprocessor:
                Optional preprocessor
            sample_data:
                Sample data to be used for type inference and ONNX conversion/validation.
                This should match exactly what the model expects as input. See example below.
            task_type:
                Task type for model. Defaults to undefined.
            model_type:
                Optional model type. This is inferred automatically.
            preprocessor_name:
                Optional preprocessor. This is inferred automatically if a
                preprocessor is provided.

        Returns:
        LightningModel
        """

        model: Optional[Trainer] = None
        onnx_args: Optional[TorchOnnxArgs] = None
        model_class: str = TrainedModelType.PYTORCH_LIGHTNING.value

        @model_validator(mode="before")
        @classmethod
        def check_model(cls, model_args: Dict[str, Any]) -> Dict[str, Any]:
            model = model_args.get("model")

            # passed as extra when modelcard is being loaded
            if model_args.get("model_uri", False):
                return model_args

            model, module, bases = get_model_args(model)

            if "lightning.pytorch" in module:
                model_args[CommonKwargs.MODEL_TYPE.value] = model.model.__class__.__name__

            for base in bases:
                if "lightning.pytorch" in base:
                    model_args[CommonKwargs.MODEL_TYPE.value] = "subclass"

            sample_data = cls.get_sample_data(sample_data=model_args.get(CommonKwargs.SAMPLE_DATA.value))
            model_args[CommonKwargs.SAMPLE_DATA.value] = sample_data
            model_args[CommonKwargs.DATA_TYPE.value] = get_class_name(sample_data)
            model_args[CommonKwargs.PREPROCESSOR_NAME.value] = cls._get_preprocessor_name(
                preprocessor=model_args.get(CommonKwargs.PREPROCESSOR.value)
            )

            return model_args

        def get_sample_prediction(self) -> SamplePrediction:
            assert self.model is not None, "Model is not defined"
            assert self.sample_data is not None, "Sample data must be provided"

            # test dict input
            if isinstance(self.sample_data, dict):
                try:
                    prediction = self.model.model(**self.sample_data)
                except Exception:
                    prediction = self.model.model(self.sample_data)

            # test list and tuple inputs
            elif isinstance(self.sample_data, (list, tuple)):
                try:
                    prediction = self.model.model(*self.sample_data)
                except Exception:
                    prediction = self.model.model(self.sample_data)

            # all others
            else:
                prediction = self.model.model(self.sample_data)

            prediction_type = get_class_name(prediction)

            return SamplePrediction(prediction_type, prediction)

except ModuleNotFoundError:

    class LightningModel(PyTorchModel):
        @model_validator(mode="before")
        @classmethod
        def check_model(cls, model_args: Dict[str, Any]) -> Dict[str, Any]:
            raise ModuleNotFoundError("LightningModel requires pytorch lightning to be installed. Please install lightning.")
