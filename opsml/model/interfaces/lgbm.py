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
from opsml.types import CommonKwargs, TrainedModelType
from opsml.types.extra import Suffix

try:
    import lightgbm as lgb
    from lightgbm import Booster, LGBMModel

    class LightGBMModel(ModelInterface):
        """Model interface for LightGBM Booster model class. If using the sklearn API, use SklearnModel instead.

        Args:
            model:
                LightGBM booster model
            preprocessor:
                Optional preprocessor
            sample_data:
                Sample data to be used for type inference.
                For lightgbm models this should be a pandas DataFrame or numpy array.
                This should match exactly what the model expects as input.
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
            LightGBMModel
        """

        model: Optional[Union[Booster, LGBMModel]] = None
        sample_data: Optional[Union[pd.DataFrame, NDArray[Any]]] = None
        preprocessor: Optional[Any] = None
        preprocessor_name: str = CommonKwargs.UNDEFINED.value

        @property
        def model_class(self) -> str:
            if "Booster" in self.model_type:
                return TrainedModelType.LGBM_BOOSTER.value
            return TrainedModelType.SKLEARN_ESTIMATOR.value

        @model_validator(mode="before")
        @classmethod
        def check_model(cls, model_args: Dict[str, Any]) -> Dict[str, Any]:
            model = model_args.get("model")

            if model_args.get("modelcard_uid", False):
                return model_args

            model, module, _ = get_model_args(model)

            if "lightgbm" in module or isinstance(model, LGBMModel):
                model_args[CommonKwargs.MODEL_TYPE.value] = model.__class__.__name__

            sample_data = cls._get_sample_data(sample_data=model_args[CommonKwargs.SAMPLE_DATA.value])
            model_args[CommonKwargs.SAMPLE_DATA.value] = sample_data
            model_args[CommonKwargs.DATA_TYPE.value] = get_class_name(sample_data)
            model_args[CommonKwargs.PREPROCESSOR_NAME.value] = get_processor_name(
                model_args.get(CommonKwargs.PREPROCESSOR.value),
            )

            return model_args

        def save_model(self, path: Path) -> None:
            """Saves lgb model according to model format. Booster models are saved to text.
            Sklearn models are saved via joblib.

            Args:
                path:
                    base path to save model to
            """
            assert self.model is not None, "No model found"
            if isinstance(self.model, Booster):
                self.model.save_model(filename=path)

            else:
                super().save_model(path)

        def load_model(self, path: Path, **kwargs: Any) -> None:
            """Loads lightgbm booster or sklearn model


            Args:
                path:
                    base path to load from
                **kwargs:
                    Additional keyword arguments
            """

            if self.model_type == TrainedModelType.LGBM_BOOSTER.value:
                self.model = lgb.Booster(model_file=path)
            else:
                super().load_model(path)

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
        def model_suffix(self) -> str:
            if self.model_type == TrainedModelType.LGBM_BOOSTER.value:
                return Suffix.TEXT.value

            return super().model_suffix

        @property
        def preprocessor_suffix(self) -> str:
            """Returns suffix for storage"""
            return Suffix.JOBLIB.value

        @staticmethod
        def name() -> str:
            return LightGBMModel.__name__

except ModuleNotFoundError:
    from opsml.model.interfaces.backups import LightGBMModelNoModule as LightGBMModel
