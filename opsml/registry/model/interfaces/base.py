from dataclasses import dataclass
from typing import Any, List, Optional, Tuple

import pandas as pd
import polars as pl
from pydantic import BaseModel, ConfigDict

from opsml.helpers.utils import get_class_name
from opsml.registry.types import AllowedDataType, CommonKwargs


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


class SupportedModel(BaseModel):
    model: Optional[Any] = None
    preprocessor: Optional[Any] = None
    sample_data: Optional[Any] = None
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
    def supports_onnx(self) -> bool:
        return True

    @classmethod
    def _get_preprocessor_name(cls, preprocessor: Optional[Any] = None) -> str:
        if preprocessor is not None:
            return preprocessor.__class__.__name__

        return CommonKwargs.UNDEFINED.value

    @classmethod
    def get_sample_data(cls, sample_data: Optional[Any] = None) -> Any:
        """Check sample data and returns one record to be used
        during type inference and ONNX conversion/validation.

        Returns:
            Sample data with only one record
        """

        assert sample_data is not None, "Sample data must be provided"
        sample_data_type = get_class_name(sample_data)

        # convert huggingface input if needed
        if sample_data_type == AllowedDataType.TRANSFORMER_BATCH:
            sample_data = dict(sample_data)

        # for array types, only use one sample
        if sample_data_type in [
            AllowedDataType.NUMPY,
            AllowedDataType.TENSORFLOW_TENSOR,
            AllowedDataType.TORCH_TENSOR,
        ]:
            return sample_data[0:1]

        if isinstance(sample_data, str):
            return sample_data

        # get sample for pandas or polars dataframes
        if isinstance(sample_data, (pl.DataFrame, pd.DataFrame)):
            if isinstance(sample_data, pl.DataFrame):
                sample_data = sample_data.to_pandas()

            return sample_data[0:1]

        sample_dict = {}
        if isinstance(sample_data, dict):
            for key, value in sample_data.items():
                if hasattr(value, "shape"):
                    if len(value.shape) > 1:  # validate one sample for array types
                        sample_dict[key] = value[0:1]
                else:
                    sample_dict[key] = value

            return sample_dict

        raise ValueError(f"Provided sample data is not a valid type. Received {sample_data_type}")

    def get_sample_prediction(self) -> SamplePrediction:
        prediction = self.model.predict(self.sample_data)
        prediction_type = get_class_name(prediction)

        return SamplePrediction(
            prediction_type,
            prediction,
        )

    @property
    def model_class(self) -> str:
        raise NotImplementedError
