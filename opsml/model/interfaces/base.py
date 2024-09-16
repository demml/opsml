from dataclasses import dataclass
from functools import cached_property
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union, cast
from uuid import UUID

import joblib
import numpy as np
import pandas as pd
import polars as pl
import pyarrow as pa
from numpy.typing import NDArray
from pydantic import BaseModel, ConfigDict, field_validator, model_validator
from scouter import DriftConfig, Drifter, DriftProfile

from opsml.data import DataInterface
from opsml.helpers.utils import get_class_name
from opsml.types import (
    AllowedDataType,
    CommonKwargs,
    Feature,
    ModelReturn,
    OnnxModel,
    Suffix,
)


def get_processor_name(_class: Optional[Any] = None) -> str:
    if _class is not None:
        return str(_class.__class__.__name__)

    return CommonKwargs.UNDEFINED.value


def get_model_args(model: Any) -> Tuple[Any, str, List[str]]:
    assert model is not None, "Model must not be None"

    model_module = model.__module__
    model_bases = [str(base) for base in model.__class__.__bases__]

    return model, model_module, model_bases


def get_data_interface(data: Any, data_type: str) -> Optional[DataInterface]:
    """Attempts to infer the data interface based on the sample data provided"""
    if isinstance(data, pd.DataFrame):
        from opsml.data.interfaces import PandasData

        return PandasData(data=data)

    if isinstance(data, np.ndarray):
        from opsml.data.interfaces import NumpyData

        return NumpyData(data=data)

    if isinstance(data, pa.Table):
        from opsml.data.interfaces import ArrowData

        return ArrowData(data=data)

    if isinstance(data, pl.DataFrame):
        from opsml.data.interfaces import PolarsData

        return PolarsData(data=data)

    if data_type == AllowedDataType.TORCH_TENSOR.value:
        from opsml.data.interfaces import TorchData

        return TorchData(data=data)

    return None


