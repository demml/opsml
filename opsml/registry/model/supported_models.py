from dataclasses import dataclass
from functools import cached_property
from typing import Any, Dict, List, Optional, Tuple, Union

import pandas as pd
import polars as pl
from pydantic import BaseModel, ConfigDict, field_validator, model_validator

from opsml.helpers.utils import get_class_name
from opsml.registry.types import (
    GENERATION_TYPES,
    AllowedDataType,
    CommonKwargs,
    HuggingFaceModuleType,
    HuggingFaceTask,
    TrainedModelType,
)


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
    sample_data: Optional[Any] = None
    task_type: str = CommonKwargs.UNDEFINED.value
    model_type: str = CommonKwargs.UNDEFINED.value
    preprocessor_name: str = CommonKwargs.UNDEFINED.value

    model_config = ConfigDict(
        protected_namespaces=("protect_",),
        arbitrary_types_allowed=True,
        validate_assignment=False,
        validate_default=True,
        extra="allow",
    )

    @cached_property
    def data_type(self) -> str:
        return get_class_name(self.sample_data)

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
    """Model interface for Sklearn models.

    Args:
        model:
            Sklearn model
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
       SklearnModel
    """

    @model_validator(mode="before")
    @classmethod
    def check_model(cls, model_args: Dict[str, Any]) -> Dict[str, Any]:
        model = model_args.get("model")

        # passed as extra when modelcard is being loaded
        if model_args.get("model_uri", False):
            return model_args

        model, module, bases = get_model_args(model)

        from sklearn.base import BaseEstimator

        assert isinstance(model, BaseEstimator), "Model must be an sklearn estimator"

        if "sklearn" in module:
            model_args[CommonKwargs.MODEL_TYPE.value] = model.__class__.__name__

        else:
            for base in bases:
                if "sklearn" in base:
                    model_args[CommonKwargs.MODEL_TYPE.value] = "subclass"

        model_args[CommonKwargs.SAMPLE_DATA.value] = cls.get_sample_data(
            sample_data=model_args.get(CommonKwargs.SAMPLE_DATA.value)
        )
        model_args[CommonKwargs.PREPROCESSOR_NAME.value] = cls._get_preprocessor_name(
            preprocessor=model_args.get(CommonKwargs.PREPROCESSOR.value)
        )

        return model_args

    @property
    def model_class(self) -> str:
        return TrainedModelType.SKLEARN_ESTIMATOR.value


class TensorFlowModel(SupportedModel):
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

    @model_validator(mode="before")
    @classmethod
    def check_model(cls, model_args: Dict[str, Any]) -> Dict[str, Any]:
        model = model_args.get("model")

        # passed as extra when modelcard is being loaded
        if model_args.get("model_uri", False):
            return model_args

        model, module, bases = get_model_args(model)

        import tensorflow as tf

        assert isinstance(model, tf.keras.Model), "Model must be a tensorflow keras model"

        if "keras" in module:
            model_args[CommonKwargs.MODEL_TYPE.value] = model.__class__.__name__

        else:
            for base in bases:
                if "keras" in base:
                    model_args[CommonKwargs.MODEL_TYPE.value] = "subclass"

        model_args[CommonKwargs.SAMPLE_DATA.value] = cls.get_sample_data(
            sample_data=model_args.get(CommonKwargs.SAMPLE_DATA.value)
        )
        model_args[CommonKwargs.PREPROCESSOR_NAME.value] = cls._get_preprocessor_name(
            preprocessor=model_args.get(CommonKwargs.PREPROCESSOR.value)
        )

        return model_args

    @property
    def model_class(self) -> str:
        return TrainedModelType.TF_KERAS.value


class PyTorchModel(SupportedModel):
    """Model interface for Pytorch models.

    Args:
        model:
            Torch model
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
       PyTorchModel
    """

    @model_validator(mode="before")
    @classmethod
    def check_model(cls, model_args: Dict[str, Any]) -> Dict[str, Any]:
        model = model_args.get("model")

        # passed as extra when modelcard is being loaded
        if model_args.get("model_uri", False):
            return model_args

        model, _, bases = get_model_args(model)

        from torch.nn import Module

        assert isinstance(model, Module), "Model must be a pytorch model"

        for base in bases:
            if "torch" in base:
                model_args[CommonKwargs.MODEL_TYPE.value] = model.__class__.__name__

        model_args[CommonKwargs.SAMPLE_DATA.value] = cls.get_sample_data(
            sample_data=model_args.get(CommonKwargs.SAMPLE_DATA.value)
        )
        model_args[CommonKwargs.PREPROCESSOR_NAME.value] = cls._get_preprocessor_name(
            preprocessor=model_args.get(CommonKwargs.PREPROCESSOR.value)
        )

        return model_args

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


