from typing import Any, Dict, Optional, Union

from pydantic import field_validator, model_validator

from opsml.helpers.utils import get_class_name
from opsml.registry.model.interfaces.base import SamplePrediction, ModelInterface
from opsml.registry.types import (
    GENERATION_TYPES,
    CommonKwargs,
    HuggingFaceOnnxArgs,
    HuggingFaceTask,
    TrainedModelType,
)

try:
    from transformers import BatchEncoding, Pipeline, PreTrainedModel, TFPreTrainedModel
    from transformers.utils import ModelOutput

    class HuggingFaceModel(ModelInterface):
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
            is_pipeline:
                If model is a pipeline. Defaults to False.
            backend:
                Backend for HuggingFace model. This is inferred from model
            onnx_args:
                Optional arguments for ONNX conversion. See `HuggingFaceOnnxArgs` for supported arguments.

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

        model: Optional[Union[Pipeline, PreTrainedModel, TFPreTrainedModel]] = None
        is_pipeline: bool = False
        backend: str
        onnx_args: Optional[HuggingFaceOnnxArgs] = None
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
                sample_dict = {}
                for key, value in sample_data.items():
                    sample_dict[key] = value[0:1]
                return sample_dict

            return sample_data[0:1]

        @classmethod
        def _check_model_backend(cls, model: Any) -> str:
            """Check model backend type for HuggingFace model

            Args:
                model:
                    HuggingFace model

            Returns:
                backend name
            """

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
            assert hf_model is not None, "Model is not defined"

            if isinstance(hf_model, Pipeline):
                model_args[CommonKwargs.BACKEND.value] = cls._check_model_backend(hf_model.model)
                model_args[CommonKwargs.IS_PIPELINE.value] = True

            else:
                model_args[CommonKwargs.BACKEND.value] = cls._check_model_backend(hf_model)
                model_args[CommonKwargs.IS_PIPELINE.value] = False

            sample_data = cls.get_sample_data(sample_data=model_args.get(CommonKwargs.SAMPLE_DATA.value))

            # set args
            model_args[CommonKwargs.MODEL_TYPE.value] = hf_model.__class__.__name__
            model_args[CommonKwargs.SAMPLE_DATA.value] = sample_data
            model_args[CommonKwargs.DATA_TYPE.value] = get_class_name(sample_data)
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
            assert self.model is not None, "Model must be provided"

            if isinstance(self.sample_data, (BatchEncoding, dict)):
                return self.model.generate(**self.sample_data)

            return self.generate(self.sample_data)

        def _functional_predictions(self):
            """Use model in functional mode if functional task"""

            assert self.sample_data is not None, "Sample data must be provided"
            assert self.model is not None, "Model must be provided"

            if isinstance(self.sample_data, (BatchEncoding, dict)):
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

            if isinstance(prediction, ModelOutput):
                prediction = dict(prediction)

            prediction_type = get_class_name(prediction)

            return SamplePrediction(prediction_type, prediction)

        @property
        def model_class(self) -> str:
            return TrainedModelType.TRANSFORMERS.value

except ModuleNotFoundError:

    class HuggingFaceModel(ModelInterface):
        @model_validator(mode="before")
        @classmethod
        def check_model(cls, model_args: Dict[str, Any]) -> Dict[str, Any]:
            raise ModuleNotFoundError("HuggingFaceModel requires transformers to be installed. Please install transformers.")
