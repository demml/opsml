from pathlib import Path
from typing import Any, Dict, Optional

from ..core import CommonKwargs, FeatureSchema, OnnxSchema
from ..data import DataType

class HuggingFaceORTModel:
    OrtAudioClassification = "ORTModelForAudioClassification"
    OrtAudioFrameClassification = "ORTModelForAudioFrameClassification"
    OrtAudioXVector = "ORTModelForAudioXVector"
    OrtCustomTasks = "ORTModelForCustomTasks"
    OrtCtc = "ORTModelForCTC"
    OrtFeatureExtraction = "ORTModelForFeatureExtraction"
    OrtImageClassification = "ORTModelForImageClassification"
    OrtMaskedLm = "ORTModelForMaskedLM"
    OrtMultipleChoice = "ORTModelForMultipleChoice"
    OrtQuestionAnswering = "ORTModelForQuestionAnswering"
    OrtSemanticSegmentation = "ORTModelForSemanticSegmentation"
    OrtSequenceClassification = "ORTModelForSequenceClassification"
    OrtTokenClassification = "ORTModelForTokenClassification"
    OrtSeq2SeqLm = "ORTModelForSeq2SeqLM"
    OrtSpeechSeq2Seq = "ORTModelForSpeechSeq2Seq"
    OrtVision2Seq = "ORTModelForVision2Seq"
    OrtPix2Struct = "ORTModelForPix2Struct"
    OrtCausalLm = "ORTModelForCausalLM"
    OrtOptimizer = "ORTOptimizer"
    OrtQuantizer = "ORTQuantizer"
    OrtTrainer = "ORTTrainer"
    OrtSeq2SeqTrainer = "ORTSeq2SeqTrainer"
    OrtTrainingArguments = "ORTTrainingArguments"
    OrtSeq2SeqTrainingArguments = "ORTSeq2SeqTrainingArguments"
    OrtStableDiffusionPipeline = "ORTStableDiffusionPipeline"
    OrtStableDiffusionImg2ImgPipeline = "ORTStableDiffusionImg2ImgPipeline"
    OrtStableDiffusionInpaintPipeline = "ORTStableDiffusionInpaintPipeline"
    OrtStableDiffusionXlPipeline = "ORTStableDiffusionXLPipeline"
    OrtStableDiffusionXlImg2ImgPipeline = "ORTStableDiffusionXLImg2ImgPipeline"

class HuggingFaceOnnxArgs:
    ort_type: HuggingFaceORTModel
    provider: str
    quantize: bool
    config: Optional[Any]

    def __init__(
        self,
        ort_type: HuggingFaceORTModel,
        provider: str,
        quantize: bool = False,
        config: Optional[Any] = None,
    ) -> None:
        """Optional Args to use with a huggingface model

        Args:
            ort_type:
                Optimum onnx class name
            provider:
                Onnx runtime provider to use
            config:
                Optional optimum config to use
        """

class TorchOnnxArgs:
    input_names: list[str]
    output_names: list[str]
    dynamic_axes: Optional[Dict[str, Dict[int, str]]]
    do_constant_folding: bool
    export_params: bool
    verbose: bool

    def __init__(
        self,
        input_names: list[str],
        output_names: list[str],
        dynamic_axes: Optional[Dict[str, Dict[int, str]]] = None,
        do_constant_folding: bool = True,
        export_params: bool = True,
        verbose: bool = True,
    ) -> None:
        """Optional arguments to pass to torch when converting to onnx

        Args:
            input_names:
                Optional list containing input names for model inputs.
            output_names:
                Optional list containing output names for model outputs.
            dynamic_axes:
                Optional PyTorch attribute that defines dynamic axes
            constant_folding:
                Whether to use constant folding optimization. Default is True
        """

    def model_dump(self) -> dict[str, Any]:
        """Dump onnx args to dictionary

        Returns:
            Dictionary containing model information
        """

class TorchSaveArgs:
    as_state_dict: bool

    def __init__(self, as_state_dict: bool = False) -> None:
        """Optional arguments to pass to torch when saving a model

        Args:
            as_state_dict:
                Whether to save the model as a state dict. Default is False
        """

class SaveArgs:
    def __init__(self, onnx: Optional[Dict], model: Optional[Dict]) -> None:
        """Optional arguments to pass to save_model

        Args:
            onnx (Dict):
                Optional onnx arguments
            model (Dict):
                Optional model arguments
        """

