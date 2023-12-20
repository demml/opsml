from typing import Any, Dict, List, Optional, Tuple, Union

import pandas as pd
from numpy.typing import NDArray
from pydantic import model_validator

from opsml.helpers.utils import get_class_name
from opsml.registry.model.interfaces.base import SupportedModel, get_model_args
from opsml.registry.types import CommonKwargs, OnnxModelDefinition, TrainedModelType

try:
    from sklearn.base import BaseEstimator

    VALID_DATA = Union[
        pd.DataFrame, NDArray[Any], Dict[str, NDArray[Any]], List[NDArray[Any]], Tuple[NDArray[Any]], Any
    ]

    class SklearnModel(SupportedModel):
        """Model interface for Sklearn models.

        Args:
            model:
                Sklearn model
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
                Optional preprocessor name. This is inferred automatically if a
                preprocessor is provided.

        Returns:
        SklearnModel
        """

        model: Optional[BaseEstimator] = None
        sample_data: Optional[VALID_DATA] = None
        onnx_model_def: Optional[OnnxModelDefinition] = None
        model_class: str = TrainedModelType.SKLEARN_ESTIMATOR.value

        @model_validator(mode="before")
        @classmethod
        def check_model(cls, model_args: Dict[str, Any]) -> Dict[str, Any]:
            model = model_args.get("model")

            # passed as extra when modelcard is being loaded
            if model_args.get("model_uri", False):
                return model_args

            model, module, bases = get_model_args(model)

            if "sklearn" in module:
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

    class SklearnModel(SupportedModel):
        @model_validator(mode="before")
        @classmethod
        def check_model(cls, model_args: Dict[str, Any]) -> Dict[str, Any]:
            raise ModuleNotFoundError(
                "SklearnModel requires scikit-learn to be installed. Please install scikit-learn."
            )
