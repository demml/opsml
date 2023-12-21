from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
from numpy.typing import NDArray
from pydantic import model_validator

from opsml.helpers.utils import get_class_name
from opsml.registry.model.interfaces.base import ModelInterface, get_model_args
from opsml.registry.types import CommonKwargs, OnnxModelDefinition, TrainedModelType

try:
    import tensorflow as tf

    ARRAY = Union[NDArray, tf.Tensor]
    VALID_DATA = Union[ARRAY, Dict[str, ARRAY], List[ARRAY], Tuple[ARRAY]]

    class TensorFlowModel(ModelInterface):
        """Model interface for Tensorflow models.

        Args:
            model:
                Tensorflow model
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

        Returns:
            TensorFlowModel
        """

        model: Optional[tf.keras.Model] = None
        sample_data: Optional[VALID_DATA] = None
        onnx_model_def: Optional[OnnxModelDefinition] = None
        model_class: str = TrainedModelType.TF_KERAS.value

        @classmethod
        def get_sample_data(cls, sample_data: Optional[Any] = None) -> Any:
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

            # passed as extra when modelcard is being loaded
            if model_args.get("model_uri", False):
                return model_args

            model, module, bases = get_model_args(model)

            assert isinstance(model, tf.keras.Model), "Model must be a tensorflow keras model"

            if "keras" in module:
                model_args[CommonKwargs.MODEL_TYPE.value] = model.__class__.__name__

            else:
                for base in bases:
                    if "keras" in base:
                        model_args[CommonKwargs.MODEL_TYPE.value] = "subclass"

            sample_data = cls.get_sample_data(sample_data=model_args.get(CommonKwargs.SAMPLE_DATA.value))
            model_args[CommonKwargs.SAMPLE_DATA.value] = sample_data
            model_args[CommonKwargs.DATA_TYPE.value] = get_class_name(sample_data)
            model_args[CommonKwargs.PREPROCESSOR_NAME.value] = cls._get_preprocessor_name(
                preprocessor=model_args.get(CommonKwargs.PREPROCESSOR.value)
            )

            return model_args

except ModuleNotFoundError:

    class TensorFlowModel(ModelInterface):
        @model_validator(mode="before")
        @classmethod
        def check_model(cls, model_args: Dict[str, Any]) -> Dict[str, Any]:
            raise ModuleNotFoundError("TensorFlowModel requires tensorflow to be installed. Please install tensorflow.")