# Define interface save and metadata arguments
class ModelInterfaceSaveMetadata:
    trained_model_uri: str
    sample_data_uri: str
    preprocessor_uri: Optional[str]
    preprocessor_name: Optional[str]
    onnx_model_uri: Optional[str]
    extra_metadata: Optional[Dict[str, str]]
    save_args: Optional[SaveArgs]

    def __init__(
        self,
        trained_model_uri: str,
        sample_data_uri: str,
        preprocessor_uri: Optional[str] = None,
        preprocessor_name: Optional[str] = None,
        onnx_model_uri: Optional[str] = None,
        extra_metadata: Optional[Dict[str, str]] = None,
        save_args: Optional[SaveArgs] = None,
    ) -> None:
        """Define model interface save arguments

        Args:
            trained_model_uri:
                The trained model uri
            sample_data_uri:
                The sample data uri
            preprocessor_uri:
                The preprocessor uri
            onnx_model_uri:
                The onnx model uri
            extra_metadata:
                The save metadata
            save_args:
                Optional save args for the model and onnx model
        """

class ModelInterfaceMetadata:
    task_type: str
    model_type: str
    data_type: str
    modelcard_uid: str
    feature_map: FeatureSchema
    sample_data_interface_type: str
    save_metadata: ModelInterfaceSaveMetadata
    extra_metadata: dict[str, str]

    def __init__(
        self,
        interface: Any,
        save_metadata: ModelInterfaceSaveMetadata,
        extra_metadata: Optional[dict[str, str]] = None,
    ) -> None:
        """Define a model interface

        Args:
            interface:
                The interface to use
            save_metadata:
                The save metadata
            metadata:
                Any additional metadata
        """

class SklearnModelInterfaceMetadata(ModelInterfaceMetadata):
    preprocessor_name: str

    def __init__(
        self,
        task_type: str,
        model_type: str,
        data_type: str,
        modelcard_uid: str,
        feature_map: FeatureSchema,
        sample_data_interface_type: str,
        preprocessor_name: str,
        metadata: Optional[dict[str, str]] = None,
    ) -> None:
        """Define a model interface

        Args:
            task_type:
                The type of task the model performs
            model_type:
                The type of model
            data_type:
                The type of data the model uses
            modelcard_uid:
                The modelcard uid
            feature_map:
                A dictionary of features
            sample_data_interface_type:
                The type of sample data interface
            preprocessor_name:
                The name of the preprocessor
            metadata:
                Any additional metadata
        """

class CatBoostModelInterfaceMetadata(SklearnModelInterfaceMetadata): ...

class HuggingFaceOnnxSaveArgs:
    ort_type: HuggingFaceORTModel
    provider: str
    quantize: bool

    def __init__(
        self, ort_type: HuggingFaceORTModel, provider: str, quantize: bool
    ) -> None:
        """Optional Args to use with a huggingface model

        Args:
            ort_type:
                Optimum onnx class name
            provider:
                Onnx runtime provider to use
            quantize:
                Whether to quantize the model
        """

class HuggingFaceModelInterfaceMetadata(SklearnModelInterfaceMetadata):
    is_pipeline: bool
    backend: CommonKwargs
    onnx_args: HuggingFaceOnnxSaveArgs
    tokenizer_name: str
    feature_extractor_name: str

    def __init__(
        self,
        task_type: str,
        model_type: str,
        data_type: str,
        modelcard_uid: str,
        feature_map: FeatureSchema,
        sample_data_interface_type: str,
        preprocessor_name: str,
        is_pipeline: bool,
        backend: CommonKwargs,
        onnx_args: HuggingFaceOnnxSaveArgs,
        tokenizer_name: str,
        feature_extractor_name: str,
        metadata: Optional[dict[str, str]] = None,
    ) -> None:
        """Define a model interface

        Args:
            task_type:
                The type of task the model performs
            model_type:
                The type of model
            data_type:
                The type of data the model uses
            modelcard_uid:
                The modelcard uid
            feature_map:
                A dictionary of features
            sample_data_interface_type:
                The type of sample data interface
            preprocessor_name:
                The name of the preprocessor
            is_pipeline:
                Whether the model is a pipeline
            backend:
                The backend to use
            onnx_args:
                The onnx args to use
            tokenizer_name:
                The name of the tokenizer
            feature_extractor_name:
                The name of the feature extractor
            metadata:
                Any additional metadata
        """

class LightGBMModelInterfaceMetadata(SklearnModelInterfaceMetadata): ...

class LightningInterfaceMetadata(SklearnModelInterfaceMetadata):
    onnx_args: Optional[TorchOnnxArgs]

    def __init__(
        self,
        task_type: str,
        model_type: str,
        data_type: str,
        modelcard_uid: str,
        feature_map: FeatureSchema,
        sample_data_interface_type: str,
        preprocessor_name: str,
        onnx_args: Optional[TorchOnnxArgs] = None,
        metadata: Optional[dict[str, str]] = None,
    ) -> None:
        """Define a model interface

        Args:
            task_type:
                The type of task the model performs
            model_type:
                The type of model
            data_type:
                The type of data the model uses
            modelcard_uid:
                The modelcard uid
            feature_map:
                A dictionary of features
            sample_data_interface_type:
                The type of sample data interface
            preprocessor_name:
                The name of the preprocessor
            onnx_args:
                The onnx args to use
            metadata:
                Any additional metadata
        """

