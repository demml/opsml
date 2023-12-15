from typing import Any, Union, Optional, Dict, Tuple, List
import pandas as pd
import polars as pl
from numpy.typing import NDArray
from pydantic import BaseModel, ConfigDict, field_validator, model_validator
from opsml.model.utils.types import TrainedModelType, ValidModelInput, HuggingFaceModuleType


def get_model_args(model_args: Dict[str, Any]) -> Tuple[Any, str, List[str]]:
    model = model_args.get("model")

    if model is None:
        raise ValueError("Model must be passed to ModelCardValidator when using pytorch lightning models")

    model_module = model.__module__
    model_bases = [str(base) for base in model.__class__.__bases__]

    return model, model_module, model_bases


class SupportedModel(BaseModel):
    model: Any
    preprocessor: Any
    sample_data: ValidModelInput
    task_type: str = "undefined"
    model_type: str

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
    def model_class(self) -> str:
        raise NotImplementedError


class SklearnModel(SupportedModel):
    @model_validator(mode="before")
    @classmethod
    def check_model(cls, model_args: Dict[str, Any]) -> Dict[str, Any]:
        model, module, bases = get_model_args(model_args)

        if "sklearn" in module:
            model_args["model_type"] = model.__class__.__name__

        for base in bases:
            if "sklearn" in base:
                model_args["model_type"] = "subclass"

        return model_args

    @property
    def model_class(self) -> str:
        return TrainedModelType.SKLEARN_ESTIMATOR.value


class TensorflowModel(SupportedModel):
    @model_validator(mode="before")
    @classmethod
    def check_model(cls, model_args: Dict[str, Any]) -> Dict[str, Any]:
        model, module, bases = get_model_args(model_args)

        if "keras" in module:
            model_args["model_type"] = model.__class__.__name__

        for base in bases:
            if "keras" in base:
                model_args["model_type"] = "subclass"

        return model_args

    @property
    def model_class(self) -> str:
        return TrainedModelType.TF_KERAS.value


class PytorchModel(SupportedModel):
    @model_validator(mode="before")
    @classmethod
    def check_model(cls, model_args: Dict[str, Any]) -> Dict[str, Any]:
        model, _, bases = get_model_args(model_args)

        for base in bases:
            if "torch" in base:
                model_args["model_type"] = model.__class__.__name__

        return model_args

    @property
    def model_class(self) -> str:
        return TrainedModelType.PYTORCH.value


class LightningModel(SupportedModel):
    @model_validator(mode="before")
    @classmethod
    def check_model(cls, model_args: Dict[str, Any]) -> Dict[str, Any]:
        model, module, bases = get_model_args(model_args)

        if "lightning.pytorch" in module:
            if "trainer" not in module:
                raise ValueError("Trainer must be passed to ModelCardValidator when using pytorch lightning models")
            model_args["model_type"] = model.__class__.__name__

        for base in bases:
            if "lightning.pytorch" in base:
                if "trainer" not in base:
                    raise ValueError("Trainer must be passed to ModelCardValidator when using pytorch lightning models")
                model_args["model_type"] = "subclass"

        return model_args

    @property
    def model_class(self) -> str:
        return TrainedModelType.PYTORCH_LIGHTNING.value


class XGBoostModel(SklearnModel):
    ...


class LightGBMBoosterModel(SupportedModel):
    """LightGBM Booster model class. If using the sklearn API, use SklearnModel instead."""

    @model_validator(mode="before")
    @classmethod
    def check_model(cls, model_args: Dict[str, Any]) -> Dict[str, Any]:
        model, module, _ = get_model_args(model_args)

        if "lightgbm" in module:
            model_args["model_type"] = model.__class__.__name__

        return model_args

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
    def model_class(self) -> str:
        return TrainedModelType.LGBM_BOOSTER.value


class HuggingFaceModel(SupportedModel):
    is_pipeline: bool = False

    @model_validator(mode="before")
    @classmethod
    def check_model(cls, model_args: Dict[str, Any]) -> Dict[str, Any]:
        model, module, bases = get_model_args(model_args)

        if any(huggingface_module in module for huggingface_module in HuggingFaceModuleType):
            model_args["model_type"] = model.__class__.__name__

        # for subclassed models
        if hasattr(model, "mro"):
            # check for mro
            bases = [str(base) for base in model.mro()]
            for base in bases:
                if any(huggingface_module in base for huggingface_module in HuggingFaceModuleType):
                    model_args["model_type"] = "subclass"

        return model_args

    @property
    def model_class(self) -> str:
        return TrainedModelType.TRANSFORMERS.value


SUPPORTED_MODELS = Union[
    SklearnModel,
    TensorflowModel,
    PytorchModel,
    LightningModel,
    XGBoostModel,
    LightGBMBoosterModel,
    HuggingFaceModel,
]
