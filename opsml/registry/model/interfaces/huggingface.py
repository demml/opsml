from pathlib import Path
from typing import Any, Dict, Optional, Tuple, Union, cast

from pydantic import field_validator, model_validator

from opsml.helpers.utils import get_class_name
from opsml.registry.model.interfaces.base import ModelInterface, SamplePrediction
from opsml.registry.types import (
    GENERATION_TYPES,
    CommonKwargs,
    HuggingFaceOnnxArgs,
    HuggingFaceTask,
    ModelReturn,
    OnnxModel,
    SaveName,
    TrainedModelType,
)

try:
    import transformers
    from transformers import (
        BatchEncoding,
        Pipeline,
        PreTrainedModel,
        TFPreTrainedModel,
        pipeline,
    )
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
            if model_args.get("modelcard_uid", False):
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

        def save_model(self, path: Path) -> Path:
            assert self.model is not None, "No model detected in interface"
            self.model.save_pretrained(path)
            return path

        def save_preprocessor(self, path: Path) -> Path:
            assert self.preprocessor is not None, "No preprocessor detected in interface"
            self.preprocessor.save_pretrained(path)
            return path

        def convert_to_onnx(self, path: Path) -> Tuple[ModelReturn, Path]:
            """Converts a huggingface model or pipeline to onnx via optimum library.
            Converted model or pipeline is accessible via the `onnx_model` attribute.


            Args:
                path:
                    Path to save onnx model. This path will be path to onnx file
            """
            import onnx
            import onnxruntime as rt
            import optimum.onnxruntime as ort

            from opsml.registry.model.model_converters import _get_onnx_metadata

            ort_model: ort.ORTModel = getattr(ort, self.onnx_args.ort_type)
            model_path = path.parent / SaveName.TRAINED_MODEL
            onnx_model = ort_model.from_pretrained(
                model_path,
                export=True,
                config=self.onnx_args.config,
                provider=self.onnx_args.provider,
            )
            onnx_model.save_pretrained(path)

            if self.is_pipeline:
                from transformers import pipeline

                self.onnx_model = OnnxModel(
                    onnx_version=onnx.__version__,
                    sess=pipeline(
                        self.task_type,
                        model=onnx_model,
                        tokenizer=self.preprocessor,
                    ),
                )
            else:
                self.onnx_model = OnnxModel(onnx_version=onnx.__version__, sess=onnx_model)

            return _get_onnx_metadata(self, cast(rt.InferenceSession, onnx_model.model)), path

        def load_preprocessor(self, path: Path) -> None:
            self.preprocessor = getattr(transformers, self.preprocessor_name).from_pretrained(path)

        def load_model(self, path: Path, **kwargs) -> None:
            """Load huggingface model from path"""

            if self.is_pipeline:
                self.model = transformers.pipeline(self.task_type, path)
            else:
                self.model = getattr(transformers, self.model_type).from_pretrained(path)

        def load_onnx_model(self, path: Path) -> None:
            """Load onnx model from path"""
            import onnx
            import optimum.onnxruntime as ort

            ort_model = getattr(ort, self.onnx_args.ort_type)
            onnx_model = ort_model.from_pretrained(
                path,
                config=self.onnx_args.config,
                provider=self.onnx_args.provider,
            )

            if self.is_pipeline:
                self.onnx_model = OnnxModel(
                    onnx_version=onnx.__version__,
                    sess=pipeline(
                        self.task_type,
                        model=onnx_model,
                        tokenizer=self.preprocessor,
                    ),
                )
            else:
                self.onnx_model = OnnxModel(
                    onnx_version=onnx.__version__,
                    sess=onnx_model,
                )

        @property
        def model_class(self) -> str:
            return TrainedModelType.TRANSFORMERS.value

        @property
        def model_suffix(self) -> str:
            """Returns suffix for storage"""
            return ""

        @staticmethod
        def name() -> str:
            return HuggingFaceModel.__name__

except ModuleNotFoundError:

    class HuggingFaceModel(ModelInterface):
        @model_validator(mode="before")
        @classmethod
        def check_model(cls, model_args: Dict[str, Any]) -> Dict[str, Any]:
            raise ModuleNotFoundError(
                "HuggingFaceModel requires transformers to be installed. Please install transformers."
            )

        @staticmethod
        def name() -> str:
            return HuggingFaceModel.__name__
