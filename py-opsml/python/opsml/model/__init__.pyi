# pylint: disable=dangerous-default-value, arguments-renamed

from pathlib import Path
from typing import Any, Dict, List, Optional, Union, overload

from ..core import ExtraMetadata, FeatureSchema, OnnxSchema
from ..data import DataType
from ..scouter.drift import (
    CustomDriftProfile,
    CustomMetric,
    CustomMetricDriftConfig,
    PsiDriftConfig,
    PsiDriftProfile,
    SpcDriftConfig,
    SpcDriftProfile,
)

class ModelSaveKwargs:
    def __init__(
        self,
        onnx: Optional[Dict | HuggingFaceOnnxArgs] = None,
        model: Optional[Dict] = None,
        preprocessor: Optional[Dict] = None,
    ) -> None:
        """Optional arguments to pass to save_model

        Args:
            onnx (Dict or HuggingFaceOnnxArgs):
                Optional onnx arguments to use when saving model to onnx format
            model (Dict):
                Optional model arguments to use when saving
            preprocessor (Dict):
                Optional preprocessor arguments to use when saving
        """

    def __str__(self): ...
    def model_dump_json(self) -> str: ...
    @staticmethod
    def model_validate_json(json_string: str) -> "ModelSaveKwargs": ...

class ModelLoadKwargs:
    onnx: Optional[Dict]
    model: Optional[Dict]
    preprocessor: Optional[Dict]

    def __init__(
        self,
        onnx: Optional[Dict] = None,
        model: Optional[Dict] = None,
        preprocessor: Optional[Dict] = None,
    ) -> None:
        """Optional arguments to pass to load_model

        Args:
            onnx (Dict):
                Optional onnx arguments to use when loading
            model (Dict):
                Optional model arguments to use when loading
            preprocessor (Dict):
                Optional preprocessor arguments to use when loading
        """

class ModelType:
    Transformers: "ModelType"
    SklearnPipeline: "ModelType"
    SklearnEstimator: "ModelType"
    StackingRegressor: "ModelType"
    StackingClassifier: "ModelType"
    StackingEstimator: "ModelType"
    CalibratedClassifier: "ModelType"
    LgbmRegressor: "ModelType"
    LgbmClassifier: "ModelType"
    XgbRegressor: "ModelType"
    XgbClassifier: "ModelType"
    XgbBooster: "ModelType"
    LgbmBooster: "ModelType"
    TfKeras: "ModelType"
    Pytorch: "ModelType"
    PytorchLightning: "ModelType"
    Catboost: "ModelType"
    Vowpal: "ModelType"
    Unknown: "ModelType"

class HuggingFaceORTModel:
    OrtAudioClassification: "HuggingFaceORTModel"
    OrtAudioFrameClassification: "HuggingFaceORTModel"
    OrtAudioXVector: "HuggingFaceORTModel"
    OrtCustomTasks: "HuggingFaceORTModel"
    OrtCtc: "HuggingFaceORTModel"
    OrtFeatureExtraction: "HuggingFaceORTModel"
    OrtImageClassification: "HuggingFaceORTModel"
    OrtMaskedLm: "HuggingFaceORTModel"
    OrtMultipleChoice: "HuggingFaceORTModel"
    OrtQuestionAnswering: "HuggingFaceORTModel"
    OrtSemanticSegmentation: "HuggingFaceORTModel"
    OrtSequenceClassification: "HuggingFaceORTModel"
    OrtTokenClassification: "HuggingFaceORTModel"
    OrtSeq2SeqLm: "HuggingFaceORTModel"
    OrtSpeechSeq2Seq: "HuggingFaceORTModel"
    OrtVision2Seq: "HuggingFaceORTModel"
    OrtPix2Struct: "HuggingFaceORTModel"
    OrtCausalLm: "HuggingFaceORTModel"
    OrtOptimizer: "HuggingFaceORTModel"
    OrtQuantizer: "HuggingFaceORTModel"
    OrtTrainer: "HuggingFaceORTModel"
    OrtSeq2SeqTrainer: "HuggingFaceORTModel"
    OrtTrainingArguments: "HuggingFaceORTModel"
    OrtSeq2SeqTrainingArguments: "HuggingFaceORTModel"
    OrtStableDiffusionPipeline: "HuggingFaceORTModel"
    OrtStableDiffusionInpaintPipeline: "HuggingFaceORTModel"
    OrtStableDiffusionXlPipeline: "HuggingFaceORTModel"
    OrtStableDiffusionXlImg2ImgPipeline: "HuggingFaceORTModel"
    OrtStableDiffusionImg2ImgPipeline: "HuggingFaceORTModel"

