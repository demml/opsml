from typing import Any, Union, Optional, Dict, Tuple, List
from functools import cached_property
import pandas as pd
import polars as pl
from dataclasses import dataclass
from numpy.typing import NDArray
from pydantic import BaseModel, ConfigDict, field_validator, model_validator
from opsml.registry.cards.types import CommonKwargs
from opsml.model.utils.types import TrainedModelType, ValidModelInput, HuggingFaceModuleType
from opsml.model.utils.huggingface_types import HuggingFaceTask, GENERATION_TYPES
from opsml.registry.data.types import get_class_name, AllowedDataType


def get_model_args(model: Any) -> Tuple[Any, str, List[str]]:
    if model is None:
        raise ValueError("Model must be passed to ModelCardValidator when using pytorch lightning models")

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
    sample_data: Optional[ValidModelInput] = None
    task_type: str = CommonKwargs.UNDEFINED.value
    model_type: str

    model_config = ConfigDict(
        protected_namespaces=("protect_",),
        arbitrary_types_allowed=True,
        validate_assignment=False,
        validate_default=True,
    )

    @cached_property
    def data_type(self) -> str:
        return get_class_name(self.sample_data)

    @property
    def supports_onnx(self) -> bool:
        return True

    @cached_property
    def preprocessor_name(self) -> str:
        if self.preprocessor is not None:
            return self.preprocessor.__class__.__name__

        return CommonKwargs.UNDEFINED.value

    @field_validator("sample_data", mode="before")
    @classmethod
    def get_sample_data(
        cls, sample_data: Optional[ValidModelInput] = None
    ) -> Optional[Union[str, pd.DataFrame, NDArray[Any], Dict[str, NDArray[Any]]]]:
        """Check sample data and returns one record to be used
        during type inference and ONNX conversion/validation

        Returns:
            Sample data with only one record
        """
        assert sample_data is not None, "Sample data must be provided"

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


class SklearnModel(SupportedModel):
    @model_validator(mode="before")
    @classmethod
    def check_model(cls, model_args: Dict[str, Any]) -> Dict[str, Any]:
        model = model_args.get("model")

        # passed as extra when modelcard is being loaded
        model_uri = model_args.get("model_uri", False)

        if model_uri:
            return model_args

        model, module, bases = get_model_args(model)

        from sklearn.base import BaseEstimator

        assert isinstance(model, BaseEstimator), "Model must be a sklearn estimator"

        if "sklearn" in module:
            model_args[CommonKwargs.MODEL_TYPE.value] = model.__class__.__name__

        for base in bases:
            if "sklearn" in base:
                model_args[CommonKwargs.MODEL_TYPE.value] = "subclass"

        return model_args

    @property
    def model_class(self) -> str:
        return TrainedModelType.SKLEARN_ESTIMATOR.value


class TensorflowModel(SupportedModel):
    @model_validator(mode="before")
    @classmethod
    def check_model(cls, model_args: Dict[str, Any]) -> Dict[str, Any]:
        model = model_args.get("model")

        # passed as extra when modelcard is being loaded
        model_uri = model_args.get("model_uri", False)

        if model_uri:
            return model_args

        model, module, bases = get_model_args(model)

        import tensorflow as tf

        assert isinstance(model, tf.keras.Model), "Model must be a tensorflow keras model"

        if "keras" in module:
            model_args[CommonKwargs.MODEL_TYPE.value] = model.__class__.__name__

        for base in bases:
            if "keras" in base:
                model_args[CommonKwargs.MODEL_TYPE.value] = "subclass"

        return model

    @property
    def model_class(self) -> str:
        return TrainedModelType.TF_KERAS.value


class PytorchModel(SupportedModel):
    @model_validator(mode="before")
    @classmethod
    def check_model(cls, model_args: Dict[str, Any]) -> Dict[str, Any]:
        model = model_args.get("model")

        # passed as extra when modelcard is being loaded
        model_uri = model_args.get("model_uri", False)

        if model_uri:
            return model_args

        model, _, bases = get_model_args(model)

        from torch.nn import Module

        assert isinstance(model, Module), "Model must be a pytorch model"

        for base in bases:
            if "torch" in base:
                model_args[CommonKwargs.MODEL_TYPE.value] = model.__class__.__name__

        return model

    def get_sample_prediction(self) -> SamplePrediction:
        assert self.sample_data is not None, "Sample data must be provided"

        if self.data_type in [AllowedDataType.DICT, AllowedDataType.TRANSFORMER_BATCH]:
            prediction = self.model(**self.sample_data)
        else:
            prediction = self.model(self.sample_data)

        prediction_type = get_class_name(prediction)

        return SamplePrediction(prediction_type, prediction)

    @property
    def model_class(self) -> str:
        return TrainedModelType.PYTORCH.value


