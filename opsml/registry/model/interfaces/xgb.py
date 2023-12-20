from typing import Any, Dict

from pydantic import model_validator

from opsml.helpers.utils import get_class_name
from opsml.registry.model.interfaces.base import SupportedModel, get_model_args
from opsml.registry.types import CommonKwargs

try:
    from xgboost import XGBModel

    from opsml.registry.model.interfaces.sklearn import SklearnModel

    class XGBoostModel(SklearnModel):
        """Model interface for XGBoost model class. Currently, only Sklearn flavor of XGBoost
        regressor and classifier are supported.

        Args:
            model:
                XGBoost model
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
            XGBoostModel
        """

        @model_validator(mode="before")
        @classmethod
        def check_model(cls, model_args: Dict[str, Any]) -> Dict[str, Any]:
            model = model_args.get("model")

            # passed as extra when modelcard is being loaded
            if model_args.get("model_uri", False):
                return model_args

            model, _, bases = get_model_args(model)

            if isinstance(model, XGBModel):
                model_args[CommonKwargs.MODEL_TYPE.value] = model.__class__.__name__

            else:
                for base in bases:
                    if "sklearn" in base:
                        model_args[CommonKwargs.MODEL_TYPE.value] = "subclass"

            sample_data = cls.get_sample_data(sample_data=model_args.get(CommonKwargs.SAMPLE_DATA.value))
            model_args[CommonKwargs.SAMPLE_DATA.value] = sample_data
            model_args[CommonKwargs.DATA_TYPE.value] = get_class_name(sample_data)
            model_args[CommonKwargs.PREPROCESSOR_NAME.value] = cls._get_preprocessor_name(
                preprocessor=model_args.get(CommonKwargs.PREPROCESSOR.value)
            )

            return model_args

except ModuleNotFoundError:

    class XGBoostModel(SupportedModel):
        @model_validator(mode="before")
        @classmethod
        def check_model(cls, model_args: Dict[str, Any]) -> Dict[str, Any]:
            raise ModuleNotFoundError("XGBoostModel requires xgboost to be installed. Please install xgboost.")
