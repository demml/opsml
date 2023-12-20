from dataclasses import dataclass
from typing import Any, List, Optional, Tuple

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict

from opsml.helpers.utils import get_class_name
from opsml.registry.types import CommonKwargs


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
    def model_class(self) -> str:
        raise NotImplementedError
