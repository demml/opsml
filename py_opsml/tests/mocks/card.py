from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional, Union

import joblib  # type: ignore
from pydantic import BaseModel, ConfigDict, Field
from opsml_core import (
    CommonKwargs,
    Feature,
    Suffix,
    ModelInterfaceType,
    SaveName,
    ModelInterfaceSaveMetadata,
    ModelInterfaceMetadata,
)
import onnxruntime as rt  # type: ignore

OnnxInferenceSession = rt.InferenceSession


class OnnxModel(BaseModel):
    onnx_version: str = Field(
        ..., description="Version of onnx model used to create proto"
    )
    sess: Union[rt.InferenceSession] = Field(
        default=None, description="Onnx model session"
    )  # type: ignore

    model_config = ConfigDict(arbitrary_types_allowed=True)


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
    task_type: str = CommonKwargs.Undefined.as_string()
    model_type: str = CommonKwargs.Undefined.as_string()
    data_type: str = CommonKwargs.Undefined.as_string()
    modelcard_uid: str = CommonKwargs.Undefined.as_string()
    feature_map: Dict[str, Feature] = {}
    sample_data_interface_type: str = CommonKwargs.Undefined.as_string()
    preprocessor: Optional[Any] = None

    model_config = ConfigDict(
        protected_namespaces=("protect_",),
        arbitrary_types_allowed=True,
        validate_assignment=False,
        validate_default=True,
        extra="allow",
    )

    def _save_model(self, path: Path) -> str:
        """Saves model to path. Base implementation use Joblib

        Args:
            path:
                Pathlib object
        """
        assert self.model is not None, "No model detected in interface"

        save_path = (path / SaveName.TrainedModel.as_string()).with_suffix(
            Suffix.Joblib.as_string()
        )
        # joblib.dump(self.model, save_path)

        return save_path.as_posix()

    def _load_model(self, path: Path, **kwargs: Any) -> None:
        """Load model from pathlib object

        Args:
            path:
                Pathlib object
            kwargs:
                Additional kwargs
        """
        self.model = joblib.load(path, **kwargs)

    def _save_sample_data(self, path: Path) -> str:
        """Serialize and save sample data to path.

        Attempts to save data based on the type of data provided with the following order:

        1. If sample data is an interface, save data using the interface
        2. Save using joblib

        Args:
            path:
                Pathlib object
        """

        save_path = (path / SaveName.SampleModelData.as_string()).with_suffix(
            Suffix.Joblib.as_string()
        )
        # joblib.dump(self.sample_data, save_path)

        return save_path.as_posix()

    def _load_sample_data(self, path: Path, **kwargs: Any) -> None:
        """Load sample data from path

        Args:
            path:
                Pathlib object

        """
        self.sample_data = joblib.load(path, **kwargs)

    def _save_preprocessor(self, path: Path) -> Optional[str]:
        # if self.preprocessor is None:
        # return None

        save_path = (path / SaveName.SampleModelData.as_string()).with_suffix(
            Suffix.Joblib.as_string()
        )
        # joblib.dump(self.sample_data, save_path)

        return save_path.as_posix()

    def save_onnx(self, path: Path) -> str:
        """Saves the onnx model

        Args:
            path:
                Path to save

        Returns:
            ModelReturn
        """

        save_path = (path / SaveName.OnnxModel.as_string()).with_suffix(
            Suffix.Onnx.as_string()
        )

        return save_path.as_posix()

    def save_interface_artifacts(
        self,
        path: Path,
        to_onnx: bool,
    ) -> ModelInterfaceMetadata:
        """Save interface artifacts to path

        Args:
            path:
                Pathlib object
            to_onnx:
                Convert model to onnx

        Returns:
            ModelInterfaceMetadata
        """

        trained_model_uri = self._save_model(path)
        sample_data_uri = self._save_sample_data(path)
        preprocessor_uri = self._save_preprocessor(path)
        onnx_model_uri = None

        if to_onnx:
            onnx_model_uri = self.save_onnx(path)

        save_metadata = ModelInterfaceSaveMetadata(
            trained_model_uri=trained_model_uri,
            sample_data_uri=sample_data_uri,
            preprocessor_uri=preprocessor_uri,
            preprocessor_name=CommonKwargs.Undefined.as_string(),
            onnx_model_uri=onnx_model_uri,
        )

        return ModelInterfaceMetadata(
            interface=self,
            save_metadata=save_metadata,
        )

    @property
    def interface_type(self) -> ModelInterfaceType:
        return ModelInterfaceType.Base
