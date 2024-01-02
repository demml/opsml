from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union, cast

from pydantic import model_validator

from opsml.helpers.utils import OpsmlImportExceptions, get_class_name
from opsml.registry.model.interfaces.base import (
    ModelInterface,
    SamplePrediction,
    get_model_args,
)
from opsml.registry.types import (
    CommonKwargs,
    ModelReturn,
    Suffix,
    TorchOnnxArgs,
    TorchSaveArgs,
    TrainedModelType,
)

try:
    import torch

    VALID_DATA = Union[torch.Tensor, Dict[str, torch.Tensor], List[torch.Tensor], Tuple[torch.Tensor]]

    class PyTorchModel(ModelInterface):
        """Model interface for Pytorch models.

        Args:
            model:
                Torch model
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
                Optional preprocessor. This is inferred automatically if a
                preprocessor is provided.
            onnx_args:
                Optional arguments for ONNX conversion. See `TorchOnnxArgs` for supported arguments.

        Returns:
        PyTorchModel
        """

        model: Optional[torch.nn.Module] = None
        sample_data: Optional[VALID_DATA] = None
        onnx_args: Optional[TorchOnnxArgs] = None
        save_args: TorchSaveArgs = TorchSaveArgs()

        @property
        def model_class(self) -> str:
            return TrainedModelType.PYTORCH.value

        @classmethod
        def get_sample_data(cls, sample_data: Optional[Any] = None) -> Any:
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
                return (data[0:1] for data in sample_data)

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

            sample_data = cls.get_sample_data(sample_data=model_args.get(CommonKwargs.SAMPLE_DATA.value))
            model_args[CommonKwargs.SAMPLE_DATA.value] = sample_data
            model_args[CommonKwargs.DATA_TYPE.value] = get_class_name(sample_data)
            model_args[CommonKwargs.PREPROCESSOR_NAME.value] = cls._get_preprocessor_name(
                preprocessor=model_args.get(CommonKwargs.PREPROCESSOR.value)
            )

            return model_args

        def get_sample_prediction(self) -> SamplePrediction:
            assert self.model is not None, "Model is not defined"
            assert self.sample_data is not None, "Sample data must be provided"

            # test dict input
            if isinstance(self.sample_data, dict):
                try:
                    prediction = self.model(**self.sample_data)
                except Exception:
                    prediction = self.model(self.sample_data)

            # test list and tuple inputs
            elif isinstance(self.sample_data, (list, tuple)):
                try:
                    prediction = self.model(*self.sample_data)
                except Exception:
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

            if self.save_args.as_state_dict:
                torch.save(self.model.state_dict(), path)
            else:
                torch.save(self.model, path)

        def load_model(self, path: Path, **kwargs: Dict[str, Any]) -> None:
            """Load pytorch model from path

            Args:
                path:
                    pathlib object
            """
            self.model = torch.load(path)

        def convert_to_onnx(self, path: Path) -> ModelReturn:
            # import packages for onnx conversion
            OpsmlImportExceptions.try_torchonnx_imports()

            import onnxruntime as rt

            from opsml.registry.model.onnx import _get_onnx_metadata
            from opsml.registry.model.onnx.torch_converter import _PyTorchOnnxModel

            if self.onnx_model is None:
                self.onnx_model = _PyTorchOnnxModel(self).convert_to_onnx(path=path)
            else:
                sess: rt.InferenceSession = self.onnx_model.sess
                path.write_bytes(sess._model_bytes)

            return _get_onnx_metadata(self, cast(rt.InferenceSession, self.onnx_model.sess))

        @property
        def model_suffix(self) -> str:
            """Returns suffix for storage"""
            return Suffix.PT.value

        @staticmethod
        def name() -> str:
            return PyTorchModel.__name__

except ModuleNotFoundError:
    VALID_DATA = Any

    class PyTorchModel(ModelInterface):
        @model_validator(mode="before")
        @classmethod
        def check_model(cls, model_args: Dict[str, Any]) -> Dict[str, Any]:
            raise ModuleNotFoundError("PyTorchModel requires torch to be installed. Please install pytorch.")

        @staticmethod
        def name() -> str:
            return PyTorchModel.__name__