def _set_data_args(data: Any, model_args: Dict[str, Any]) -> Dict[str, Any]:
    """Helper for setting data args

    Args:
        data:
            Sample data
        model_args:
            Pydantic ModelInterface args
    """
    if isinstance(data, DataInterface):
        model_args[CommonKwargs.DATA_TYPE.value] = data.data_type
        model_args[CommonKwargs.SAMPLE_DATA_INTERFACE_TYPE.value] = data.name()

    else:
        model_args[CommonKwargs.DATA_TYPE.value] = get_class_name(data)

    model_args[CommonKwargs.SAMPLE_DATA.value] = data

    return model_args


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
    sample_data: Optional[Any] = None
    onnx_model: Optional[OnnxModel] = None
    task_type: str = CommonKwargs.UNDEFINED.value
    model_type: str = CommonKwargs.UNDEFINED.value
    data_type: str = CommonKwargs.UNDEFINED.value
    modelcard_uid: str = ""
    feature_map: Dict[str, Feature] = {}
    sample_data_interface_type: str = CommonKwargs.UNDEFINED.value
    drift_profile: Optional[DriftProfile] = None

    model_config = ConfigDict(
        protected_namespaces=("protect_",),
        arbitrary_types_allowed=True,
        validate_assignment=False,
        validate_default=True,
        extra="allow",
    )

    @property
    def model_class(self) -> str:
        return CommonKwargs.UNDEFINED.value

    @model_validator(mode="before")
    @classmethod
    def check_model(cls, model_args: Dict[str, Any]) -> Dict[str, Any]:
        if model_args.get("modelcard_uid", False):
            return model_args

        sample_data = cls._get_sample_data(sample_data=model_args[CommonKwargs.SAMPLE_DATA.value])

        return _set_data_args(sample_data, model_args)

    @field_validator("modelcard_uid", mode="before")
    @classmethod
    def check_modelcard_uid(cls, modelcard_uid: str) -> str:
        # empty strings are falsey
        if not modelcard_uid:
            return modelcard_uid

        try:
            UUID(modelcard_uid, version=4)  # we use uuid4
            return modelcard_uid

        except ValueError as exc:
            raise ValueError("ModelCard uid is not a valid uuid") from exc

    def save_model(self, path: Path) -> None:
        """Saves model to path. Base implementation use Joblib

        Args:
            path:
                Pathlib object
        """
        assert self.model is not None, "No model detected in interface"
        joblib.dump(self.model, path)

    def load_model(self, path: Path, **kwargs: Any) -> None:
        """Load model from pathlib object

        Args:
            path:
                Pathlib object
            kwargs:
                Additional kwargs
        """
        self.model = joblib.load(path, **kwargs)

    def save_onnx(self, path: Path) -> ModelReturn:
        """Saves the onnx model

        Args:
            path:
                Path to save

        Returns:
            ModelReturn
        """
        import onnxruntime as rt

        from opsml.model.onnx import _get_onnx_metadata

        if self.onnx_model is None:
            self.convert_to_onnx()
            sess: rt.InferenceSession = self.onnx_model.sess
            path.write_bytes(sess._model_bytes)  # pylint: disable=protected-access

        else:
            self.onnx_model.sess_to_path(path.with_suffix(Suffix.ONNX.value))

        assert self.onnx_model is not None, "No onnx model detected in interface"
        metadata = _get_onnx_metadata(self, cast(rt.InferenceSession, self.onnx_model.sess))

        return metadata

    def convert_to_onnx(self, **kwargs: Path) -> None:
        """Converts model to onnx format"""
        from opsml.model.onnx import _OnnxModelConverter

        if self.onnx_model is not None:
            return None

        metadata = _OnnxModelConverter(self).convert_model()
        self.onnx_model = metadata.onnx_model

        return None

    def load_onnx_model(self, path: Path) -> None:
        """Load onnx model from pathlib object

        Args:
            path:
                Pathlib object
        """
        from onnxruntime import InferenceSession

        assert self.onnx_model is not None, "No onnx model detected in interface"
        self.onnx_model.sess = InferenceSession(path)

    def save_sample_data(self, path: Path) -> None:
        """Serialized and save sample data to path.

        Attempts to save data based on the type of data provided with the following order:

        1. If sample data is an interface, save data using the interface
        2. Save using joblib

        Args:
            path:
                Pathlib object
        """

        # (1)
        if isinstance(self.sample_data, DataInterface):
            self.sample_data.save_data(path)
            self.feature_map = self.sample_data.feature_map

        else:
            joblib.dump(self.sample_data, path)

    def load_sample_data(self, path: Path) -> None:
        """Serialized and save sample data to path.

        Args:
            path:
                Pathlib object
        """

        if isinstance(self.sample_data, DataInterface):
            self.sample_data.load_data(path)
            self.feature_map = self.sample_data.feature_map

        else:
            self.sample_data = joblib.load(path)

    @classmethod
    def _get_sample_data(cls, sample_data: Any) -> Any:
        """Check sample data and returns one record to be used
        during type inference and ONNX conversion/validation.

        Returns:
            Sample data with only one record
        """

        # check for data interface
        if isinstance(sample_data, DataInterface):
            assert sample_data.data is not None, "No data detected in interface"
            sample_data.data = sample_data.data[0:1]  #

            return sample_data

        # check if sample data can be converted to an interface
        interface: Optional[DataInterface] = get_data_interface(sample_data, get_class_name(sample_data))
        if interface is not None:
            assert interface.data is not None, "No data detected in interface"
            interface.data = interface.data[0:1]
            return interface

        # check for other types
        if isinstance(sample_data, list):
            return [data[0:1] for data in sample_data]

        if isinstance(sample_data, tuple):
            return (data[0:1] for data in sample_data)

        if isinstance(sample_data, dict):
            return {key: data[0:1] for key, data in sample_data.items()}

        return sample_data[0:1]

    def get_sample_prediction(self) -> SamplePrediction:
        assert self.model is not None, "Model is not defined"

        if isinstance(self._prediction_data, (pd.DataFrame, np.ndarray)):
            prediction = self.model.predict(self._prediction_data)

        elif isinstance(self._prediction_data, dict):
            try:
                prediction = self.model.predict(**self._prediction_data)
            except Exception as _:  # pylint: disable=broad-except
                prediction = self.model.predict(self._prediction_data)

        elif isinstance(self._prediction_data, (list, tuple)):
            try:
                prediction = self.model.predict(*self._prediction_data)
            except Exception as _:  # pylint: disable=broad-except
                prediction = self.model.predict(self._prediction_data)

        else:
            prediction = self.model.predict(self._prediction_data)

        prediction_type = get_class_name(prediction)

        return SamplePrediction(
            prediction_type,
            prediction,
        )

    @property
    def model_suffix(self) -> str:
        """Returns suffix for storage"""
        return Suffix.JOBLIB.value

    @property
    def data_suffix(self) -> str:
        """Returns suffix for storage"""
        return Suffix.JOBLIB.value

    @cached_property
    def _prediction_data(self) -> Any:
        """Returns data used for prediction"""
        if isinstance(self.sample_data, DataInterface):
            return cast(Any, self.sample_data.data)

        return self.sample_data

    def create_drift_profile(
        self,
        data: Union[pl.DataFrame, pd.DataFrame, NDArray[Any], pa.Table],
        monitor_config: DriftConfig,
    ) -> DriftProfile:
        """Create a drift profile from data to use for model monitoring.

        Args:
            data:
                Data to create a monitoring profile from. Data can be a numpy array, pyarrow table,
                a polars dataframe or pandas dataframe. Data is expected to not contain
                any missing values, NaNs or infinities and it typically the data used for training a model.
            monitor_config:
                Configuration for the monitoring profile.

        """

        if self.drift_profile is not None:
            return self.drift_profile

        drifter = Drifter()
        profile = drifter.create_drift_profile(
            data=data,
            monitor_config=monitor_config,
        )
        self.drift_profile = profile

        return profile

    @staticmethod
    def name() -> str:
        return ModelInterface.__name__
