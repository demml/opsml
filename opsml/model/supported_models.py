from typing import Any, Union, Optional, Dict
import pandas as pd
import polars as pl
from numpy.typing import NDArray
from pydantic import BaseModel, ConfigDict, field_validator
from opsml.model.utils.types import TrainedModelType, ValidModelInput


class SupportedModel(BaseModel):
    model: Any
    preprocessor: Any
    sample_data: ValidModelInput
    task_type: str = "undefined"

    model_config = ConfigDict(protected_namespaces=("protect_",))

    @field_validator("sample_data", mode="before")
    @classmethod
    def get_sample_data(
        cls, sample_data: ValidModelInput
    ) -> Optional[Union[str, pd.DataFrame, NDArray[Any], Dict[str, NDArray[Any]]]]:
        """Check sample data and returns one record to be used
        during type inference and ONNX conversion/validation

        Returns:
            Sample data with only one record
        """
        if isinstance(sample_data, str):
            return sample_data

        if not isinstance(sample_data, dict):
            if isinstance(sample_data, pl.DataFrame):
                sample_data = sample_data.to_pandas()

            return sample_data[0:1]

        sample_dict = {}
        if isinstance(sample_data, dict):
            for key, value in sample_data.items():
                if hasattr(value, "shape"):
                    if len(value.shape) > 1:
                        sample_dict[key] = value[0:1]
                else:
                    raise ValueError(
                        """Provided sample data is not a valid type. 
                        Must be a dictionary of numpy, torch, or tensorflow tensors."""
                    )

            return sample_dict

        raise ValueError("Provided sample data is not a valid type")

    @property
    def model_type(self) -> str:
        raise NotImplementedError


class SklearnModel(SupportedModel):
    @property
    def model_type(self) -> str:
        return TrainedModelType.SKLEARN_ESTIMATOR.value


class TensorflowModel(SupportedModel):
    @property
    def model_type(self) -> str:
        return TrainedModelType.TF_KERAS.value


class PytorchModel(SupportedModel):
    @property
    def model_type(self) -> str:
        return TrainedModelType.PYTORCH.value


class LightningModel(SupportedModel):
    @property
    def model_type(self) -> str:
        return TrainedModelType.PYTORCH_LIGHTNING.value


class XGBoostModel(SupportedModel):
    @property
    def model_type(self) -> str:
        return TrainedModelType.SKLEARN_ESTIMATOR.value


class LightGBMBoosterModel(SupportedModel):
    """LightGBM Booster model class. If using the sklearn API, use SklearnModel instead."""

    @field_validator("model", mode="before")
    @classmethod
    def check_model_name(cls, model: Any) -> Any:
        if "sklearn" in model.__module_.lower():
            raise ValueError("Sklearn flavor of LightGBM model is not supported. Use SklearnModel instead.")

        model_bases = [str(base) for base in model.__class__.__bases__]
        for base in model_bases:
            if "sklearn" in base:
                raise ValueError("Sklearn flavor of LightGBM model is not supported. Use SklearnModel instead.")
        return model

    @property
    def model_type(self) -> str:
        return TrainedModelType.LGBM_BOOSTER.value


class HuggingfaceModel(SupportedModel):
    is_pipeline: bool = False

    @property
    def model_type(self) -> str:
        return TrainedModelType.TRANSFORMERS.value


SUPPORTED_MODELS = Union[
    SklearnModel,
    TensorflowModel,
    PytorchModel,
    LightningModel,
    XGBoostModel,
    LightGBMBoosterModel,
    HuggingfaceModel,
]
