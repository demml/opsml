from typing import Any, Dict, Optional

from pydantic import model_validator

from opsml.helpers.utils import get_class_name
from opsml.registry.model.interfaces.base import SupportedModel, get_model_args
from opsml.registry.types import CommonKwargs, OnnxModelDefinition, TrainedModelType

try:
    from lightgbm import Booster

    class LightGBMBoosterModel(SupportedModel):
        """Model interface for LightGBM Booster model class. If using the sklearn API, use SklearnModel instead.

        Args:
            model:
                LightGBM booster model
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
            onnx_args:
                Optional arguments for ONNX conversion. See `TorchOnnxArgs` for supported arguments.

        Returns:
            LightGBMBoosterModel
        """

        onnx_model_def: Optional[OnnxModelDefinition] = None
        model_class: str = TrainedModelType.LGBM_BOOSTER.value

        @model_validator(mode="before")
        @classmethod
        def check_model(cls, model_args: Dict[str, Any]) -> Dict[str, Any]:
            model = model_args.get("model")

            # passed as extra when modelcard is being loaded
            if model_args.get("model_uri", False):
                return model_args

            model, module, _ = get_model_args(model)

            assert isinstance(
                model, Booster
            ), "Model must be a lightgbm booster. If using the sklearn API, use SklearnModel instead."

            if "lightgbm" in module:
                model_args[CommonKwargs.MODEL_TYPE.value] = model.__class__.__name__

            sample_data = cls.get_sample_data(sample_data=model_args.get(CommonKwargs.SAMPLE_DATA.value))
            model_args[CommonKwargs.SAMPLE_DATA.value] = sample_data
            model_args[CommonKwargs.DATA_TYPE.value] = get_class_name(sample_data)
            model_args[CommonKwargs.PREPROCESSOR_NAME.value] = cls._get_preprocessor_name(
                preprocessor=model_args.get(CommonKwargs.PREPROCESSOR.value)
            )

            return model_args

        @property
        def supports_onnx(self) -> bool:
            return False

except ModuleNotFoundError:

    class LightGBMBoosterModel(SupportedModel):
        @model_validator(mode="before")
        @classmethod
        def check_model(cls, model_args: Dict[str, Any]) -> Dict[str, Any]:
            raise ModuleNotFoundError(
                "LightGBMBoosterModel requires lightgbm to be installed. Please install lightgbm."
            )