class LightningModel(PyTorchModel):
    """Model interface for Pytorch Lightning models.

    Args:
        model:
            Torch lightning model
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
       LightningModel
    """

    @model_validator(mode="before")
    @classmethod
    def check_model(cls, model_args: Dict[str, Any]) -> Dict[str, Any]:
        model = model_args.get("model")

        # passed as extra when modelcard is being loaded
        if model_args.get("model_uri", False):
            return model_args

        model, module, bases = get_model_args(model)

        from lightning import Trainer

        assert isinstance(model, Trainer), "Model must be a pytorch lightning trainer"

        if "lightning.pytorch" in module:
            model_args[CommonKwargs.MODEL_TYPE.value] = model.model.__class__.__name__

        for base in bases:
            if "lightning.pytorch" in base:
                model_args[CommonKwargs.MODEL_TYPE.value] = "subclass"

        model_args[CommonKwargs.SAMPLE_DATA.value] = cls.get_sample_data(
            sample_data=model_args.get(CommonKwargs.SAMPLE_DATA.value)
        )
        model_args[CommonKwargs.PREPROCESSOR_NAME.value] = cls._get_preprocessor_name(
            preprocessor=model_args.get(CommonKwargs.PREPROCESSOR.value)
        )

        return model_args

    def get_sample_prediction(self) -> SamplePrediction:
        assert self.sample_data is not None, "Sample data must be provided"

        from lightning import Trainer

        if not isinstance(self.model, Trainer):
            return super().get_sample_prediction()

        if self.data_type in [AllowedDataType.DICT, AllowedDataType.TRANSFORMER_BATCH]:
            prediction = self.model.model(**self.sample_data)
        else:
            prediction = self.model.model(self.sample_data)

        prediction_type = get_class_name(prediction)

        return SamplePrediction(prediction_type, prediction)

    @property
    def model_class(self) -> str:
        return TrainedModelType.PYTORCH_LIGHTNING.value


class XGBoostModel(SklearnModel):
    """Model interface for XGBoost model class. Currently, only Sklearn flavor of XGBoost
    regressor and classifier are supported.

    Args:
        model:
            XGBoost model
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
        XGBoostModel
    """

    ...


class LightGBMBoosterModel(SupportedModel):
    """Model interface for LightGBM Booster model class. If using the sklearn API, use SklearnModel instead.

    Args:
        model:
            LightGBM booster model
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
        LightGBMBoosterModel
    """

    @model_validator(mode="before")
    @classmethod
    def check_model(cls, model_args: Dict[str, Any]) -> Dict[str, Any]:
        model = model_args.get("model")

        # passed as extra when modelcard is being loaded
        if model_args.get("model_uri", False):
            return model_args

        model, module, _ = get_model_args(model)

        from lightgbm import Booster

        assert isinstance(
            model, Booster
        ), "Model must be a lightgbm booster. If using the sklearn API, use SklearnModel instead."

        if "lightgbm" in module:
            model_args[CommonKwargs.MODEL_TYPE.value] = model.__class__.__name__

        model_args[CommonKwargs.SAMPLE_DATA.value] = cls.get_sample_data(
            sample_data=model_args.get(CommonKwargs.SAMPLE_DATA.value)
        )
        model_args[CommonKwargs.PREPROCESSOR_NAME.value] = cls._get_preprocessor_name(
            preprocessor=model_args.get(CommonKwargs.PREPROCESSOR.value)
        )

        return model_args

    @property
    def supports_onnx(self) -> bool:
        return False

    @property
    def model_class(self) -> str:
        return TrainedModelType.LGBM_BOOSTER.value