class LightningModel(PytorchModel):
    @model_validator(mode="before")
    @classmethod
    def check_model(cls, model_args: Dict[str, Any]) -> Dict[str, Any]:
        model = model_args.get("model")

        # passed as extra when modelcard is being loaded
        model_uri = model_args.get("model_uri", False)

        if model_uri:
            return model_args

        model, module, bases = get_model_args(model)

        from pytorch_lightning import Trainer

        assert isinstance(model, Trainer), "Model must be a pytorch lightning trainer"

        if "lightning.pytorch" in module:
            model_args[CommonKwargs.MODEL_TYPE.value] = model.model.__class__.__name__

        for base in bases:
            if "lightning.pytorch" in base:
                model_args[CommonKwargs.MODEL_TYPE.value] = "subclass"

        return model

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
        model = model_args.get("model")

        # passed as extra when modelcard is being loaded
        model_uri = model_args.get("model_uri", False)

        if model_uri:
            return model_args

        model, module, _ = get_model_args(model)

        from lightgbm import Booster

        assert isinstance(model, Booster), "Model must be a lightgbm booster. If using the sklearn API, use SklearnModel instead."

        if "lightgbm" in module:
            model_args[CommonKwargs.MODEL_TYPE.value] = model.__class__.__name__

        return model

    @property
    def supports_onnx(self) -> bool:
        return False

    @property
    def model_class(self) -> str:
        return TrainedModelType.LGBM_BOOSTER.value


class HuggingFaceModel(SupportedModel):
    is_pipeline: bool = False
    backend: str

    @model_validator(mode="before")
    @classmethod
    def check_model(cls, model_args: Dict[str, Any]) -> Dict[str, Any]:
        model = model_args.get("model")

        # passed as extra when modelcard is being loaded
        model_uri = model_args.get("model_uri", False)

        if model_uri:
            return model_args

        model, module, bases = get_model_args(model)

        if model_args.get(CommonKwargs.IS_PIPELINE):
            from transformers import Pipeline

            assert isinstance(model, Pipeline), "Model must be a huggingface pipeline"

        else:
            from transformers import PreTrainedModel, TFPreTrainedModel

            if isinstance(model, PreTrainedModel):
                model_args[CommonKwargs.BACKEND.value] = CommonKwargs.PYTORCH.value

            elif isinstance(model, TFPreTrainedModel):
                model_args[CommonKwargs.BACKEND.value] = CommonKwargs.TENSORFLOW.value

            else:
                raise ValueError("Model must be a huggingface model")

        if any(huggingface_module in module for huggingface_module in HuggingFaceModuleType):
            model_args[CommonKwargs.MODEL_TYPE.value] = model.__class__.__name__

        # for subclassed models
        if hasattr(model, "mro"):
            # check bases
            bases = [str(base) for base in model.mro()]
            for base in bases:
                if any(huggingface_module in base for huggingface_module in HuggingFaceModuleType):
                    model_args[CommonKwargs.MODEL_TYPE.value] = "subclass"

        return model_args

    @field_validator("task_type", mode="before")
    @classmethod
    def check_task_type(cls, task_type: str) -> str:
        """Check if task is a huggingface approved task"""

        task = task_type.lower()
        if task not in list(HuggingFaceTask):
            raise ValueError(f"Task type {task} is not supported")
        return task

    def _generate_predictions(self):
        """Use model in generate mode if generate task"""

        assert self.sample_data is not None, "Sample data must be provided"
        if self.data_type in [AllowedDataType.DICT, AllowedDataType.TRANSFORMER_BATCH]:
            return self.model.generate(**self.sample_data)

        return self.generate(self.sample_data)

    def _functional_predictions(self):
        """Use model in functional mode if functional task"""

        assert self.sample_data is not None, "Sample data must be provided"
        if self.data_type in [AllowedDataType.DICT, AllowedDataType.TRANSFORMER_BATCH]:
            return self.model(**self.sample_data)

        return self.model(self.sample_data)

    def _get_pipeline_prediction(self):
        """Use model in pipeline mode if pipeline task"""

        if isinstance(self.sample_data, dict):
            return self.model(**self.sample_data)

        return self.model(self.sample_data)

    def get_sample_prediction(self) -> SamplePrediction:
        if self.is_pipeline:
            prediction = self._get_pipeline_prediction()
        elif self.task_type in GENERATION_TYPES:
            prediction = self._generate_predictions()
        else:
            prediction = self._functional_predictions()

        prediction_type = get_class_name(prediction)

        return SamplePrediction(prediction_type, prediction)

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