class TorchInterfaceMetadata(SklearnModelInterfaceMetadata):
    onnx_args: Optional[TorchOnnxArgs]
    save_args: TorchSaveArgs

    def __init__(
        self,
        task_type: str,
        model_type: str,
        data_type: str,
        modelcard_uid: str,
        feature_map: FeatureSchema,
        sample_data_interface_type: str,
        preprocessor_name: str,
        onnx_args: Optional[TorchOnnxArgs] = None,
        save_args: Optional[TorchSaveArgs] = None,
        metadata: Optional[dict[str, str]] = None,
    ) -> None:
        """Define a model interface

        Args:
            task_type:
                The type of task the model performs
            model_type:
                The type of model
            data_type:
                The type of data the model uses
            modelcard_uid:
                The modelcard uid
            feature_map:
                A dictionary of features
            sample_data_interface_type:
                The type of sample data interface
            preprocessor_name:
                The name of the preprocessor
            onnx_args:
                The onnx args to use
            save_args:
                The save args to use
            metadata:
                Any additional metadata
        """

class TensorFlowInterfaceMetadata(SklearnModelInterfaceMetadata): ...

class VowpalWabbitInterfaceMetadata(ModelInterfaceMetadata):
    arguments: str

    def __init__(
        self,
        task_type: str,
        model_type: str,
        data_type: str,
        modelcard_uid: str,
        feature_map: FeatureSchema,
        arguments: str,
        sample_data_interface_type: str,
        metadata: Optional[dict[str, str]] = None,
    ) -> None:
        """Define a model interface

        Args:
            task_type:
                The type of task the model performs
            model_type:
                The type of model
            data_type:
                The type of data the model uses
            modelcard_uid:
                The modelcard uid
            feature_map:
                A dictionary of features
            arguments:
                The arguments to use
            sample_data_interface_type:
                The type of sample data interface
            metadata:
                Any additional metadata
        """

class XGBoostModelInterfaceMetadata(SklearnModelInterfaceMetadata): ...

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
    def onnx_schema(self) -> OnnxSchema:
        """Returns the onnx schema"""

    @property
    def session(self) -> Any:
        """Returns the onnx session"""

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

class ModelInterface:
    def __init__(
        self,
        model: Optional[Any] = None,
        sample_data: Optional[Any] = None,
        task_type: Optional[TaskType] = None,
        schema: Optional[FeatureSchema] = None,
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
        """

    @property
    def task_type(self) -> TaskType:
        """Returns the task type"""

    @property
    def data_type(self) -> DataType:
        """Returns the task type"""

    @property
    def sample_data(self) -> Optional[Any]:
        """Returns the data"""

    @sample_data.setter
    def sample_data(self, data: Any) -> None:
        """Sets the data"""

    def convert_to_onnx(self, **kwargs) -> None:
        """Convert the model to onnx

        **kwargs:
            Optional arguments to pass to the onnx converter
        """

    def save_onnx_model(self, path: Path, **kwargs) -> None:
        """Save the onnx model

        Args:
            path (Path):
                Path to save the model

        **kwargs:
            Optional arguments to pass to the onnx converter

        """

    def load_onnx_model(self, path: Path, **kwargs) -> None:
        """Load the onnx model

        Args:
            path (Path):
                Path to load the model

        **kwargs:
            Optional arguments to pass to the onnx converter

        """

    def save(
        self,
        path: Path,
        model_kwargs: Optional[Dict] = None,
        to_onnx: bool = False,
        onnx_kwargs: Optional[Dict] = None,
    ) -> ModelInterfaceMetadata:
        """Save the model interface

        Args:
            path (Path):
                Path to save the model
            to_onnx (bool):
                Whether to save the model to onnx
            onnx_kwargs (Optional[Dict]):
                Optional onnx arguments to pass to the onnx converter
            model_kwargs (Optional[Dict]):
                Optional model arguments to pass to save_model
        """

    @property
    def onnx_session(self) -> Optional[OnnxSession]:
        """Returns the onnx schema if it exists"""

class SklearnModel(ModelInterface):
    def __init__(
        self,
        model: Optional[Any] = None,
        preprocessor: Optional[Any] = None,
        sample_data: Optional[Any] = None,
        task_type: Optional[TaskType] = None,
        schema: Optional[FeatureSchema] = None,
    ) -> None:
        """Base class for ModelInterface

        Args:
            model:
                Model to associate with interface. This model must be from the
                scikit-learn ecosystem
            preprocessor:
                Preprocessor to associate with interface. This preprocessor must be from the
                scikit-learn ecosystem
            sample_data:
                Sample data to use to make predictions
            task_type:
                The type of task the model performs
            schema:
                Feature schema for model features
        """

    @property
    def preprocessor(self) -> Optional[Any]:
        """Returns the preprocessor"""

    @property
    def preprocessor_name(self) -> Optional[str]:
        """Returns the preprocessor name"""
