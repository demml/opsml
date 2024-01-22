from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import joblib
import numpy as np
from numpy.typing import NDArray
from pydantic import model_validator

from opsml.helpers.utils import get_class_name
from opsml.model.interfaces.base import (
    ModelInterface,
    get_model_args,
    get_processor_name,
)
from opsml.types import CommonKwargs, Suffix, TrainedModelType

try:
    import tensorflow as tf

    ArrayType = Union[NDArray[Any], tf.Tensor]

    class TensorFlowModel(ModelInterface):
        """Model interface for Tensorflow models.

        Args:
            model:
                Tensorflow model
            preprocessor:
                Optional preprocessor
            sample_data:
                Sample data to be used for type inference and ONNX conversion/validation.
                This should match exactly what the model expects as input. ArrayType = Union[NDArray[Any], tf.Tensor]
            task_type:
                Task type for model. Defaults to undefined.
            model_type:
                Optional model type. This is inferred automatically.
            preprocessor_name:
                Optional preprocessor. This is inferred automatically if a
                preprocessor is provided.

        Returns:
            TensorFlowModel
        """

        model: Optional[tf.keras.Model] = None
        sample_data: Optional[Union[ArrayType, Dict[str, ArrayType], List[ArrayType], Tuple[ArrayType]]] = None
        preprocessor: Optional[Any] = None
        preprocessor_name: str = CommonKwargs.UNDEFINED.value

        @property
        def model_class(self) -> str:
            return TrainedModelType.TF_KERAS.value

        @classmethod
        def _get_sample_data(cls, sample_data: Any) -> Any:
            """Check sample data and returns one record to be used
            during type inference and ONNX conversion/validation.

            Returns:
                Sample data with only one record
            """

            if isinstance(sample_data, (np.ndarray, tf.Tensor)):
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

            model, module, bases = get_model_args(model)

            assert isinstance(model, tf.keras.Model), "Model must be a tensorflow keras model"

            if "keras" in module:
                model_args[CommonKwargs.MODEL_TYPE.value] = model.__class__.__name__

            else:
                for base in bases:
                    if "keras" in base:
                        model_args[CommonKwargs.MODEL_TYPE.value] = "subclass"

            sample_data = cls._get_sample_data(sample_data=model_args[CommonKwargs.SAMPLE_DATA.value])
            model_args[CommonKwargs.SAMPLE_DATA.value] = sample_data
            model_args[CommonKwargs.DATA_TYPE.value] = get_class_name(sample_data)
            model_args[CommonKwargs.PREPROCESSOR_NAME.value] = get_processor_name(
                model_args.get(CommonKwargs.PREPROCESSOR.value),
            )

            return model_args

        def save_model(self, path: Path) -> None:
            """Save tensorflow model to path

            Args:
                path:
                    pathlib object
            """
            assert self.model is not None, "Model is not initialized"
            self.model.save(path)

        def load_model(self, path: Path, **kwargs: Any) -> None:
            """Load tensorflow model from path

            Args:
                path:
                    pathlib object
                kwargs:
                    Additional arguments to be passed to load_model
            """
            self.model = tf.keras.models.load_model(path, **kwargs)

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
            return ""

        @staticmethod
        def name() -> str:
            return TensorFlowModel.__name__

except ModuleNotFoundError:
    from opsml.model.interfaces.backups import (
        TensorFlowModelNoModule as TensorFlowModel,
    )
