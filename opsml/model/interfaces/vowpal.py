from pathlib import Path
from typing import Any, Dict, Optional

from pydantic import model_validator

from opsml.helpers.utils import get_class_name
from opsml.model.interfaces.base import ModelInterface
from opsml.types import CommonKwargs, ModelReturn, Suffix, TrainedModelType

try:
    import vowpalwabbit as vw

    class VowpalWabbitModel(ModelInterface):
        """Model interface for VowPal Wabbit model.

        Args:
            model:
                vowpal wabbit workspace
            sample_data:
                Sample data to be used for type inference.
                For vowpal wabbit models this should be a string.
            arguments:
                Vowpal Wabbit arguments. This will be inferred automatically from the workspace

        Returns:
            VowpalWabbitModel
        """

        model: Optional[vw.Workspace] = None
        sample_data: Optional[str] = None
        arguments: str = ""

        @property
        def model_class(self) -> str:
            return TrainedModelType.VOWPAL.value

        @classmethod
        def _get_sample_data(cls, sample_data: str) -> str:
            """Check sample data and returns one record to be used
            during type inference and ONNX conversion/validation.

            Returns:
                Sample data with only one record
            """

            assert isinstance(sample_data, str), "Sample data must be a string"
            return sample_data

        @model_validator(mode="before")
        @classmethod
        def check_model(cls, model_args: Dict[str, Any]) -> Dict[str, Any]:
            model = model_args.get("model")

            if model_args.get("modelcard_uid", False):
                return model_args

            assert model is not None, "Model must not be None"

            sample_data = cls._get_sample_data(sample_data=model_args[CommonKwargs.SAMPLE_DATA.value])
            model_args[CommonKwargs.SAMPLE_DATA.value] = sample_data
            model_args[CommonKwargs.DATA_TYPE.value] = get_class_name(sample_data)
            model_args[CommonKwargs.VOWPAL_ARGS.value] = model.get_arguments()

            return model_args

        def save_model(self, path: Path) -> None:
            """Saves vowpal model to ".model" file.

            Args:
                path:
                    base path to save model to
            """
            assert self.model is not None, "No model found"
            self.model.save(path.as_posix())

        def load_model(self, path: Path, **kwargs: Any) -> None:
            """Loads a vowpal model from ".model" file with arguments.

            Args:
                path:
                    base path to load from
                **kwargs:
                    Additional arguments to be passed to the workspace. This is supplied via
                    "arguments" key.

                    Example:
                        arguments="--cb 4"
                        or
                        arguments=["--cb", "4"]

                    There is no need to specify "-i" argument. This is done automatically during loading.
            """
            args = kwargs.get("arguments", self.arguments)

            if args is None:
                args = self.arguments

            elif isinstance(args, str):
                args = args + f" -i {path.as_posix()}"

            elif isinstance(args, list):
                args.append(f"-i {path.as_posix()}")
                args = " ".join(args)

            else:
                raise ValueError("Arguments must be a string or a list")

            self.model = vw.Workspace(args)

        def save_onnx(self, path: Path) -> ModelReturn:  # pylint: disable=redundant-returns-doc
            """Onnx is not supported for vowpal wabbit models.

            Args:
                path:
                    Path to save

            Returns:
                ModelReturn
            """
            raise ValueError("Onnx is not supported for vowpal wabbit models")

        @property
        def model_suffix(self) -> str:
            """Returns suffix for model storage"""
            return Suffix.MODEL.value

        @staticmethod
        def name() -> str:
            return VowpalWabbitModel.__name__

except ModuleNotFoundError:
    from opsml.model.interfaces.backups import (
        VowpalWabbitModelNoModule as VowpalWabbitModel,
    )
