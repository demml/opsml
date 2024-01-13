from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

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
import numpy as np
from opsml.types import CommonKwargs, Suffix, TrainedModelType

ValidData = Union[List[Any], NDArray[Any]]

try:
    from catboost import CatBoost

    class CatBoostModel(ModelInterface):
        """Model interface for CatBoost models.

        Args:
            model:
                CatBoost model (Classifier, Regressor, Ranker)
            preprocessor:
                Optional preprocessor
            sample_data:
                Sample data to be used for type inference and sample prediction.
                For catboost models this should be a numpy array (either 1d or 2d) or list of feature values.
                This should match exactly what the model expects as input. See example below.
            task_type:
                Task type for model. Defaults to undefined.
            model_type:
                Optional model type. This is inferred automatically.
            preprocessor_name:
                Optional preprocessor name. This is inferred automatically if a
                preprocessor is provided.

        Returns:
            CatBoostModel
        """

        model: Optional[CatBoost] = None
        sample_data: Optional[ValidData] = None
        preprocessor: Optional[Any] = None
        preprocessor_name: str = CommonKwargs.UNDEFINED.value

        @classmethod
        def _get_sample_data(cls, sample_data: NDArray[Any]) -> ValidData:
            """Check sample data and returns one record to be used
            during type inference and sample prediction.

            Returns:
                Sample data with only one record
            """

            if isinstance(sample_data, list):
                return sample_data

            if isinstance(sample_data, np.ndarray):
                if len(sample_data.shape) == 1:
                    return sample_data.reshape(1, -1)
                return sample_data[0:1]

        @property
        def model_class(self) -> str:
            return TrainedModelType.CATBOOST.value

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
                    if "catboost" in base:
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
            return CatBoostModel.__name__


except ModuleNotFoundError:
    from opsml.model.interfaces.backups import CatBoostModelNoModule as CatBoostModel
