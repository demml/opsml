from dataclasses import dataclass
from pathlib import Path
from typing import Any, List, Optional, Tuple

import joblib
import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict

from opsml.helpers.utils import get_class_name
from opsml.registry.types import CommonKwargs, ModelReturn, OnnxModel
from opsml.registry.types.extra import Suffix


def get_model_args(model: Any) -> Tuple[Any, str, List[str]]:
    assert model is not None, "Model must not be None"

    model_module = model.__module__
    model_bases = [str(base) for base in model.__class__.__bases__]

    return model, model_module, model_bases


@dataclass
class SamplePrediction:
    """Dataclass that holds sample prediction information

    Args:
        prediction_type:
            Type of prediction
        prediction:
            Sample prediction
    """

    prediction_type: str
    prediction: Any


class ModelInterface(BaseModel):
    model: Optional[Any] = None
    preprocessor: Optional[Any] = None
    sample_data: Optional[Any] = None
    onnx_model: Optional[OnnxModel] = None
    task_type: str = CommonKwargs.UNDEFINED.value
    model_type: str = CommonKwargs.UNDEFINED.value
    preprocessor_name: str = CommonKwargs.UNDEFINED.value
    data_type: str = CommonKwargs.UNDEFINED.value

    model_config = ConfigDict(
        protected_namespaces=("protect_",),
        arbitrary_types_allowed=True,
        validate_assignment=False,
        validate_default=True,
        extra="allow",
    )

    @property
    def model_class(self) -> str:
        raise NotImplementedError

    def save_model(self, path: Path) -> Path:
        """Saves model to path. Base implementation use Joblib

        Args:
            path:
                Pathlib object
        """
        assert self.model is not None, "No model detected in interface"
        save_path = path.with_suffix(self.storage_suffix)
        joblib.dump(self.model, save_path)

        return save_path

    def save_preprocessor(self, path: Path) -> Path:
        """Saves preprocessor to path if present. Base implementation use Joblib

        Args:
            path:
                Pathlib object
        """
        assert self.preprocessor is not None, "No preprocessor detected in interface"
        save_path = path.with_suffix(self.storage_suffix)
        joblib.dump(self.preprocessor, save_path)

        return save_path

    def load_model(self, path: Path) -> None:
        """Load model from pathlib object

        Args:
            path:
                Pathlib object
        """
        save_path = path.with_suffix(self.storage_suffix)
        self.model = joblib.load(save_path)

    def load_preprocessor(self, path: Path) -> None:
        """Load preprocessor from pathlib object

        Args:
            path:
                Pathlib object
        """
        save_path = path.with_suffix(self.storage_suffix)
        self.preprocessor = joblib.load(save_path)

    def convert_to_onnx(self, path: Path) -> Tuple[ModelReturn, Path]:
        # don't want to try and import onnx unless we need to
        import onnxruntime as rt

        from opsml.registry.model.model_converters import _OnnxModelConverter

        if self.onnx_model is None:
            metadata = _OnnxModelConverter(self).convert_model()
            self.onnx_model = metadata.onnx_model

        sess: rt.InferenceSession = self.onnx_model.sess
        path = path.with_suffix(Suffix.ONNX.value)
        path.write_bytes(sess._model_bytes)

        return metadata, path

    def load_onnx_model(self, path: Path) -> None:
        """Load onnx model from pathlib object

        Args:
            path:
                Pathlib object
        """
        from onnxruntime import InferenceSession

        onnx_path = path.with_suffix(".onnx")
        self.onnx_model.sess = InferenceSession(onnx_path)

    def download_artifacts(self) -> Any:
        raise NotImplementedError

    @classmethod
    def _get_preprocessor_name(cls, preprocessor: Optional[Any] = None) -> str:
        if preprocessor is not None:
            return preprocessor.__class__.__name__

        return CommonKwargs.UNDEFINED.value

    def save_sample_data(self, path: Path) -> Path:
        """Serialized and save sample data to path.

        Args:
            path:
                Pathlib object
        """
        save_path = path.with_suffix(Suffix.JOBLIB.value)
        joblib.dump(self.sample_data, save_path)
        return save_path

    def load_sample_data(self, path: Path) -> None:
        """Serialized and save sample data to path.

        Args:
            path:
                Pathlib object
        """

        self.sample_data = joblib.load(path)

    @classmethod
    def get_sample_data(cls, sample_data: Optional[Any] = None) -> Any:
        """Check sample data and returns one record to be used
        during type inference and ONNX conversion/validation.

        Returns:
            Sample data with only one record
        """
        if isinstance(sample_data, list):
            return [data[0:1] for data in sample_data]

        if isinstance(sample_data, tuple):
            return (data[0:1] for data in sample_data)

        if isinstance(sample_data, dict):
            return {key: data[0:1] for key, data in sample_data.items()}

        return sample_data[0:1]

    def get_sample_prediction(self) -> SamplePrediction:
        assert self.model is not None, "Model is not defined"
        assert self.sample_data is not None, "Sample data must be provided"

        if isinstance(self.sample_data, (pd.DataFrame, np.ndarray)):
            prediction = self.model.predict(self.sample_data)

        elif isinstance(self.sample_data, dict):
            try:
                prediction = self.model.predict(**self.sample_data)
            except Exception:
                prediction = self.model.predict(self.sample_data)

        elif isinstance(self.sample_data, (list, tuple)):
            try:
                prediction = self.model.predict(*self.sample_data)
            except Exception:
                prediction = self.model.predict(self.sample_data)

        else:
            prediction = self.model.predict(self.sample_data)

        prediction_type = get_class_name(prediction)

        return SamplePrediction(
            prediction_type,
            prediction,
        )

    @property
    def storage_suffix(self) -> str:
        """Returns suffix for storage"""
        return Suffix.JOBLIB.value
