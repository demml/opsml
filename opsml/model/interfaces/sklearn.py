from pathlib import Path
from typing import Any, Dict, Optional, Union

import joblib
import pandas as pd
from numpy.typing import NDArray
from pydantic import model_validator

from opsml.helpers.utils import get_class_name
from opsml.model.interfaces.base import (
    ModelInterface,
    get_model_args,
    get_processor_name,
)
from opsml.types import CommonKwargs, Suffix, TrainedModelType

try:
    from sklearn.base import BaseEstimator

    class SklearnModel(ModelInterface):
        """Model interface for Sklearn models.

        Args:
            model:
                Sklearn model
            preprocessor:
                Optional preprocessor
            sample_data:
                Sample data to be used for type inference.
                For sklearn models this should be a pandas DataFrame or numpy array.
                This should match exactly what the model expects as input.
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
        sample_data: Optional[Union[pd.DataFrame, NDArray[Any]]] = None
        preprocessor: Optional[Any] = None
        preprocessor_name: str = CommonKwargs.UNDEFINED.value

        @property
        def model_class(self) -> str:
            return TrainedModelType.SKLEARN_ESTIMATOR.value

        @model_validator(mode="before")
        @classmethod
        def check_model(cls, model_args: Dict[str, Any]) -> Dict[str, Any]:
            model = model_args.get("model")

            if model_args.get("modelcard_uid", False):
                return model_args

            model, module, bases = get_model_args(model)

            if "sklearn" in module:
                model_args[CommonKwargs.MODEL_TYPE.value] = model.__class__.__name__

            else:
                for base in bases:
                    if "sklearn" in base:
                        model_args[CommonKwargs.MODEL_TYPE.value] = "subclass"

            sample_data = cls._get_sample_data(sample_data=model_args[CommonKwargs.SAMPLE_DATA.value])
            model_args[CommonKwargs.SAMPLE_DATA.value] = sample_data
            model_args[CommonKwargs.DATA_TYPE.value] = get_class_name(sample_data)
            model_args[CommonKwargs.PREPROCESSOR_NAME.value] = get_processor_name(
                model_args.get(CommonKwargs.PREPROCESSOR.value),
            )

            return model_args

        def save_preprocessor(self, path: Path) -> None:
            """Saves preprocessor to path if present. Base implementation use Joblib

            Args:
                path:
                    Pathlib object
            """
            assert self.preprocessor is not None, "No preprocessor detected in interface"
            joblib.dump(self.preprocessor, path)

        def load_preprocessor(self, path: Path) -> None:
            """Load preprocessor from pathlib object

            Args:
                path:
                    Pathlib object
            """
            self.preprocessor = joblib.load(path)

        @property
        def preprocessor_suffix(self) -> str:
            """Returns suffix for storage"""
            return Suffix.JOBLIB.value

        @staticmethod
        def name() -> str:
            return SklearnModel.__name__

except ModuleNotFoundError:
    from opsml.model.interfaces.backups import SklearnModelNoModule as SklearnModel
