from pathlib import Path
from typing import Any, Dict, Optional

from pydantic import model_validator

from opsml.helpers.utils import OpsmlImportExceptions, get_class_name
from opsml.model.interfaces.base import (
    SamplePrediction,
    get_model_args,
    get_processor_name,
)
from opsml.model.interfaces.pytorch import TorchModel
from opsml.types import CommonKwargs, Suffix, TorchOnnxArgs, TrainedModelType

try:
    from lightning import LightningModule, Trainer

    class LightningModel(TorchModel):
        """Model interface for Pytorch Lightning models.

        Args:
            model:
                Torch lightning model
            preprocessor:
                Optional preprocessor
            sample_data:
                Sample data to be used for type inference.
                This should match exactly what the model expects as input.
            task_type:
                Task type for model. Defaults to undefined.
            model_type:
                Optional model type. This is inferred automatically.
            preprocessor_name:
                Optional preprocessor. This is inferred automatically if a
                preprocessor is provided.

        Returns:
        LightningModel
        """

        model: Optional[Trainer] = None  # type: ignore[assignment]
        onnx_args: Optional[TorchOnnxArgs] = None

        @property
        def model_class(self) -> str:
            return TrainedModelType.PYTORCH_LIGHTNING.value

        @model_validator(mode="before")
        @classmethod
        def check_model(cls, model_args: Dict[str, Any]) -> Dict[str, Any]:
            model = model_args.get("model")

            if model_args.get("modelcard_uid", False):
                return model_args

            model, module, bases = get_model_args(model)

            if "lightning.pytorch" in module:
                model_args[CommonKwargs.MODEL_TYPE.value] = model.model.__class__.__name__

            for base in bases:
                if "lightning.pytorch" in base:
                    model_args[CommonKwargs.MODEL_TYPE.value] = "subclass"

            sample_data = cls._get_sample_data(sample_data=model_args[CommonKwargs.SAMPLE_DATA.value])
            model_args[CommonKwargs.SAMPLE_DATA.value] = sample_data
            model_args[CommonKwargs.DATA_TYPE.value] = get_class_name(sample_data)
            model_args[CommonKwargs.PREPROCESSOR_NAME.value] = get_processor_name(
                model_args.get(CommonKwargs.PREPROCESSOR.value),
            )

            return model_args

        def get_sample_prediction(self) -> SamplePrediction:
            assert self.model is not None, "Trainer is not defined"
            assert self.sample_data is not None, "Sample data must be provided"

            trainer_model = self.model.model
            assert trainer_model is not None, "No model provided to trainer"

            # test dict input
            if isinstance(self.sample_data, dict):
                try:
                    prediction = trainer_model(**self.sample_data)
                except Exception as _:  # pylint: disable=broad-except
                    prediction = trainer_model(self.sample_data)

            # test list and tuple inputs
            elif isinstance(self.sample_data, (list, tuple)):
                try:
                    prediction = trainer_model(*self.sample_data)
                except Exception as _:  # pylint: disable=broad-except
                    prediction = trainer_model(self.sample_data)

            # all others
            else:
                prediction = trainer_model(self.sample_data)

            prediction_type = get_class_name(prediction)

            return SamplePrediction(prediction_type, prediction)

        def save_model(self, path: Path) -> None:
            assert self.model is not None, "No model detected in interface"
            self.model.save_checkpoint(path)

        def load_model(self, path: Path, **kwargs: Any) -> None:
            """Load lightning model from path"""

            model_arch = kwargs.get(CommonKwargs.MODEL_ARCH.value)

            try:
                if model_arch is not None:
                    # attempt to load checkpoint into model
                    assert issubclass(
                        model_arch, LightningModule
                    ), "Model architecture must be a subclass of LightningModule"
                    self.model = model_arch.load_from_checkpoint(checkpoint_path=path, **kwargs)

                else:
                    # load via torch
                    import torch

                    self.model = torch.load(path)

            except Exception as exc:
                raise ValueError(f"Unable to load pytorch lightning model: {exc}") from exc

        def convert_to_onnx(self, **kwargs: Path) -> None:
            """Converts model to onnx"""
            # import packages for onnx conversion
            OpsmlImportExceptions.try_torchonnx_imports()

            if self.onnx_model is not None:
                return None

            from opsml.model.onnx.torch_converter import _PyTorchLightningOnnxModel

            path: Optional[Path] = kwargs.get("path")
            if path is None:
                return self._convert_to_onnx_inplace()

            self.onnx_model = _PyTorchLightningOnnxModel(self).convert_to_onnx(**{"path": path})
            return None

        @property
        def model_suffix(self) -> str:
            """Returns suffix for storage"""
            return Suffix.CKPT.value

        @staticmethod
        def name() -> str:
            return LightningModel.__name__

except ModuleNotFoundError:
    from opsml.model.interfaces.backups import LightningModelNoModule as LightningModel