class HuggingFaceTask:
    AudioClassification: "HuggingFaceTask"
    AutomaticSpeechRecognition: "HuggingFaceTask"
    Conversational: "HuggingFaceTask"
    DepthEstimation: "HuggingFaceTask"
    DocumentQuestionAnswering: "HuggingFaceTask"
    FeatureExtraction: "HuggingFaceTask"
    FillMask: "HuggingFaceTask"
    ImageClassification: "HuggingFaceTask"
    ImageSegmentation: "HuggingFaceTask"
    ImageToImage: "HuggingFaceTask"
    ImageToText: "HuggingFaceTask"
    MaskGeneration: "HuggingFaceTask"
    ObjectDetection: "HuggingFaceTask"
    QuestionAnswering: "HuggingFaceTask"
    Summarization: "HuggingFaceTask"
    TableQuestionAnswering: "HuggingFaceTask"
    Text2TextGeneration: "HuggingFaceTask"
    TextClassification: "HuggingFaceTask"
    TextGeneration: "HuggingFaceTask"
    TextToAudio: "HuggingFaceTask"
    TokenClassification: "HuggingFaceTask"
    Translation: "HuggingFaceTask"
    TranslationXxToYy: "HuggingFaceTask"
    VideoClassification: "HuggingFaceTask"
    VisualQuestionAnswering: "HuggingFaceTask"
    ZeroShotClassification: "HuggingFaceTask"
    ZeroShotImageClassification: "HuggingFaceTask"
    ZeroShotAudioClassification: "HuggingFaceTask"
    ZeroShotObjectDetection: "HuggingFaceTask"
    Undefined: "HuggingFaceTask"

