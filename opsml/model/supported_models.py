from typing import Any, List
from pydantic import BaseModel, ConfigDict, field_validator
from opsml.model.utils.types import TrainedModelType, ValidModelInput


class SupportedModel(BaseModel):
    model: Any
    preprocessor: Any
    sample_data: ValidModelInput

    model_config = ConfigDict(protected_namespaces=("protect_",))

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
    task_type: str
    is_pipeline: bool = False

    @property
    def model_type(self) -> str:
        return TrainedModelType.TRANSFORMERS.value


SUPPORTED_MODELS = List[
    SklearnModel,
    TensorflowModel,
    PytorchModel,
    LightningModel,
    XGBoostModel,
    LightGBMBoosterModel,
    HuggingfaceModel,
]
