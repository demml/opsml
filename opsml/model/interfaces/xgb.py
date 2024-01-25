from pathlib import Path
from typing import Any, Dict, Optional, Union

import joblib
import pandas as pd
from numpy.typing import NDArray
from pydantic import model_validator

from opsml.helpers.logging import ArtifactLogger
from opsml.helpers.utils import get_class_name
from opsml.model import ModelInterface
from opsml.model.interfaces.base import get_model_args, get_processor_name
from opsml.types import CommonKwargs, ModelReturn, Suffix, TrainedModelType

logger = ArtifactLogger.get_logger()

try:
    from xgboost import Booster, DMatrix, XGBModel

    class XGBoostModel(ModelInterface):
        """Model interface for XGBoost model class. Currently, only Sklearn flavor of XGBoost
        regressor and classifier are supported.

        Args:
            model:
                XGBoost model. Can be either a Booster or XGBModel.
            preprocessor:
                Optional preprocessor
            sample_data:
                Sample data to be used for type inference and ONNX conversion/validation.
                This should match exactly what the model expects as input.
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

        model: Optional[Union[Booster, XGBModel]] = None
        sample_data: Optional[Union[pd.DataFrame, NDArray[Any], DMatrix]] = None
        preprocessor: Optional[Any] = None
        preprocessor_name: str = CommonKwargs.UNDEFINED.value

        @property
        def model_class(self) -> str:
            if "Booster" in self.model_type:
                return TrainedModelType.XGB_BOOSTER.value
            return TrainedModelType.SKLEARN_ESTIMATOR.value

        @classmethod
        def _get_sample_data(cls, sample_data: Any) -> Union[pd.DataFrame, NDArray[Any], DMatrix]:
            """Check sample data and returns one record to be used
            during type inference and ONNX conversion/validation.

            Returns:
                Sample data with only one record
            """
            if isinstance(sample_data, DMatrix):
                return sample_data.slice([0])
            return super()._get_sample_data(sample_data)

        @model_validator(mode="before")
        @classmethod
        def check_model(cls, model_args: Dict[str, Any]) -> Dict[str, Any]:
            model = model_args.get("model")

            if model_args.get("modelcard_uid", False):
                return model_args

            model, _, bases = get_model_args(model)

            if isinstance(model, XGBModel):
                model_args[CommonKwargs.MODEL_TYPE.value] = model.__class__.__name__

            elif isinstance(model, Booster):
                model_args[CommonKwargs.MODEL_TYPE.value] = "Booster"

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

        def save_model(self, path: Path) -> None:
            """Saves lgb model according to model format. Booster models are saved to text.
            Sklearn models are saved via joblib.

            Args:
                path:
                    base path to save model to
            """
            assert self.model is not None, "No model found"
            if isinstance(self.model, Booster):
                self.model.save_model(path)

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
                self.model = Booster(model_file=path)
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

        def save_onnx(self, path: Path) -> ModelReturn:
            """Saves the onnx model

            Args:
                path:
                    Path to save

            Returns:
                ModelReturn
            """

            if self.model_class == TrainedModelType.XGB_BOOSTER.value:
                logger.warning("ONNX conversion for XGBoost Booster is not supported")

            return super().save_onnx(path)

        def save_sample_data(self, path: Path) -> None:
            """Serialized and save sample data to path.

            Args:
                path:
                    Pathlib object
            """
            if isinstance(self.sample_data, DMatrix):
                self.sample_data.save_binary(path)

            else:
                joblib.dump(self.sample_data, path)

        def load_sample_data(self, path: Path) -> None:
            """Serialized and save sample data to path.

            Args:
                path:
                    Pathlib object
            """
            if self.model_class == TrainedModelType.XGB_BOOSTER.value:
                self.sample_data = DMatrix(path)
            else:
                self.sample_data = joblib.load(path)

        @property
        def model_suffix(self) -> str:
            if self.model_type == TrainedModelType.XGB_BOOSTER.value:
                return Suffix.JSON.value

            return super().model_suffix

        @property
        def preprocessor_suffix(self) -> str:
            """Returns suffix for storage"""
            return Suffix.JOBLIB.value

        @property
        def data_suffix(self) -> str:
            """Returns suffix for storage"""
            if self.model_class == TrainedModelType.XGB_BOOSTER.value:
                return Suffix.DMATRIX.value
            return Suffix.JOBLIB.value

        @staticmethod
        def name() -> str:
            return XGBoostModel.__name__

except ModuleNotFoundError:
    from opsml.model.interfaces.backups import XGBoostModelNoModule as XGBoostModel