class HuggingFaceOnnxArgs:
    ort_type: HuggingFaceORTModel
    provider: str
    quantize: bool
    export: bool
    config: Optional[Any]
    extra_kwargs: Optional[Dict[str, Any]]

    def __init__(
        self,
        ort_type: HuggingFaceORTModel,
        provider: str,
        quantize: bool = False,
        config: Optional[Any] = None,
        extra_kwargs: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Optional Args to use with a huggingface model

        Args:
            ort_type:
                Optimum onnx class name
            provider:
                Onnx runtime provider to use
            config:
                Optional optimum config to use
            quantize:
                Whether to quantize the model
            extra_kwargs:
                Extra kwargs to pass to the onnx conversion (save_pretrained method for ort models)

        """

class DataProcessor:
    name: str
    uri: Path

    def __str__(self): ...

# Define interface save and metadata arguments
class ModelInterfaceSaveMetadata:
    model_uri: Path
    data_processor_map: Dict[str, DataProcessor]
    sample_data_uri: Path
    onnx_model_uri: Optional[Path]
    drift_profile_uri: Optional[Path]
    extra: Optional[ExtraMetadata]
    save_kwargs: Optional[ModelSaveKwargs]

    def __init__(
        self,
        model_uri: Path,
        data_processor_map: Optional[Dict[str, DataProcessor]] = {},  # type: ignore
        sample_data_uri: Optional[Path] = None,
        onnx_model_uri: Optional[Path] = None,
        drift_profile_uri: Optional[Path] = None,
        extra: Optional[ExtraMetadata] = None,
        save_kwargs: Optional[ModelSaveKwargs] = None,
    ) -> None:
        """Define model interface save arguments

        Args:
            model_uri:
                Path to the model
            data_processor_map:
                Dictionary of data processors
            sample_data_uri:
                Path to the sample data
            onnx_model_uri:
                Path to the onnx model
            drift_profile_uri:
                Path to the drift profile
            extra_metadata:
                Extra metadata
            save_kwargs:
                Optional save args
        """

    def __str__(self): ...
    def model_dump_json(self) -> str: ...

class ModelInterfaceType:
    Base: "ModelInterfaceType"
    Sklearn: "ModelInterfaceType"
    CatBoost: "ModelInterfaceType"
    HuggingFace: "ModelInterfaceType"
    LightGBM: "ModelInterfaceType"
    Lightning: "ModelInterfaceType"
    Torch: "ModelInterfaceType"
    TensorFlow: "ModelInterfaceType"
    VowpalWabbit: "ModelInterfaceType"
    XGBoost: "ModelInterfaceType"

class TaskType:
    Classification: "TaskType"
    Regression: "TaskType"
    Clustering: "TaskType"
    AnomalyDetection: "TaskType"
    TimeSeries: "TaskType"
    Forecasting: "TaskType"
    Recommendation: "TaskType"
    Ranking: "TaskType"
    NLP: "TaskType"
    Image: "TaskType"
    Audio: "TaskType"
    Video: "TaskType"
    Graph: "TaskType"
    Tabular: "TaskType"
    TimeSeriesForecasting: "TaskType"
    TimeSeriesAnomalyDetection: "TaskType"
    TimeSeriesClassification: "TaskType"
    TimeSeriesRegression: "TaskType"
    TimeSeriesClustering: "TaskType"
    TimeSeriesRecommendation: "TaskType"
    TimeSeriesRanking: "TaskType"
    TimeSeriesNLP: "TaskType"
    TimeSeriesImage: "TaskType"
    TimeSeriesAudio: "TaskType"
    TimeSeriesVideo: "TaskType"
    TimeSeriesGraph: "TaskType"
    TimeSeriesTabular: "TaskType"
    Other: "TaskType"

class OnnxSession:
    @property
    def schema(self) -> OnnxSchema:
        """Returns the onnx schema"""

    @property
    def session(self) -> Any:
        """Returns the onnx session"""

    @session.setter
    def session(self, session: Any) -> None:
        """Sets the onnx session

        Args:
            session:
                Onnx session
        """

    def run(
        self,
        input_data: Dict[str, Any],
        output_names: Optional[list[str]] = None,
        run_options: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Run the onnx session

        Args:
            output_names:
                List of output names
            input_data:
                Dictionary of input data
            run_options:
                Optional run options

        Returns:
            Output data
        """

    def model_dump_json(self) -> str:
        """Dump the onnx model to json"""

    @staticmethod
    def model_validate_json(json_string: str) -> "OnnxSession":
        """Validate the onnx model json"""

class ModelInterfaceMetadata:
    task_type: TaskType
    model_type: ModelType
    data_type: DataType
    onnx_session: Optional[OnnxSession]
    schema: FeatureSchema
    save_metadata: ModelInterfaceSaveMetadata
    extra_metadata: dict[str, str]

    def __init__(
        self,
        save_metadata: ModelInterfaceSaveMetadata,
        task_type: TaskType = TaskType.Other,
        model_type: ModelType = ModelType.Unknown,
        data_type: DataType = DataType.NotProvided,
        schema: FeatureSchema = FeatureSchema(),
        onnx_session: Optional[OnnxSession] = None,
        extra_metadata: dict[str, str] = {},  # type: ignore
    ) -> None:
        """Define a model interface

        Args:
            task_type:
                Task type
            model_type:
                Model type
            data_type:
                Data type
            onnx_session:
                Onnx session
            schema:
                Feature schema
            data_type:
                Sample data type
            save_metadata:
                Save metadata
            extra_metadata:
                Extra metadata. Must be a dictionary of strings
        """

    def __str__(self) -> str:
        """Return the string representation of the model interface metadata"""

    def model_dump_json(self) -> str:
        """Dump the model interface metadata to json"""

    @staticmethod
    def model_validate_json(json_string: str) -> "ModelInterfaceMetadata":
        """Validate the model interface metadata json"""

class ModelInterface:
    def __init__(
        self,
        model: None | Any = None,
        sample_data: None | Any = None,
        task_type: None | TaskType = None,
        schema: None | FeatureSchema = None,
        drift_profile: (
            None
            | List[SpcDriftProfile | PsiDriftProfile | CustomDriftProfile]
            | Union[SpcDriftProfile | PsiDriftProfile | CustomDriftProfile]
        ) = None,
    ) -> None:
        """Base class for ModelInterface

        Args:
            data:
                Data. Can be a pyarrow table, pandas dataframe, polars dataframe
                or numpy array
            sample_data:
                Sample data to use to make predictions
            task_type:
                The type of task the model performs
            schema:
                Feature schema for model features
            drift_profile:
                Drift profile to use. Can be a list of SpcDriftProfile, PsiDriftProfile or CustomDriftProfile
        """

    @property
    def model(self) -> None | Any:
        """Returns the model"""

    @model.setter
    def model(self, model: Any) -> None:
        """Sets the model"""

    @property
    def sample_data(self) -> None | Any:
        """Returns the sample data"""

    @sample_data.setter
    def sample_data(self, sample_data: Any) -> None:
        """Sets the sample data"""

    @property
    def data_type(self) -> DataType:
        """Returns the task type"""

    @property
    def task_type(self) -> TaskType:
        """Returns the task type"""

    @property
    def schema(self) -> FeatureSchema:
        """Returns the feature schema"""

    @property
    def model_type(self) -> ModelType:
        """Returns the model type"""

    @property
    def interface_type(self) -> ModelInterfaceType:
        """Returns the model type"""

    @property
    def drift_profile(
        self,
    ) -> List[Any]:
        """Returns the drift profile"""

    @drift_profile.setter
    def drift_profile(
        self,
        profile: List[SpcDriftProfile | PsiDriftProfile | CustomDriftProfile],
    ) -> None:
        """Sets the drift profile"""

    @property
    def onnx_session(self) -> None | OnnxSession:
        """Returns the onnx session if it exists"""

    @onnx_session.setter
    def onnx_session(self, session: None | OnnxSession) -> None:
        """Sets the onnx session


        Args:
            session:
                Onnx session
        """

    @overload
    def create_drift_profile(
        self,
        data: CustomMetric | List[CustomMetric],
        config: CustomMetricDriftConfig,
        data_type: Optional[DataType] = None,
    ) -> CustomDriftProfile: ...
    @overload
    def create_drift_profile(
        self,
        data: Any,
        config: SpcDriftConfig,
        data_type: Optional[DataType] = None,
    ) -> SpcDriftProfile: ...
    @overload
    def create_drift_profile(
        self,
        data: Any,
        config: PsiDriftConfig,
        data_type: Optional[DataType] = None,
    ) -> PsiDriftProfile: ...
    @overload
    def create_drift_profile(
        self,
        data: Any,
        data_type: Optional[DataType] = None,
    ) -> SpcDriftProfile: ...
    def create_drift_profile(  # type: ignore
        self,
        data: Any,
        config: None | SpcDriftConfig | PsiDriftConfig | CustomMetricDriftConfig = None,
        data_type: None | DataType = None,
    ) -> Any:
        """Create a drift profile and append it to the drift profile list

        Args:
            data:
                Data to use to create the drift profile. Can be a pandas dataframe,
                polars dataframe, pyarrow table or numpy array.
            config:
                Drift config to use. If None, defaults to SpcDriftConfig.
            data_type:
                Data type to use. If None, data_type will be inferred from the data.

        Returns:
            Drift profile SPcDriftProfile, PsiDriftProfile or CustomDriftProfile
        """

    def save(
        self,
        path: Path,
        to_onnx: bool = False,
        save_kwargs: None | ModelSaveKwargs = None,
    ) -> ModelInterfaceMetadata:
        """Save the model interface

        Args:
            path (Path):
                Path to save the model
            to_onnx (bool):
                Whether to save the model to onnx
            save_kwargs (ModelSaveKwargs):
                Optional kwargs to pass to the various underlying methods. This is a passthrough object meaning
                that the kwargs will be passed to the underlying methods as is and are expected to be supported by
                the underlying library.

                - model: Kwargs that will be passed to save_model. See save_model for more details.
                - preprocessor: Kwargs that will be passed to save_preprocessor
                - onnx: Kwargs that will be passed to save_onnx_model. See convert_onnx_model for more details
        """

    def load(
        self,
        path: Path,
        onnx: bool = False,
        load_kwargs: None | ModelLoadKwargs = None,
    ) -> None:
        """Load ModelInterface components

        Args:
            path (Path):
                Path to load the model
            onnx (bool):
                Whether to load the onnx model
            load_kwargs (ModelLoadKwargs):
                Optional load kwargs to pass to the different load methods
        """

    @staticmethod
    def from_metadata(metadata: ModelInterfaceMetadata) -> "ModelInterface":
        """Create a ModelInterface from metadata

        Args:
            metadata:
                Model interface metadata

        Returns:
            Model interface
        """

class SklearnModel(ModelInterface):
    def __init__(
        self,
        model: Optional[Any] = None,
        preprocessor: Optional[Any] = None,
        sample_data: Optional[Any] = None,
        task_type: Optional[TaskType] = None,
        schema: Optional[FeatureSchema] = None,
        drift_profile: (
            None
            | List[SpcDriftProfile | PsiDriftProfile | CustomDriftProfile]
            | Union[SpcDriftProfile | PsiDriftProfile | CustomDriftProfile]
        ) = None,
    ) -> None:
        """Instantiate an SklearnModel interface

        Args:
            model:
                Model to associate with interface. This model must be from the
                scikit-learn ecosystem
            preprocessor:
                Preprocessor to associate with the model. This preprocessor must be from the
                scikit-learn ecosystem
            sample_data:
                Sample data to use to make predictions
            task_type:
                The type of task the model performs
            schema:
                Feature schema for model features
            drift_profile:
                Drift profile to use. Can be a list of SpcDriftProfile, PsiDriftProfile or CustomDriftProfile
        """

    @property
    def preprocessor(self) -> Optional[Any]:
        """Returns the preprocessor"""

    @preprocessor.setter
    def preprocessor(self, preprocessor: Any) -> None:
        """Sets the preprocessor

        Args:
            preprocessor:
                Preprocessor to associate with the model. This preprocessor must be from the
                scikit-learn ecosystem
        """

    @property
    def preprocessor_name(self) -> Optional[str]:
        """Returns the preprocessor name"""

class LightGBMModel(ModelInterface):
    def __init__(
        self,
        model: Optional[Any] = None,
        preprocessor: Optional[Any] = None,
        sample_data: Optional[Any] = None,
        task_type: Optional[TaskType] = None,
        schema: Optional[FeatureSchema] = None,
        drift_profile: (
            None
            | List[SpcDriftProfile | PsiDriftProfile | CustomDriftProfile]
            | Union[SpcDriftProfile | PsiDriftProfile | CustomDriftProfile]
        ) = None,
    ) -> None:
        """Instantiate a LightGBMModel interface

        Args:
            model:
                Model to associate with interface. This model must be a lightgbm booster.
            preprocessor:
                Preprocessor to associate with the model.
            sample_data:
                Sample data to use to make predictions
            task_type:
                The type of task the model performs
            schema:
                Feature schema for model features
            drift_profile:
                Drift profile to use. Can be a list of SpcDriftProfile, PsiDriftProfile or CustomDriftProfile
        """

    @property
    def preprocessor(self) -> Optional[Any]:
        """Returns the preprocessor"""

    @preprocessor.setter
    def preprocessor(self, preprocessor: Any) -> None:
        """Sets the preprocessor

        Args:
            preprocessor:
                Preprocessor to associate with the model. This preprocessor must be from the
                scikit-learn ecosystem
        """

    @property
    def preprocessor_name(self) -> Optional[str]:
        """Returns the preprocessor name"""

class XGBoostModel(ModelInterface):
    def __init__(
        self,
        model: Optional[Any] = None,
        preprocessor: Optional[Any] = None,
        sample_data: Optional[Any] = None,
        task_type: Optional[TaskType] = None,
        schema: Optional[FeatureSchema] = None,
        drift_profile: (
            None
            | List[SpcDriftProfile | PsiDriftProfile | CustomDriftProfile]
            | Union[SpcDriftProfile | PsiDriftProfile | CustomDriftProfile]
        ) = None,
    ) -> None:
        """Interface for saving XGBoost Booster models

        Args:
            model:
                Model to associate with interface. This model must be an xgboost booster.
            preprocessor:
                Preprocessor to associate with the model.
            sample_data:
                Sample data to use to make predictions.
            task_type:
                The type of task the model performs
            schema:
                Feature schema for model features
            drift_profile:
                Drift profile to use. Can be a list of SpcDriftProfile, PsiDriftProfile or CustomDriftProfile
        """

    @property
    def preprocessor(self) -> Optional[Any]:
        """Returns the preprocessor"""

    @preprocessor.setter
    def preprocessor(self, preprocessor: Any) -> None:
        """Sets the preprocessor

        Args:
            preprocessor:
                Preprocessor to associate with the model. This preprocessor must be from the
                scikit-learn ecosystem
        """

    @property
    def preprocessor_name(self) -> Optional[str]:
        """Returns the preprocessor name"""

class TorchModel(ModelInterface):
    def __init__(
        self,
        model: Optional[Any] = None,
        preprocessor: Optional[Any] = None,
        sample_data: Optional[Any] = None,
        task_type: Optional[TaskType] = None,
        schema: Optional[FeatureSchema] = None,
        drift_profile: (
            None
            | List[SpcDriftProfile | PsiDriftProfile | CustomDriftProfile]
            | Union[SpcDriftProfile | PsiDriftProfile | CustomDriftProfile]
        ) = None,
    ) -> None:
        """Interface for saving PyTorch models

        Args:
            model:
                Model to associate with interface. This model must inherit from torch.nn.Module.
            preprocessor:
                Preprocessor to associate with model.
            sample_data:
                Sample data to use to convert to ONNX and make sample predictions. This data must be a
                pytorch-supported type. TorchData interface, torch tensor, torch dataset, Dict[str, torch.Tensor],
                List[torch.Tensor], Tuple[torch.Tensor].
            task_type:
                The intended task type of the model.
            schema:
                Feature schema for model features. Will be inferred from the sample data if not provided.
            drift_profile:
                Drift profile to use. Can be a list of SpcDriftProfile, PsiDriftProfile or CustomDriftProfile
        """

    @property
    def preprocessor(self) -> Optional[Any]:
        """Returns the preprocessor"""

    @preprocessor.setter
    def preprocessor(self, preprocessor: Any) -> None:
        """Sets the preprocessor

        Args:
            preprocessor:
                Preprocessor to associate with the model. This preprocessor must be from the
                scikit-learn ecosystem
        """

    @property
    def preprocessor_name(self) -> Optional[str]:
        """Returns the preprocessor name"""

    def save(
        self,
        path: Path,
        to_onnx: bool = False,
        save_kwargs: None | ModelSaveKwargs = None,
    ) -> ModelInterfaceMetadata:
        """Save the TorchModel interface. Torch models are saved
        as state_dicts as is the standard for PyTorch.

        Args:
            path (Path):
                Base path to save artifacts
            to_onnx (bool):
                Whether to save the model to onnx
            save_kwargs (ModelSaveKwargs):
                Optional kwargs to pass to the various underlying methods. This is a passthrough object meaning
                that the kwargs will be passed to the underlying methods as is and are expected to be supported by
                the underlying library.

                - model: Kwargs that will be passed to save_model. See save_model for more details.
                - preprocessor: Kwargs that will be passed to save_preprocessor
                - onnx: Kwargs that will be passed to save_onnx_model. See convert_onnx_model for more details.
        """

class LightningModel(ModelInterface):
    def __init__(
        self,
        trainer: Optional[Any] = None,
        preprocessor: Optional[Any] = None,
        sample_data: Optional[Any] = None,
        task_type: Optional[TaskType] = None,
        schema: Optional[FeatureSchema] = None,
        drift_profile: (
            None
            | List[SpcDriftProfile | PsiDriftProfile | CustomDriftProfile]
            | Union[SpcDriftProfile | PsiDriftProfile | CustomDriftProfile]
        ) = None,
    ) -> None:
        """Interface for saving PyTorch Lightning models

        Args:
            trainer:
                Pytorch lightning trainer to associate with interface.
            preprocessor:
                Preprocessor to associate with model.
            sample_data:
                Sample data to use to convert to ONNX and make sample predictions. This data must be a
                pytorch-supported type. TorchData interface, torch tensor, torch dataset, Dict[str, torch.Tensor],
                List[torch.Tensor], Tuple[torch.Tensor].
            task_type:
                The intended task type of the model.
            schema:
                Feature schema for model features. Will be inferred from the sample data if not provided.
            drift_profile:
                Drift profile to use. Can be a list of SpcDriftProfile, PsiDriftProfile or CustomDriftProfile
        """

    @property
    def trainer(self) -> None:
        """Returns the trainer"""

    @trainer.setter
    def trainer(self, trainer: Any) -> None:
        """Sets the trainer"""

    @property
    def preprocessor(self) -> Optional[Any]:
        """Returns the preprocessor"""

    @preprocessor.setter
    def preprocessor(self, preprocessor: Any) -> None:
        """Sets the preprocessor

        Args:
            preprocessor:
                Preprocessor to associate with the model. This preprocessor must be from the
                scikit-learn ecosystem
        """

    @property
    def preprocessor_name(self) -> Optional[str]:
        """Returns the preprocessor name"""

    def save(
        self,
        path: Path,
        to_onnx: bool = False,
        save_kwargs: None | ModelSaveKwargs = None,
    ) -> ModelInterfaceMetadata:
        """Save the LightningModel interface. Lightning models are saved via checkpoints.

        Args:
            path (Path):
                Base path to save artifacts
            to_onnx (bool):
                Whether to save the model to onnx
            save_kwargs (ModelSaveKwargs):
                Optional kwargs to pass to the various underlying methods. This is a passthrough object meaning
                that the kwargs will be passed to the underlying methods as is and are expected to be supported by
                the underlying library.

                - model: Kwargs that will be passed to save_model. See save_model for more details.
                - preprocessor: Kwargs that will be passed to save_preprocessor
                - onnx: Kwargs that will be passed to save_onnx_model. See convert_onnx_model for more details.
        """

class HuggingFaceModel(ModelInterface):
    def __init__(
        self,
        model: Optional[Any] = None,
        tokenizer: Optional[Any] = None,
        feature_extractor: Optional[Any] = None,
        image_processor: Optional[Any] = None,
        sample_data: Optional[Any] = None,
        hf_task: Optional[HuggingFaceTask] = None,
        task_type: Optional[TaskType] = None,
        schema: Optional[FeatureSchema] = None,
        drift_profile: (
            None
            | List[SpcDriftProfile | PsiDriftProfile | CustomDriftProfile]
            | Union[SpcDriftProfile | PsiDriftProfile | CustomDriftProfile]
        ) = None,
    ) -> None:
        """Interface for saving HuggingFace models and pipelines

        Args:
            model:
                Model to associate with interface. This can be a HuggingFace pipeline (inherits from Pipeline),
                or a HuggingFace model (inherits from PreTrainedModel or TFPreTrainedModel).
            tokenizer:
                Tokenizer to associate with the model. This must be a HuggingFace tokenizer (PreTrainedTokenizerBase).
                If using a pipeline that already has a tokenizer, this can be None.
            feature_extractor:
                Feature extractor to associate with the model. This must be a HuggingFace feature extractor
                (PreTrainedFeatureExtractor). If using a pipeline that already has a feature extractor,
                this can be None.
            image_processor:
                Image processor to associate with the model. This must be a HuggingFace image processor
                (BaseImageProcessor). If using a pipeline that already has an image processor,
                this can be None.
            sample_data:
                Sample data to use to convert to ONNX and make sample predictions. This data must be a
                HuggingFace-supported type.
            hf_task:
                HuggingFace task to associate with the model. Defaults to Undefined.
                Accepted tasks are as follows (taken from HuggingFace pipeline docs):
                    - `"audio-classification"`: will return a [`AudioClassificationPipeline`].
                    - `"automatic-speech-recognition"`: will return a [`AutomaticSpeechRecognitionPipeline`].
                    - `"depth-estimation"`: will return a [`DepthEstimationPipeline`].
                    - `"document-question-answering"`: will return a [`DocumentQuestionAnsweringPipeline`].
                    - `"feature-extraction"`: will return a [`FeatureExtractionPipeline`].
                    - `"fill-mask"`: will return a [`FillMaskPipeline`]:.
                    - `"image-classification"`: will return a [`ImageClassificationPipeline`].
                    - `"image-feature-extraction"`: will return an [`ImageFeatureExtractionPipeline`].
                    - `"image-segmentation"`: will return a [`ImageSegmentationPipeline`].
                    - `"image-text-to-text"`: will return a [`ImageTextToTextPipeline`].
                    - `"image-to-image"`: will return a [`ImageToImagePipeline`].
                    - `"image-to-text"`: will return a [`ImageToTextPipeline`].
                    - `"mask-generation"`: will return a [`MaskGenerationPipeline`].
                    - `"object-detection"`: will return a [`ObjectDetectionPipeline`].
                    - `"question-answering"`: will return a [`QuestionAnsweringPipeline`].
                    - `"summarization"`: will return a [`SummarizationPipeline`].
                    - `"table-question-answering"`: will return a [`TableQuestionAnsweringPipeline`].
                    - `"text2text-generation"`: will return a [`Text2TextGenerationPipeline`].
                    - `"text-classification"` (alias `"sentiment-analysis"` available): will return a
                    [`TextClassificationPipeline`].
                    - `"text-generation"`: will return a [`TextGenerationPipeline`]:.
                    - `"text-to-audio"` (alias `"text-to-speech"` available): will return a [`TextToAudioPipeline`]:.
                    - `"token-classification"` (alias `"ner"` available): will return a [`TokenClassificationPipeline`].
                    - `"translation"`: will return a [`TranslationPipeline`].
                    - `"translation_xx_to_yy"`: will return a [`TranslationPipeline`].
                    - `"video-classification"`: will return a [`VideoClassificationPipeline`].
                    - `"visual-question-answering"`: will return a [`VisualQuestionAnsweringPipeline`].
                    - `"zero-shot-classification"`: will return a [`ZeroShotClassificationPipeline`].
                    - `"zero-shot-image-classification"`: will return a [`ZeroShotImageClassificationPipeline`].
                    - `"zero-shot-audio-classification"`: will return a [`ZeroShotAudioClassificationPipeline`].
                    - `"zero-shot-object-detection"`: will return a [`ZeroShotObjectDetectionPipeline`].
            task_type:
                The intended task type for the model. Note: This is the OpsML task type, not the HuggingFace task type.
            schema:
                Feature schema for model features. Will be inferred from the sample data if not provided.
            drift_profile:
                Drift profile to use. Can be a list of SpcDriftProfile, PsiDriftProfile or CustomDriftProfile
        """

    def save(
        self,
        path: Path,
        to_onnx: bool = False,
        save_kwargs: None | ModelSaveKwargs = None,
    ) -> ModelInterfaceMetadata:
        """Save the HuggingFaceModel interface

        Args:
            path (Path):
                Base path to save artifacts
            to_onnx (bool):
                Whether to save the model/pipeline to onnx
            save_kwargs (ModelSaveKwargs):
                Optional kwargs to pass to the various underlying methods. This is a passthrough object meaning
                that the kwargs will be passed to the underlying methods as is and are expected to be supported by
                the underlying library.

                - model: Kwargs that will be passed to save_model. See save_model for more details.
                - preprocessor: Kwargs that will be passed to save_preprocessor
                - onnx: Kwargs that will be passed when saving the onnx model
                    - For the HuggingFaceModel, this should be an instance of HuggingFaceOnnxArgs
        """

    @property
    def model(self) -> Optional[Any]:
        """Returns as HuggingFace model (PreTrainedModel, TFPreTrainedModel).
        Can be None if the model is a pipeline.
        """

    @model.setter
    def model(self, model: Any) -> None:
        """Sets the model

        Args:
            model:
                Model to associate with the interface. This must be a HuggingFace model (PreTrainedModel, TFPreTrainedModel).
                If using a pipeline that already has a model, this can be None.
        """

    @property
    def tokenizer(self) -> Optional[Any]:
        """Returns the tokenizer. Can be None if the model is a pipeline.
        If present, will be of type PreTrainedTokenizerBase
        """

    @tokenizer.setter
    def tokenizer(self, tokenizer: Any) -> None:
        """Sets the tokenizer

        Args:
            tokenizer:
                Tokenizer to associate with the model. This must be a HuggingFace tokenizer (PreTrainedTokenizerBase).
                If using a pipeline that already has a tokenizer, this can be None.
        """

    @property
    def image_processor(self) -> Optional[Any]:
        """Returns the image processor. Can be None if the model is a pipeline.
        If present, will be of type BaseImageProcessor
        """

    @image_processor.setter
    def image_processor(self, image_processor: Any) -> None:
        """Sets the image processor

        Args:
            image_processor:
                Image processor to associate with the model. This must be a HuggingFace image processor
                (BaseImageProcessor). If using a pipeline that already has an image processor,
                this can be None.
        """

    @property
    def feature_extractor(self) -> Optional[Any]:
        """Returns the feature extractor. Can be None if the model is a pipeline.
        If present, will be of type PreTrainedFeatureExtractor
        """

    @feature_extractor.setter
    def feature_extractor(self, feature_extractor: Any) -> None:
        """Sets the feature extractor

        Args:
            feature_extractor:
                Feature extractor to associate with the model. This must be a HuggingFace feature extractor
                (PreTrainedFeatureExtractor). If using a pipeline that already has a feature extractor,
                this can be None.
        """

class CatBoostModel(ModelInterface):
    def __init__(
        self,
        model: Optional[Any] = None,
        preprocessor: Optional[Any] = None,
        sample_data: Optional[Any] = None,
        task_type: Optional[TaskType] = None,
        schema: Optional[FeatureSchema] = None,
        drift_profile: (
            None
            | List[SpcDriftProfile | PsiDriftProfile | CustomDriftProfile]
            | Union[SpcDriftProfile | PsiDriftProfile | CustomDriftProfile]
        ) = None,
    ) -> None:
        """Interface for saving CatBoost models

        Args:
            model:
                Model to associate with the interface. This model must be a CatBoost model.
            preprocessor:
                Preprocessor to associate with the model.
            sample_data:
                Sample data to use to make predictions.
            task_type:
                The type of task the model performs
            schema:
                Feature schema for model features
            drift_profile:
                Drift profile to use. Can be a list of SpcDriftProfile, PsiDriftProfile or CustomDriftProfile
        """

    @property
    def preprocessor(self) -> Optional[Any]:
        """Returns the preprocessor"""

    @preprocessor.setter
    def preprocessor(self, preprocessor: Any) -> None:
        """Sets the preprocessor

        Args:
            preprocessor:
                Preprocessor to associate with the model. This preprocessor must be from the
                scikit-learn ecosystem
        """

    @property
    def preprocessor_name(self) -> Optional[str]:
        """Returns the preprocessor name"""

class TensorFlowModel(ModelInterface):
    def __init__(
        self,
        model: Optional[Any] = None,
        preprocessor: Optional[Any] = None,
        sample_data: Optional[Any] = None,
        task_type: Optional[TaskType] = None,
        schema: Optional[FeatureSchema] = None,
        drift_profile: (
            None
            | List[SpcDriftProfile | PsiDriftProfile | CustomDriftProfile]
            | Union[SpcDriftProfile | PsiDriftProfile | CustomDriftProfile]
        ) = None,
    ) -> None:
        """Interface for saving PyTorch models

        Args:
            model:
                Model to associate with interface. This model must inherit from tensorflow.keras.Model
            preprocessor:
                Preprocessor to associate with model.
            sample_data:
                Sample data to use to convert to ONNX and make sample predictions. This data must be a
                tensorflow-supported type. numpy array, tf.Tensor, torch dataset, Dict[str, tf.Tensor],
                List[tf.Tensor], Tuple[tf.Tensor].
            task_type:
                The intended task type of the model.
            schema:
                Feature schema for model features. Will be inferred from the sample data if not provided.
            drift_profile:
                Drift profile to use. Can be a list of SpcDriftProfile, PsiDriftProfile or CustomDriftProfile
        """

    @property
    def preprocessor(self) -> Optional[Any]:
        """Returns the preprocessor"""

    @preprocessor.setter
    def preprocessor(self, preprocessor: Any) -> None:
        """Sets the preprocessor

        Args:
            preprocessor:
                Preprocessor to associate with the model. This preprocessor must be from the
                scikit-learn ecosystem
        """

    @property
    def preprocessor_name(self) -> Optional[str]:
        """Returns the preprocessor name"""
