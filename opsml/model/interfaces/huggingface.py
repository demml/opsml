import tempfile
from pathlib import Path
from typing import Any, Dict, Optional, Union, cast

from pydantic import field_validator, model_validator

from opsml.helpers.logging import ArtifactLogger
from opsml.helpers.utils import get_class_name
from opsml.model.interfaces.base import (
    ModelInterface,
    SamplePrediction,
    get_processor_name,
)
from opsml.types import (
    GENERATION_TYPES,
    CommonKwargs,
    HuggingFaceOnnxArgs,
    HuggingFaceTask,
    ModelReturn,
    OnnxModel,
    SaveName,
    TrainedModelType,
)

logger = ArtifactLogger.get_logger()

try:
    import transformers
    from PIL import ImageFile
    from transformers import (
        BatchEncoding,
        BatchFeature,
        FeatureExtractionMixin,
        ImageProcessingMixin,
        Pipeline,
        PreTrainedModel,
        PreTrainedTokenizer,
        PreTrainedTokenizerFast,
        TFPreTrainedModel,
        pipeline,
    )
    from transformers.utils import ModelOutput

    class HuggingFaceModel(ModelInterface):
        """Model interface for HuggingFace models

        Args:
            model:
                HuggingFace model or pipeline
            tokenizer:
                HuggingFace tokenizer. If passing pipeline, tokenizer will be extracted
            feature_extractor:
                HuggingFace feature extractor or image processor. If passing pipeline, feature extractor will be extracted
            sample_data:
                Sample data to be used for type inference.
                This should match exactly what the model expects as input.
            task_type:
                Task type for HuggingFace model. See `HuggingFaceTask` for supported tasks.
            model_type:
                Optional model type for HuggingFace model. This is inferred automatically.
            is_pipeline:
                If model is a pipeline. Defaults to False.
            backend:
                Backend for HuggingFace model. This is inferred from model
            onnx_args:
                Optional arguments for ONNX conversion. See `HuggingFaceOnnxArgs` for supported arguments.
            tokenizer_name:
                Optional tokenizer name for HuggingFace model. This is inferred automatically.
            feature_extractor_name:
                Optional feature_extractor name for HuggingFace model. This is inferred automatically.

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
                tokenizer=tokenizer,
                sample_data=inputs,
                task_type=HuggingFaceTask.TEXT_CLASSIFICATION.value,
            )
        """

        model: Optional[Union[Pipeline, PreTrainedModel, TFPreTrainedModel]] = None
        tokenizer: Optional[Union[PreTrainedTokenizer, PreTrainedTokenizerFast]] = None
        feature_extractor: Optional[Union[FeatureExtractionMixin, ImageProcessingMixin]] = None
        is_pipeline: bool = False
        backend: str = CommonKwargs.PYTORCH.value
        onnx_args: Optional[HuggingFaceOnnxArgs] = None
        tokenizer_name: str = CommonKwargs.UNDEFINED.value
        feature_extractor_name: str = CommonKwargs.UNDEFINED.value

        @classmethod
        def _get_sample_data(cls, sample_data: Any) -> Any:
            """Check sample data and returns one record to be used
            during type inference and ONNX conversion/validation.

            Returns:
                Sample data with only one record
            """

            if isinstance(sample_data, list):
                return [data[0:1] for data in sample_data]

            if isinstance(sample_data, tuple):
                return (data[0:1] for data in sample_data)

            if isinstance(sample_data, (BatchEncoding, BatchFeature, dict)):
                sample_dict = {}
                for key, value in sample_data.items():
                    sample_dict[key] = value[0:1]
                return sample_dict

            if isinstance(sample_data, str):
                return sample_data

            if isinstance(sample_data, ImageFile.ImageFile):
                return sample_data

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

            if isinstance(model, TFPreTrainedModel):
                return CommonKwargs.TENSORFLOW.value

            raise ValueError("Model must be a huggingface model")

        @model_validator(mode="before")
        @classmethod
        def check_model(cls, model_args: Dict[str, Any]) -> Dict[str, Any]:
            if bool(model_args.get("modelcard_uid", False)):
                return model_args

            hf_model = model_args.get("model")
            assert hf_model is not None, "Model is not defined"

            if isinstance(hf_model, Pipeline):
                model_args[CommonKwargs.BACKEND.value] = cls._check_model_backend(hf_model.model)
                model_args[CommonKwargs.IS_PIPELINE.value] = True
                model_args[CommonKwargs.MODEL_TYPE.value] = hf_model.model.__class__.__name__
                model_args[CommonKwargs.TOKENIZER.value] = hf_model.tokenizer
                model_args[CommonKwargs.TOKENIZER_NAME.value] = get_processor_name(hf_model.tokenizer)
                model_args[CommonKwargs.FEATURE_EXTRACTOR.value] = hf_model.feature_extractor
                model_args[CommonKwargs.FEATURE_EXTRACTOR_NAME.value] = get_processor_name(hf_model.feature_extractor)

            else:
                model_args[CommonKwargs.BACKEND.value] = cls._check_model_backend(hf_model)
                model_args[CommonKwargs.IS_PIPELINE.value] = False
                model_args[CommonKwargs.MODEL_TYPE.value] = hf_model.__class__.__name__
                model_args[CommonKwargs.TOKENIZER_NAME.value] = get_processor_name(
                    model_args.get(CommonKwargs.TOKENIZER.value),
                )

                model_args[CommonKwargs.FEATURE_EXTRACTOR_NAME.value] = get_processor_name(
                    model_args.get(CommonKwargs.FEATURE_EXTRACTOR.value)
                )

            sample_data = cls._get_sample_data(sample_data=model_args[CommonKwargs.SAMPLE_DATA.value])

            # set args
            model_args[CommonKwargs.SAMPLE_DATA.value] = sample_data
            model_args[CommonKwargs.DATA_TYPE.value] = get_class_name(sample_data)

            return model_args

        @field_validator("task_type", mode="before")
        @classmethod
        def check_task_type(cls, task_type: str) -> str:
            """Check if task is a huggingface approved task"""

            task = task_type.lower()
            if task not in list(HuggingFaceTask):
                raise ValueError(f"Task type {task} is not supported")
            return task

        # ------------ Model Interface Helper Methods ------------#

        def _generate_predictions(self) -> Any:
            """Use model in generate mode if generate task"""

            assert self.sample_data is not None, "Sample data must be provided"
            assert self.model is not None, "Model must be provided"

            try:  # try generation first , then functional
                if isinstance(self.sample_data, (BatchEncoding, dict)):
                    return self.model.generate(**self.sample_data)

                return self.model.generate(self.sample_data)

            except Exception as _:  # pylint: disable=broad-except
                return self._functional_predictions()

        def _functional_predictions(self) -> Any:
            """Use model in functional mode if functional task"""

            assert self.sample_data is not None, "Sample data must be provided"
            assert self.model is not None, "Model must be provided"

            if isinstance(self.sample_data, (BatchEncoding, dict)):
                return self.model(**self.sample_data)

            return self.model(self.sample_data)

        def _get_pipeline_prediction(self) -> Any:
            """Use model in pipeline mode if pipeline task"""
            assert isinstance(self.model, Pipeline), "Model must be a pipeline"

            if isinstance(self.sample_data, dict):
                prediction = self.model(**self.sample_data)

            else:
                prediction = self.model(self.sample_data)

            if isinstance(prediction, dict):
                return prediction

            if isinstance(prediction, list):
                assert len(prediction) >= 1, "Pipeline model must return a prediction"
                return prediction[0]

            raise ValueError("Pipeline model must return a prediction")

        def get_sample_prediction(self) -> SamplePrediction:
            """Generates prediction from model and provided sample data"""

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

        # ------------ Model Interface Onnx Methods ------------#

        def _quantize_model(self, path: Path, onnx_model: Any) -> None:
            """Quantizes an huggingface model

            Args:
                path:
                    parent path to save too
                onnx_model:
                    onnx model to quantize

            Returns:
                Path to quantized model
            """
            assert self.onnx_args is not None, "No onnx args provided"
            assert self.onnx_args.config is not None, "No quantization config provided"

            logger.info("Quantizing HuggingFace ONNX model")

            from optimum.onnxruntime import ORTQuantizer

            save_path = path / SaveName.QUANTIZED_MODEL.value
            quantizer = ORTQuantizer.from_pretrained(onnx_model)

            quantizer.quantize(save_dir=save_path, quantization_config=self.onnx_args.config)

        def _convert_to_onnx_inplace(self) -> None:
            """Converts model to onnx in place"""

            with tempfile.TemporaryDirectory() as tmpdirname:
                lpath = Path(tmpdirname)
                self.save_model((lpath / SaveName.TRAINED_MODEL.value))

                if self.tokenizer is not None:
                    self.save_tokenizer((lpath / SaveName.TOKENIZER.value))

                if self.feature_extractor is not None:
                    self.save_feature_extractor((lpath / SaveName.FEATURE_EXTRACTOR.value))

                onnx_path = lpath / SaveName.ONNX_MODEL.value
                return self.convert_to_onnx(**{"path": onnx_path})

        def convert_to_onnx(self, **kwargs: Path) -> None:
            """Converts a huggingface model or pipeline to onnx via optimum library.
            Converted model or pipeline is accessible via the `onnx_model` attribute.
            """

            logger.info("Staring conversion of HuggingFace model to ONNX")

            assert (
                self.onnx_args is not None
            ), "No onnx args provided. If converting to onnx, provide a HuggingFaceOnnxArgs instance"

            if self.onnx_model is not None:
                return None

            import onnx
            import optimum.onnxruntime as ort

            path: Optional[Path] = kwargs.get("path")
            if path is None:
                return self._convert_to_onnx_inplace()

            # ensure no suffix (this is an exception to the rule to all model interfaces)
            # huggingface prefers to save onnx models in dirs instead of single model.onnx file
            path = path.with_suffix("")
            ort_model: ort.ORTModel = getattr(ort, self.onnx_args.ort_type)
            model_path = path.parent / SaveName.TRAINED_MODEL.value
            onnx_model = ort_model.from_pretrained(model_path, export=True, provider=self.onnx_args.provider)
            onnx_model.save_pretrained(path)

            if self.is_pipeline:
                self.onnx_model = OnnxModel(
                    onnx_version=onnx.__version__,
                    sess=pipeline(
                        self.task_type,
                        model=onnx_model,
                        tokenizer=self.tokenizer,
                        feature_extractor=self.feature_extractor,
                    ),
                )
            else:
                self.onnx_model = OnnxModel(onnx_version=onnx.__version__, sess=onnx_model)

            if self.onnx_args.quantize:
                self._quantize_model(path.parent, onnx_model)

            return None

        # ------------ Model Interface Save Methods ------------#

        def save_model(self, path: Path) -> None:
            assert self.model is not None, "No model detected in interface"

            if isinstance(self.model, Pipeline):
                self.model.model.save_pretrained(path)
                return None

            self.model.save_pretrained(path)
            return None

        def save_tokenizer(self, path: Path) -> None:
            if self.tokenizer is None:
                return None

            if isinstance(self.model, Pipeline):
                assert self.model.tokenizer is not None, "Tokenizer is missing"
                self.model.tokenizer.save_pretrained(path)
                return None

            self.tokenizer.save_pretrained(path)
            return None

        def save_feature_extractor(self, path: Path) -> None:
            if self.feature_extractor is None:
                return None

            if isinstance(self.model, Pipeline):
                assert self.model.feature_extractor is not None, "Feature extractor is missing"
                self.model.feature_extractor.save_pretrained(path)
                return None

            self.feature_extractor.save_pretrained(path)
            return None

        def save_onnx(self, path: Path) -> ModelReturn:
            import onnxruntime as rt

            from opsml.model.onnx import _get_onnx_metadata

            model_saved = False
            if self.onnx_model is None:
                # HF saves model during conversion
                self.convert_to_onnx(**{"path": path})
                model_saved = True

            assert self.onnx_model is not None, "No onnx model detected in interface"
            if self.is_pipeline:
                if not model_saved:
                    self.onnx_model.sess.model.save_pretrained(path.with_suffix(""))
                return _get_onnx_metadata(self, cast(rt.InferenceSession, self.onnx_model.sess.model.model))

            if not model_saved:
                self.onnx_model.sess.save_pretrained(path.with_suffix(""))

            return _get_onnx_metadata(self, cast(rt.InferenceSession, self.onnx_model.sess.model))

        # ------------ Model Interface Load Methods ------------#

        def load_tokenizer(self, path: Path) -> None:
            self.tokenizer = getattr(transformers, self.tokenizer_name).from_pretrained(path)

        def load_feature_extractor(self, path: Path) -> None:
            self.feature_extractor = getattr(transformers, self.feature_extractor_name).from_pretrained(path)

        def load_model(self, path: Path, **kwargs: Any) -> None:
            """Load huggingface model from path

            Args:
                path:
                    Path to model
                kwargs:
                    Additional kwargs to pass to transformers.load_pretrained
            """
            custom_arch = kwargs.get("custom_architecture")
            if custom_arch is not None:
                assert isinstance(
                    custom_arch, (PreTrainedModel, TFPreTrainedModel)
                ), "Custom architecture must be a huggingface model"
                self.model = custom_arch.from_pretrained(path)

            else:
                self.model = getattr(transformers, self.model_type).from_pretrained(path)

        def to_pipeline(self) -> None:
            """Converts model to pipeline"""

            if isinstance(self.model, Pipeline):
                return None

            pipe = pipeline(
                task=self.task_type,
                model=self.model,
                tokenizer=self.tokenizer,
                feature_extractor=self.feature_extractor,
            )

            self.model = pipe
            self.is_pipeline = True
            return None

        def load_onnx_model(self, path: Path) -> None:
            """Load onnx model from path"""
            import onnx
            import optimum.onnxruntime as ort

            assert self.onnx_args is not None, "No onnx args provided"
            ort_model = getattr(ort, self.onnx_args.ort_type)
            onnx_model = ort_model.from_pretrained(
                path,
                config=self.onnx_args.config,
                provider=self.onnx_args.provider,
            )

            if self.is_pipeline:
                self.onnx_model = OnnxModel(
                    onnx_version=onnx.__version__,  # type: ignore[attr-defined]
                    sess=pipeline(
                        self.task_type,
                        model=onnx_model,
                        tokenizer=self.tokenizer,
                        feature_extractor=self.feature_extractor,
                    ),
                )
            else:
                self.onnx_model = OnnxModel(
                    onnx_version=onnx.__version__,  # type: ignore[attr-defined]
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
    from opsml.model.interfaces.backups import (
        HuggingFaceModelNoModule as HuggingFaceModel,
    )
