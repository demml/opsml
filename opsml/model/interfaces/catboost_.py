import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, cast

import joblib
import numpy as np
from numpy.typing import NDArray
from pydantic import model_validator

from opsml.helpers.logging import ArtifactLogger
from opsml.helpers.utils import get_class_name
from opsml.model.interfaces.base import (
    ModelInterface,
    SamplePrediction,
    get_model_args,
    get_processor_name,
)
from opsml.types import (
    CommonKwargs,
    ModelReturn,
    OnnxModel,
    SaveName,
    Suffix,
    TrainedModelType,
)

logger = ArtifactLogger.get_logger()

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
                This should match exactly what the model expects as input.
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
        sample_data: Optional[Union[List[Any], NDArray[Any]]] = None
        preprocessor: Optional[Any] = None
        preprocessor_name: str = CommonKwargs.UNDEFINED.value

        @classmethod
        def _get_sample_data(cls, sample_data: NDArray[Any]) -> Union[List[Any], NDArray[Any]]:
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

            raise ValueError("Sample data should be a list or numpy array")

        def get_sample_prediction(self) -> SamplePrediction:
            assert self.model is not None, "Model is not defined"
            assert self.sample_data is not None, "Sample data must be provided"

            prediction = self.model.predict(self.sample_data)

            prediction_type = get_class_name(prediction)

            return SamplePrediction(prediction_type, prediction)

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

            if "catboost" in module:
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

        def save_model(self, path: Path) -> None:
            """Saves model to path. Base implementation use Joblib

            Args:
                path:
                    Pathlib object
            """
            assert self.model is not None, "No model detected in interface"
            self.model.save_model(path.as_posix())

        def load_model(self, path: Path, **kwargs: Any) -> None:
            """Load model from pathlib object

            Args:
                path:
                    Pathlib object
                kwargs:
                    Additional kwargs
            """
            import catboost

            model = getattr(catboost, self.model_type, CatBoost)()
            self.model = model.load_model(path.as_posix())

        def _convert_to_onnx_inplace(self) -> None:
            """Convert to onnx model using temp dir"""
            with tempfile.TemporaryDirectory() as tmpdir:
                lpath = Path(tmpdir) / SaveName.ONNX_MODEL.value
                onnx_path = lpath.with_suffix(Suffix.ONNX.value)
                self.convert_to_onnx(**{"path": onnx_path})

        def convert_to_onnx(self, **kwargs: Path) -> None:
            """Converts model to onnx format"""

            logger.info("Converting CatBoost model to onnx format")

            import onnx
            import onnxruntime as rt

            if self.onnx_model is not None:
                return None

            path: Optional[Path] = kwargs.get("path")
            if path is None:
                return self._convert_to_onnx_inplace()

            assert self.model is not None, "No model detected in interface"
            self.model.save_model(
                path.as_posix(),
                format="onnx",
                export_parameters={"onnx_domain": "ai.catboost"},
            )
            self.onnx_model = OnnxModel(
                onnx_version=onnx.__version__,
                sess=rt.InferenceSession(path.as_posix()),
            )
            return None

        def save_onnx(self, path: Path) -> ModelReturn:
            import onnxruntime as rt

            from opsml.model.onnx import _get_onnx_metadata

            if self.onnx_model is None:
                self.convert_to_onnx(**{"path": path})

            else:
                self.onnx_model.sess_to_path(path)

            assert self.onnx_model is not None, "No onnx model detected in interface"

            # no need to save onnx to bytes since its done during onnx conversion
            return _get_onnx_metadata(self, cast(rt.InferenceSession, self.onnx_model.sess))

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

        @property
        def model_suffix(self) -> str:
            """Returns suffix for storage"""
            return Suffix.CATBOOST.value

        @staticmethod
        def name() -> str:
            return CatBoostModel.__name__

except ModuleNotFoundError:
    from opsml.model.interfaces.backups import CatBoostModelNoModule as CatBoostModel
