import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union, cast

import joblib
from pydantic import model_validator

from opsml.helpers.utils import OpsmlImportExceptions, get_class_name
from opsml.model.interfaces.base import (
    ModelInterface,
    SamplePrediction,
    get_model_args,
    get_processor_name,
)
from opsml.types import (
    CommonKwargs,
    ModelReturn,
    SaveName,
    Suffix,
    TorchOnnxArgs,
    TorchSaveArgs,
    TrainedModelType,
)

try:
    import torch

    ValidData = Union[torch.Tensor, Dict[str, torch.Tensor], List[torch.Tensor], Tuple[torch.Tensor]]

    class TorchModel(ModelInterface):
        """Model interface for Pytorch models.

        Args:
            model:
                Torch model
            preprocessor:
                Optional preprocessor
            sample_data:
                Sample data to be used for type inference and ONNX conversion/validation.
                This should match exactly what the model expects as input.
            save_args:
                Optional arguments for saving model. See `TorchSaveArgs` for supported arguments.
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
        TorchModel
        """

        model: Optional[torch.nn.Module] = None
        sample_data: Optional[
            Union[torch.Tensor, Dict[str, torch.Tensor], List[torch.Tensor], Tuple[torch.Tensor]]
        ] = None
        onnx_args: Optional[TorchOnnxArgs] = None
        save_args: TorchSaveArgs = TorchSaveArgs()
        preprocessor: Optional[Any] = None
        preprocessor_name: str = CommonKwargs.UNDEFINED.value

        @property
        def model_class(self) -> str:
            return TrainedModelType.PYTORCH.value

        @classmethod
        def _get_sample_data(cls, sample_data: Any) -> Any:
            """Check sample data and returns one record to be used
            during type inference and ONNX conversion/validation.

            Returns:
                Sample data with only one record
            """
            if isinstance(sample_data, torch.Tensor):
                return sample_data[0:1]

            if isinstance(sample_data, list):
                return [data[0:1] for data in sample_data]

            if isinstance(sample_data, tuple):
                return tuple(data[0:1] for data in sample_data)

            if isinstance(sample_data, dict):
                sample_dict = {}
                for key, value in sample_data.items():
                    sample_dict[key] = value[0:1]
                return sample_dict

            raise ValueError("Provided sample data is not a valid type")

        @model_validator(mode="before")
        @classmethod
        def check_model(cls, model_args: Dict[str, Any]) -> Dict[str, Any]:
            model = model_args.get("model")

            if model_args.get("modelcard_uid", False):
                return model_args

            model, _, bases = get_model_args(model)

            for base in bases:
                if "torch" in base:
                    model_args[CommonKwargs.MODEL_TYPE.value] = model.__class__.__name__

            sample_data = cls._get_sample_data(model_args[CommonKwargs.SAMPLE_DATA.value])
            model_args[CommonKwargs.SAMPLE_DATA.value] = sample_data
            model_args[CommonKwargs.DATA_TYPE.value] = get_class_name(sample_data)
            model_args[CommonKwargs.PREPROCESSOR_NAME.value] = get_processor_name(
                model_args.get(CommonKwargs.PREPROCESSOR.value),
            )

            return model_args

        def get_sample_prediction(self) -> SamplePrediction:
            assert self.model is not None, "Model is not defined"
            assert self.sample_data is not None, "Sample data must be provided"

            # test dict input
            if isinstance(self.sample_data, dict):
                try:
                    prediction = self.model(**self.sample_data)
                except Exception as _:  # pylint: disable=broad-except
                    prediction = self.model(self.sample_data)

            # test list and tuple inputs
            elif isinstance(self.sample_data, (list, tuple)):
                try:
                    prediction = self.model(*self.sample_data)
                except Exception as _:  # pylint: disable=broad-except
                    prediction = self.model(self.sample_data)

            # all others
            else:
                prediction = self.model(self.sample_data)

            prediction_type = get_class_name(prediction)

            return SamplePrediction(prediction_type, prediction)

        def save_model(self, path: Path) -> None:
            """Save pytorch model to path

            Args:
                path:
                    pathlib object
            """
            assert self.model is not None, "No model found"

            if self.save_args.as_state_dict:
                torch.save(self.model.state_dict(), path)
            else:
                torch.save(self.model, path)

        def load_model(self, path: Path, **kwargs: Any) -> None:
            """Load pytorch model from path

            Args:
                path:
                    pathlib object
                kwargs:
                    Additional arguments to be passed to torch.load
            """
            model_arch = kwargs.get(CommonKwargs.MODEL_ARCH.value)

            if model_arch is not None:
                model_arch.load_state_dict(torch.load(path))
                model_arch.eval()
                self.model = model_arch

            else:
                self.model = torch.load(path)

        def save_onnx(self, path: Path) -> ModelReturn:
            """Saves an onnx model

            Args:
                path:
                    Path to save model to

            Returns:
                ModelReturn
            """
            import onnxruntime as rt

            from opsml.model.onnx import _get_onnx_metadata

            if self.onnx_model is None:
                self.convert_to_onnx(**{"path": path})

            else:
                # save onnx model
                self.onnx_model.sess_to_path(path)

            # no need to save onnx to bytes since its done during onnx conversion
            assert self.onnx_model is not None, "No onnx model detected in interface"
            return _get_onnx_metadata(self, cast(rt.InferenceSession, self.onnx_model.sess))

        def _convert_to_onnx_inplace(self) -> None:
            """Convert to onnx model using temp dir"""
            with tempfile.TemporaryDirectory() as tmpdir:
                lpath = Path(tmpdir) / SaveName.ONNX_MODEL.value
                onnx_path = lpath.with_suffix(Suffix.ONNX.value)
                self.convert_to_onnx(**{"path": onnx_path})

        def convert_to_onnx(self, **kwargs: Path) -> None:
            # import packages for onnx conversion
            OpsmlImportExceptions.try_torchonnx_imports()
            if self.onnx_model is not None:
                return None

            from opsml.model.onnx.torch_converter import _PyTorchOnnxModel

            path: Optional[Path] = kwargs.get("path")

            if path is None:
                return self._convert_to_onnx_inplace()

            self.onnx_model = _PyTorchOnnxModel(self).convert_to_onnx(path=path)
            return None

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
            return Suffix.PT.value

        @staticmethod
        def name() -> str:
            return TorchModel.__name__

except ModuleNotFoundError:
    from opsml.model.interfaces.backups import TorchModelNoModule as TorchModel