class HuggingFaceModel(SupportedModel):
    """Model interface for HuggingFace models

    Args:
        model:
            HuggingFace model
        preprocessor:
            HuggingFace preprocessor
        sample_data:
            Sample data to be used for type inference and ONNX conversion/validation.
            This should match exactly what the model expects as input. See example below.
        task_type:
            Task type for HuggingFace model. See `HuggingFaceTask` for supported tasks.
        model_type:
            Optional model type for HuggingFace model. This is inferred automatically.
        preprocessor_name:
            Optional preprocessor name for HuggingFace model. This is inferred automatically if a
            preprocessor is provided.

    Returns:
        HuggingFaceModel

    Example::

        from transformers import BartModel, BartTokenizer

        tokenizer = BartTokenizer.from_pretrained("facebook/bart-base")
        model = BartModel.from_pretrained("facebook/bart-base")
        inputs = tokenizer(["Hello. How are you"], return_tensors="pt")

        # this is fed to the ModelCard
        model = HuggingFaceModel(
            model=model,
            preprocessor=tokenizer,
            sample_data=inputs,
            task_type=HuggingFaceTask.TEXT_CLASSIFICATION.value,
        )
    """

    is_pipeline: bool = False
    backend: str
    _onnx_model: Optional[Any] = None

    @property
    def onnx_model(self) -> bool:
        """Onnx version of HuggingFace model. This is only available if `to_onnx` is set to True during registration
        or loaded from `onnx_model` method in modelcard"""
        return self._onnx_model

    @onnx_model.setter
    def onnx_model(self, value: Any) -> None:
        self._onnx_model = value

    @classmethod
    def _check_model_backend(cls, model: Any) -> str:
        """Check model backend type for HuggingFace model

        Args:
            model:
                HuggingFace model

        Returns:
            backend name
        """

        from transformers import PreTrainedModel, TFPreTrainedModel

        if isinstance(model, PreTrainedModel):
            return CommonKwargs.PYTORCH.value

        elif isinstance(model, TFPreTrainedModel):
            return CommonKwargs.TENSORFLOW.value

        raise ValueError("Model must be a huggingface model")

    @model_validator(mode="before")
    @classmethod
    def check_model(cls, model_args: Dict[str, Any]) -> Dict[str, Any]:
        # passed as extra when modelcard is being loaded
        if model_args.get("model_uri") is not None:
            return model_args

        hf_model = model_args.get("model")
        hf_model, module, bases = get_model_args(hf_model)

        if model_args.get(CommonKwargs.IS_PIPELINE):
            from transformers import Pipeline

            assert isinstance(hf_model, Pipeline), "Model must be a huggingface pipeline"
            model_args[CommonKwargs.BACKEND.value] = cls._check_model_backend(
                hf_model.model
            )  # hf_model is pipe that has 'model' attr

        else:
            model_args[CommonKwargs.BACKEND.value] = cls._check_model_backend(hf_model)

        if any(huggingface_module in module for huggingface_module in HuggingFaceModuleType):
            model_args[CommonKwargs.MODEL_TYPE.value] = hf_model.__class__.__name__

        # for subclassed models
        if hasattr(hf_model, "mro"):
            # check bases
            bases = [str(base) for base in hf_model.mro()]
            for base in bases:
                if any(huggingface_module in base for huggingface_module in HuggingFaceModuleType):
                    model_args[CommonKwargs.MODEL_TYPE.value] = "subclass"

        model_args[CommonKwargs.SAMPLE_DATA.value] = cls.get_sample_data(
            sample_data=model_args.get(CommonKwargs.SAMPLE_DATA.value)
        )
        model_args[CommonKwargs.PREPROCESSOR_NAME.value] = cls._get_preprocessor_name(
            preprocessor=model_args.get(CommonKwargs.PREPROCESSOR.value)
        )

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

    def _get_pipeline_prediction(self) -> Dict[str, Any]:
        """Use model in pipeline mode if pipeline task"""

        if isinstance(self.sample_data, dict):
            prediction = self.model(**self.sample_data)

        else:
            prediction = self.model(self.sample_data)

        if isinstance(prediction, dict):
            return prediction

        elif isinstance(prediction, list):
            assert len(prediction) >= 1, "Pipeline model must return a prediction"
            return prediction[0]

        raise ValueError("Pipeline model must return a prediction")

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
    TensorFlowModel,
    PyTorchModel,
    LightningModel,
    XGBoostModel,
    LightGBMBoosterModel,
    HuggingFaceModel,
]
