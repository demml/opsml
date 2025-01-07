from pathlib import Path
from typing import Any, Dict, List, NewType, Optional, Union

# shared
class CommonKwargs:
    IsPipeline: "CommonKwargs"
    ModelType: "CommonKwargs"
    ModelClass: "CommonKwargs"
    ModelArch: "CommonKwargs"
    PreprocessorName: "CommonKwargs"
    Preprocessor: "CommonKwargs"
    TaskType: "CommonKwargs"
    Model: "CommonKwargs"
    Undefined: "CommonKwargs"
    Backend: "CommonKwargs"
    Pytorch: "CommonKwargs"
    Tensorflow: "CommonKwargs"
    SampleData: "CommonKwargs"
    Onnx: "CommonKwargs"
    LoadType: "CommonKwargs"
    DataType: "CommonKwargs"
    Tokenizer: "CommonKwargs"
    TokenizerName: "CommonKwargs"
    FeatureExtractor: "CommonKwargs"
    FeatureExtractorName: "CommonKwargs"
    Image: "CommonKwargs"
    Text: "CommonKwargs"
    VowpalArgs: "CommonKwargs"
    BaseVersion: "CommonKwargs"
    SampleDataInterfaceType: "CommonKwargs"

    @staticmethod
    def from_string(s: str) -> Optional["CommonKwargs"]:
        """Return the CommonKwargs enum from a string.

        Args:
            s:
                The string representation of the CommonKwargs.

        Returns:
            The CommonKwargs enum.
        """

    def as_string(self) -> str:
        """Return the string representation of the CommonKwargs.

        Returns:
            String representation of the CommonKwargs.
        """

class SaveName:
    Card: "SaveName"
    Audit: "SaveName"
    PipelineCard: "SaveName"
    ModelMetadata: "SaveName"
    TrainedModel: "SaveName"
    Preprocessor: "SaveName"
    OnnxModel: "SaveName"
    SampleModelData: "SaveName"
    DataProfile: "SaveName"
    Data: "SaveName"
    Profile: "SaveName"
    Artifacts: "SaveName"
    QuantizedModel: "SaveName"
    Tokenizer: "SaveName"
    FeatureExtractor: "SaveName"
    Metadata: "SaveName"
    Graphs: "SaveName"
    OnnxConfig: "SaveName"
    Dataset: "SaveName"
    DriftProfile: "SaveName"

    @staticmethod
    def from_string(s: str) -> Optional["SaveName"]:
        """Return the SaveName enum from a string.

        Args:
            s:
                The string representation of the SaveName.

        Returns:
            The SaveName enum.
        """

    def as_string(self) -> str:
        """Return the string representation of the SaveName.

        Returns:
            String representation of the SaveName.
        """

    def __str__(self):
        """Return a string representation of the SaveName.

        Returns:
            String representation of the SaveName.
        """

class Suffix:
    Onnx: "Suffix"
    Parquet: "Suffix"
    Zarr: "Suffix"
    Joblib: "Suffix"
    Html: "Suffix"
    Json: "Suffix"
    Ckpt: "Suffix"
    Pt: "Suffix"
    Text: "Suffix"
    Catboost: "Suffix"
    Jsonl: "Suffix"
    Empty: "Suffix"
    Dmatrix: "Suffix"
    Model: "Suffix"

    @staticmethod
    def from_string(s: str) -> Optional["Suffix"]:
        """Return the Suffix enum from a string.

        Args:
            s:
                The string representation of the Suffix.

        Returns:
            The Suffix enum.
        """

    def as_string(self) -> str:
        """Return the string representation of the Suffix.

        Returns:
            String representation of the Suffix.
        """

    def __str__(self):
        """Return a string representation of the Suffix.

        Returns:
            String representation of the Suffix.
        """

class SaverPath:
    path: Path

    def __init__(
        self,
        parent: Path,
        child: Optional[Path],
        filename: Optional[SaveName],
        extension: Optional[Suffix],
    ) -> None:
        """Helper for creating paths for saving artifacts.

        Args:
            parent (Path):
                The parent path.
            child (Path | None):
                The child path.
            filename (SaveName | None):
                The filename.
            extension (Suffix | None):
                The extension.
        """

class RegistryType:
    Data: "RegistryType"
    Model: "RegistryType"
    Run: "RegistryType"
    Project: "RegistryType"
    Audi: "RegistryType"
    Pipeline: "RegistryType"

class DataType:
    Pandas: "DataType"
    Arrow: "DataType"
    Polars: "DataType"
    Numpy: "DataType"
    Image: "DataType"
    Text: "DataType"
    Dict: "DataType"
    Sql: "DataType"
    Profile: "DataType"
    TransformerBatch: "DataType"
    String: "DataType"
    TorchTensor: "DataType"
    TorchDataset: "DataType"
    TensorflowTensor: "DataType"
    Tuple: "DataType"
    List: "DataType"
    Str: "DataType"
    OrderedDict: "DataType"
    Joblib: "DataType"
    Base: "DataType"
    Dataset: "DataType"

class InterfaceType:
    Data: "InterfaceType"
    Model: "InterfaceType"

# Errors
class OpsmlError(Exception):
    def __init__(self, message: str) -> None: ...
    def __str__(self) -> str: ...

# Config
class OpsmlConfig:
    def __init__(self, client_mode: Optional[bool] = None) -> None:
        """Initialize the OpsmlConfig.

        Args:
            client_mode:
                Whether to use the client. By default, OpsML will determine whether
                to run in client mode based on the provided OPSML_TRACKING_URI. This attribute
                will override that behavior. Default is None.
        """

    def __str__(self):
        """Return a string representation of the OpsmlConfig.

        Returns:
            String representation of the OpsmlConfig.
        """

# Cards
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

class Feature:
    feature_type: str
    shape: List[int]
    extra_args: Dict[str, str]

    def __init__(
        self,
        feature_type: str,
        shape: List[int],
        extra_args: Optional[Dict[str, str]] = None,
    ) -> None:
        """Define a feature

        Args:
            feature_type:
                The type of the feature
            shape:
                The shape of the feature
            extra_args:
                Extra arguments to pass to the feature
        """

    def __str__(self) -> str:
        """Return a string representation of the Feature.

        Returns:
            String representation of the Feature.
        """

class FeatureMap:
    def __init__(self, map: Optional[dict[str, Feature]] = None) -> None:
        """Define a feature map

        Args:
            features:
                The features to use in the feature map
        """

    def __str__(self) -> str:
        """Return a string representation of the FeatureMap."""

    def __getitem__(self, key: str) -> Feature:
        """Returns the feature at the given key."""

class OnnxSchema:
    input_features: dict[str, Feature]
    output_features: dict[str, Feature]
    onnx_version: str

    def __init__(
        self,
        input_features: dict[str, Feature],
        output_features: dict[str, Feature],
        onnx_version: str,
    ) -> None:
        """Define an onnx schema

        Args:
            input_features:
                The input features of the onnx schema
            output_features:
                The output features of the onnx schema
            onnx_version:
                The onnx version of the schema
        """

    def __str__(self) -> str:
        """Return a string representation of the OnnxSchema.

        Returns:
            String representation of the OnnxSchema.
        """

class DataSchema:
    data_type: str
    input_features: Optional[dict[str, Feature]]
    output_features: Optional[dict[str, Feature]]
    onnx_schema: Optional[OnnxSchema]

    def __init__(
        self,
        data_type: str,
        input_features: Optional[dict[str, Feature]] = None,
        output_features: Optional[dict[str, Feature]] = None,
        onnx_schema: Optional[OnnxSchema] = None,
    ) -> None:
        """Define a data schema

        Args:
            data_type:
                The type of the data schema
            input_features:
                The input features of the data schema
            output_features:
                The output features of the data schema
            onnx_schema:
                The onnx schema of the data schema
        """

    def __str__(self) -> str:
        """Return a string representation of the DataSchema.

        Returns:
            String representation of the DataSchema.
        """

class Description:
    summary: Optional[str]
    sample_code: Optional[str]
    notes: Optional[str]

    def __init__(
        self,
        summary: Optional[str] = None,
        sample_code: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> None:
        """Define a description to be used in a card

        Args:
            summary:
                A summary string or path to a markdown file with a summary.
                You can also define a summary on the ui for the card.
            sample_code:
                Sample code string or path to a markdown file with sample code.
            notes:
                Any additional notes
        """

    def __str__(self) -> str:
        """Return a string representation of the Description.

        Returns:
            String representation of the Description.
        """

# Utils

class VersionType:
    Major = "major"
    Minor = "minor"
    Patch = "patch"
    Pre = "pre"
    Build = "build"
    PreBuild = "prebuild"

    def __init__(self, version_type: str) -> None: ...
    def __eq__(self, other: object) -> bool: ...

class FileUtils:
    @staticmethod
    def open_file(filepath: str) -> str:
        """Open a file and return the contents as a string

        Args:
            filepath:
                The name of the file

        Returns:
            The file path
        """

    @staticmethod
    def find_path_to_file(filepath: str) -> str:
        """Find the path to a file

        Args:
            filepath:
                The name of the file

        Returns:
            The file path
        """

# Define interface save and metadata arguments
class ModelDataInterfaceSaveMetadata:
    trained_model_uri: str
    sample_data_uri: str
    preprocessor_uri: Optional[str]
    preprocessor_name: Optional[str]
    onnx_model_uri: Optional[str]
    extra_metadata: Optional[Dict[str, str]]

    def __init__(
        self,
        trained_model_uri: str,
        sample_data_uri: str,
        preprocessor_uri: Optional[str] = None,
        preprocessor_name: Optional[str] = None,
        onnx_model_uri: Optional[str] = None,
        extra_metadata: Optional[Dict[str, str]] = None,
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
        """

class ModelInterfaceMetadata:
    task_type: str
    model_type: str
    data_type: str
    modelcard_uid: str
    feature_map: dict[str, Feature]
    sample_data_interface_type: str
    save_metadata: ModelDataInterfaceSaveMetadata
    extra_metadata: dict[str, str]

    def __init__(
        self,
        interface: Any,
        save_metadata: ModelDataInterfaceSaveMetadata,
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
        feature_map: dict[str, Feature],
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
        feature_map: dict[str, Feature],
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
        feature_map: dict[str, Feature],
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
        feature_map: dict[str, Feature],
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
        feature_map: dict[str, Feature],
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

class Card:
    uid: Optional[str]
    created_at: Optional[str]
    app_env: Optional[str]
    name: str
    repository: str
    version: str
    contact: str
    tags: Dict[str, str]
    datacard_uids: Optional[List[str]]
    modelcard_uids: Optional[List[str]]
    runcard_uids: Optional[List[str]]
    pipelinecard_uid: Optional[str]
    auditcard_uid: Optional[str]
    interface_type: Optional[str]
    data_type: Optional[str]
    model_type: Optional[str]
    task_type: Optional[str]

    def __str__(self) -> str:
        """Return a string representation of the Card.

        Returns:
            String representation of the Card.
        """

class CardList:
    cards: List[Card]

    def as_table(self) -> None:
        """Print cards as a table"""

class CardInfo:
    name: Optional[str]
    repository: Optional[str]
    contact: Optional[str]
    uid: Optional[str]
    version: Optional[str]
    tags: Optional[Dict[str, str]]

    def __init__(
        self,
        name: Optional[str] = None,
        repository: Optional[str] = None,
        contact: Optional[str] = None,
        uid: Optional[str] = None,
        version: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
    ) -> None:
        """Define card information

        Args:
            name:
                The name of the card
            repository:
                The repository of the card
            contact:
                The contact of the card
            uid:
                The uid of the card
            version:
                The version of the card
            tags:
                The tags of the card
        """

    def set_env(self) -> None:
        """Helper to set environment variables for the current runtime environment"""

# Registry

class CardRegistry:
    def __init__(self, registry_type: RegistryType) -> None:
        """
        Interface for connecting to any of the Card registries

        Args:
            registry_type:
                Type of card registry to create

        Returns:
            Instantiated connection to specific Card registry

        Example:
            data_registry = CardRegistry(RegistryType.DATA)
            data_registry.list_cards()

            or
            data_registry = CardRegistry("data")
            data_registry.list_cards()
        """

    def registry_type(self) -> RegistryType:
        """Return the registry type.

        Returns:
            The registry type.
        """

    def table_name(self) -> str:
        """Return the table name.

        Returns:
            The table name.
        """

    def list_cards(
        self,
        info: Optional[CardInfo] = None,
        uid: Optional[str] = None,
        name: Optional[str] = None,
        repository: Optional[str] = None,
        version: Optional[str] = None,
        max_date: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
        limit: Optional[int] = None,
        sort_by_time: Optional[bool] = None,
    ) -> CardList:
        """List all cards in the registry.

        Returns:
            A list of card names.
        """

class RegistryTestHelper:
    """Helper class for testing the registry"""

    def __init__(self) -> None: ...
    def setup(self) -> None: ...
    def cleanup(self) -> None: ...

class LogLevel:
    Debug: "LogLevel"
    Info: "LogLevel"
    Warning: "LogLevel"
    Error: "LogLevel"

class OpsmlLogger:
    @staticmethod
    def setup_logging(log_level: Optional[LogLevel] = None) -> None:
        """Setup logging

        Args:
            log_level:
                The log level to use. Default is INFO
        """

    @staticmethod
    def get_logger(log_level: Optional[LogLevel] = None) -> "OpsmlLogger":
        """
        Get the logger

        Args:
            log_level:
                The log level to use. Default is INFO

        Returns:
            The logger
        """

    def info(self, message: str, *args) -> None:
        """Logs a message at the Info level.

        Args:
            message:
                The message to log
            args:
                Args to format the message with
        """

    def debug(self, message: str, *args) -> None:
        """Logs a message at the Debug level.

        Args:
            message:
                The message to log
            args:
                Args to format the message with
        """

    def warn(self, message: str, *args) -> None:
        """Logs a message at the Warning level.

        Args:
            message:
                The message to log
            args:
                Args to format the message with
        """

    def error(self, message: str, *args) -> None:
        """Logs a message at the Error level.

        Args:
            message:
                The message to log
            args:
                Args to format the message with
        """

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

class ColValType:
    String: "ColValType"
    Float: "ColValType"
    Int: "ColValType"
    Timestamp: "ColValType"

class ColType:
    Builtin: "ColType"
    Timestamp: "ColType"

class ColumnSplit:
    column_name: str
    column_value: ColValType
    column_type: ColType
    inequality: Inequality

    def __init__(
        self,
        column_name: str,
        column_value: Union[str, float, int],
        column_type: ColType,
        inequality: Optional[Union[str, Inequality]] = None,
    ) -> None:
        """Define a column split

        Args:
            column_name:
                The name of the column
            column_value:
                The value of the column. Can be a string, float, or int. If
                timestamp, convert to isoformat (str) and specify timestamp coltype
            column_type:
                The type of the column
            inequality:
                The inequality of the column
        """

class StartStopSplit:
    start: int
    stop: int

    def __init__(self, start: int, stop: int) -> None:
        """Define a start stop split

        Args:
            start:
                The start of the split
            stop:
                The stop of the split
        """

class IndiceSplit:
    indices: List[int]

    def __init__(self, indices: List[int]) -> None:
        """Define an indice split

        Args:
            indices:
                The indices of the split
        """

class DataSplit:
    label: str
    column_split: Optional[ColumnSplit]
    start_stop_split: Optional[StartStopSplit]
    indice_split: Optional[IndiceSplit]

    def __init__(
        self,
        label: str,
        column_split: Optional[ColumnSplit] = None,
        start_stop_split: Optional[StartStopSplit] = None,
        indice_split: Optional[IndiceSplit] = None,
    ) -> None:
        """Define a data split

        Args:
            label:
                The label of the split
            column_split:
                The column split
            start_stop_split:
                The start stop split
            indice_split:
                The indice split
        """

class DataSplits:
    def __init__(self, splits: List[DataSplit]) -> None:
        """Define data splits

        Args:
            splits:
                The data splits
        """

    def __str__(self) -> str:
        """String representation of the data splits"""

    @property
    def splits(self) -> List[DataSplit]:
        """Return the splits"""

    @splits.setter
    def splits(self, splits: List[DataSplit]) -> None:
        """Set the splits"""

    def split_data(
        self,
        data: Any,
        data_type: DataType,
        dependent_vars: DependentVars,
    ) -> Dict[str, Data]:
        """Split the data

        Args:
            data:
                The data to split
            data_type:
                The data type
            dependent_vars:
                Dependent variables to associate with the data

        Returns:
            A dictionary of data splits
        """

class Data:
    x: Any
    y: Any

class SqlLogic:
    def __init__(self, queries: Dict[str, str]) -> None:
        """Define sql logic

        Args:
            queries:
                Sql logic used to generate data represented as a dictionary.
                Key is the name to assign to the sql logic and value is either a sql query
                or a path to a .sql file.
        """

    def __str__(self) -> str:
        """String representation of the sql logic"""

    def add_sql_logic(
        self,
        name: str,
        query: Optional[str] = None,
        filepath: Optional[str] = None,
    ) -> None:
        """Add sql logic to existing queries

        Args:
            name:
                The name to associate with the sql logic
            query:
                SQL query
            filepath:
                Filepath to SQL query

        """

    @property
    def queries(self) -> Dict[str, str]:
        """Return the queries"""

    @queries.setter
    def queries(self, queries: Dict[str, str]) -> None:
        """Set the queries"""

    def __getitem__(self, key: str) -> str:
        """Get the query by key

        Args:
            key:
                The key to get the query by

        Returns:
            The query
        """

class DependentVars:
    def __init__(
        self,
        column_names: Optional[List[str]] = None,
        column_indices: Optional[List[int]] = None,
    ) -> None:
        """Define dependent variables for the data interface. User
        can specify either column names or column indices.

        Args:
            column_names:
                The column names of the dependent variables
            column_indices:
                The column indices of the dependent variables
        """

    def __str__(self) -> str:
        """String representation of the dependent variables"""

    @property
    def column_names(self) -> List[str]:
        """Return the column names"""

    @column_names.setter
    def column_names(self, column_names: List[str]) -> None:
        """Set the column names"""

    @property
    def column_indices(self) -> List[int]:
        """Return the column indices"""

    @column_indices.setter
    def column_indices(self, column_indices: List[int]) -> None:
        """Set the column indices"""

class Inequality:
    Equal: "Inequality"
    GreaterThan: "Inequality"
    GreaterThanEqual: "Inequality"
    LesserThan: "Inequality"
    LesserThanEqual: "Inequality"

class DataSplitter:
    @staticmethod
    def split_data(
        split: DataSplit,
        data: Any,
        data_type: DataType,
        dependent_vars: DependentVars,
    ) -> Data:
        """Create a split

        Args:
            split:
                The data split to use to split the data
            data:
                The data to split
            data_type:
                The data type
            dependent_vars:
                Dependent variables to associate with the data

        Returns:
            A Data object
        """

class DataInterface:
    def __init__(
        self,
        data: Optional[Any] = None,
        data_splits: Optional[Union[DataSplits, List[DataSplit]]] = None,
        dependent_vars: Optional[Union[DependentVars, List[str], List[int]]] = None,
        feature_map: Optional[FeatureMap] = None,
        sql_logic: Optional[SqlLogic] = None,
    ) -> None:
        """Define a data interface

        Args:
            data:
                Data. Can be a pyarrow table, pandas dataframe, polars dataframe
                or numpy array
            dependent_vars:
                List of dependent variables to associate with data
            data_splits:
                Optional list of `DataSplit`
            feature_map:
                Dictionary of features -> automatically generated
            sql_logic:
                Sql logic used to generate data represented as a dictionary.
                Key is the name to assign to the sql logic and value is either a sql query
                or a path to a .sql file.
        """

    @property
    def data(self) -> Optional[Any]:
        """Returns the data"""

    @data.setter
    def data(self, data: Any) -> None:
        """Sets the data"""

    @property
    def data_splits(self) -> DataSplits:
        """Returns the data splits."""

    @data_splits.setter
    def data_splits(self, data_splits: Union[DataSplits, List[DataSplit]]) -> None:
        """Sets the data splits"""

    @property
    def dependent_vars(self) -> DependentVars:
        """Returns the dependent variables."""

    @dependent_vars.setter
    def dependent_vars(
        self,
        dependent_vars: Union[DependentVars, List[str], List[int]],
    ) -> None:
        """Sets the dependent variables"""

    @property
    def feature_map(self) -> FeatureMap:
        """Returns the feature map."""

    @feature_map.setter
    def feature_map(self, feature_map: FeatureMap) -> None:
        """Sets the feature map"""

    @property
    def sql_logic(self) -> SqlLogic:
        """Returns the sql logic."""

    @property
    def data_type(self) -> DataType:
        """Return the data type."""

    def add_sql_logic(
        self,
        name: str,
        query: Optional[str] = None,
        filepath: Optional[str] = None,
    ) -> None:
        """Add sql logic to the data interface

        Args:
            name:
                The name of the sql logic
            query:
                The optional query to use
            filepath:
                The optional filepath to open the query from
        """

    def save_sql(self, path: Path, **kwargs) -> Optional[Path]:
        """Save the sql logic to a file

        Args:
            Path:
                The path to save the sql logic to
        """

    def create_feature_map(self, name: str) -> FeatureMap:
        """Save the sql logic to a file

        Args:
            name:
                The name of the data object
        """

    def save_data(self, path: Path, **kwargs) -> Path:
        """Save the data to a file

        Args:
            path:
                Base path to save the data to
        """

    def save(self, path: Path, **kwargs) -> DataInterfaceSaveMetadata:
        """Saves all data interface component to the given path. This used as part of saving a
        DataCard

        Methods called in save:
            - save_sql: Saves all sql logic to files(s)
            - create_feature_map: Creates a featuremap from the associated data
            - save_data: Saves the data to a file

        Args:
            path:
                The path to save the data interface components to.

        """

    def load_data(self, path: Path, **kwargs) -> None:
        """Load the data from a file

        Args:
            path:
                Base path to load the data from
        """

    def split_data(self) -> Dict[str, Data]:
        """Split the data

        Returns:
            A dictionary of data splits
        """

class DataInterfaceSaveMetadata:
    data_type: DataType
    feature_map: FeatureMap
    data_save_path: Path
    sql_save_path: Optional[Path]
    data_profile_save_path: Optional[Path]

    def __init__(
        self,
        data_type: DataType,
        feature_map: FeatureMap,
        data_save_path: Path,
        data_profile_save_path: Optional[Path] = None,
    ) -> None:
        """Define interface save metadata

        Args:
            data_type:
                The data type
            feature_map:
                The feature map
            data_save_path:
                The data save path
            data_profile_save_path:
                The data profile save path
        """

class NumpyData(DataInterface):
    def __init__(
        self,
        data: Optional[Any] = None,
        data_splits: Optional[Union[DataSplits, List[DataSplit]]] = None,
        dependent_vars: Optional[Union[DependentVars, List[str], List[int]]] = None,
        feature_map: Optional[FeatureMap] = None,
        sql_logic: Optional[SqlLogic] = None,
    ) -> None:
        """Define a data interface

        Args:
            data:
                Numpy array
            dependent_vars:
                List of dependent variables to associate with data
            data_splits:
                Optional list of `DataSplit`
            feature_map:
                Dictionary of features -> automatically generated
            sql_logic:
                Sql logic used to generate data represented as a dictionary.
                Key is the name to assign to the sql logic and value is either a sql query
                or a path to a .sql file.
        """

    def save_data(self, path: Path, **kwargs) -> Path:
        """Save data using numpy save format

        Args:
            path (Path) :
                Base path to save the data to

        Kwargs:

            see: https://numpy.org/doc/stable/reference/generated/numpy.save.html

            allow_pickle (bool):
                Allow saving object arrays using Python pickles.
            fix_imports (bool):
                The fix_imports flag is deprecated and has no effect

        """

    def save(self, path: Path, **kwargs) -> DataInterfaceSaveMetadata:
        """Saves Interface attributes. This used as part of saving a
        DataCard

        Methods called in save:
            - save_sql: Saves all sql logic to files(s)
            - create_feature_map: Creates a featuremap from the associated data
            - save_data: Saves the data to a file

        Args:
            path:
                The path to save the data interface components to.

        """

    def load_data(self, path: Path, **kwargs) -> None:
        """Load the data via numpy.load

        Args:
            path (Path):
                Base path to load the data from

        Kwargs:

            see: https://numpy.org/doc/stable/reference/generated/numpy.load.html

            mmap_mode:
                If not None, then memory-map the file, using the given mode
            allow_pickle (bool):
                Allow loading pickled object arrays stored in npy files
            fix_imports (bool):
                If fix_imports is True, pickle will try to map the old Python 2 names to the new names used in Python 3.
            encoding (str):
                What encoding to use when reading Python 2 strings. Only useful when py3k is True.
            max_header_size (int):
                The maximum size of the file header
        """

class PolarsData(DataInterface):
    def __init__(
        self,
        data: Optional[Any] = None,
        data_splits: Optional[Union[DataSplits, List[DataSplit]]] = None,
        dependent_vars: Optional[Union[DependentVars, List[str], List[int]]] = None,
        feature_map: Optional[FeatureMap] = None,
        sql_logic: Optional[SqlLogic] = None,
    ) -> None:
        """Define a data interface

        Args:
            data (pl.DataFrame | None):
                Pandas dataframe
            dependent_vars (DependentVars | List[str] | List[int] | None):
                List of dependent variables to associate with data
            data_splits (DataSplits | List[DataSplit]):
                Optional list of `DataSplit`
            feature_map (FeatureMap | None):
                Dictionary of features -> automatically generated
            sql_logic (SqlLogic | None):
                Sql logic used to generate data represented as a dictionary.
                Key is the name to assign to the sql logic and value is either a sql query
                or a path to a .sql file.

        """

    def save_data(self, path: Path, **kwargs) -> Path:
        """Saves polars dataframe to parquet dataset via write_parquet

        Args:
            path (Path):
                Base path to save the data to

        Kwargs:
            compression (ParquetCompression):
                Compression codec to use for writing.
            compression_level (int | None):
                Compression level to use. Default is None.
            statistics (bool | str | dict[str, bool]):
                Whether to write statistics. Default is True.
            row_group_size (int | None):
                Number of rows per row group. Default is None.
            data_page_size (int | None):
                Size of data pages. Default is None.
            use_pyarrow (bool):
                Whether to use PyArrow for writing. Default is False.
            pyarrow_options (dict[str, Any] | None):
                Additional options for PyArrow. Default is None.
            partition_by (str | Sequence[str] | None):
                Columns to partition by. Default is None.
            partition_chunk_size_bytes (int):
                Size of partition chunks in bytes. Default is 4294967296.
            storage_options (dict[str, Any] | None):
                Additional storage options. Default is None.
            credential_provider (CredentialProviderFunction | Literal['auto'] | None):
                Credential provider function. Default is 'auto'.
            retries (int):
                Number of retries for writing. Default is 2.

        See Also:
            https://docs.pola.rs/api/python/dev/reference/api/polars.DataFrame.write_parquet.html

        """

    def load_data(self, path: Path, **kwargs) -> None:
        """Load the data from a file

        Args:
            path (Path):
                Base path to load the data from

        Kwargs:
            columns (list[int] | list[str] | None):
                Columns to load. Default is None.
            n_rows (int | None):
                Number of rows to load. Default is None.
            row_index_name (str | None):
                Name of the row index. Default is None.
            row_index_offset (int):
                Offset for the row index. Default is 0.
            parallel (ParallelStrategy):
                Parallel strategy to use. Default is 'auto'.
            use_statistics (bool):
                Whether to use statistics. Default is True.
            hive_partitioning (bool | None):
                Whether to use hive partitioning. Default is None.
            glob (bool):
                Whether to use glob pattern matching. Default is True.
            schema (SchemaDict | None):
                Schema to use. Default is None.
            hive_schema (SchemaDict | None):
                Hive schema to use. Default is None.
            try_parse_hive_dates (bool):
                Whether to try parsing hive dates. Default is True.
            rechunk (bool):
                Whether to rechunk the data. Default is False.
            low_memory (bool):
                Whether to use low memory mode. Default is False.
            storage_options (dict[str, Any] | None):
                Additional storage options. Default is None.
            credential_provider (CredentialProviderFunction | Literal['auto'] | None):
                Credential provider function. Default is 'auto'.
            retries (int):
                Number of retries for loading. Default is 2.
            use_pyarrow (bool):
                Whether to use PyArrow for loading. Default is False.
            pyarrow_options (dict[str, Any] | None):
                Additional options for PyArrow. Default is None.
            memory_map (bool):
                Whether to use memory mapping. Default is True.
            include_file_paths (str | None):
                File paths to include. Default is None.
            allow_missing_columns (bool):
                Whether to allow missing columns. Default is False.

        See Also:
            https://docs.pola.rs/api/python/dev/reference/api/polars.read_parquet.html
        """

class PandasData(DataInterface):
    def __init__(
        self,
        data: Optional[Any] = None,
        data_splits: Optional[Union[DataSplits, List[DataSplit]]] = None,
        dependent_vars: Optional[Union[DependentVars, List[str], List[int]]] = None,
        feature_map: Optional[FeatureMap] = None,
        sql_logic: Optional[SqlLogic] = None,
    ) -> None:
        """Define a data interface

        Args:
            data (pd.DataFrame | None):
                Pandas dataframe
            dependent_vars (DependentVars | List[str] | List[int] | None):
                List of dependent variables to associate with data
            data_splits (DataSplits | List[DataSplit]):
                Optional list of `DataSplit`
            feature_map (FeatureMap | None):
                Dictionary of features -> automatically generated
            sql_logic (SqlLogic | None):
                Sql logic used to generate data represented as a dictionary.
                Key is the name to assign to the sql logic and value is either a sql query
                or a path to a .sql file.
        """

    def save_data(self, path: Path, **kwargs) -> Path:
        """Saves pandas dataframe as parquet file via to_parquet

        Args:
            path:
                Base path to save the data to

        Kwargs:
            engine ({'auto', 'pyarrow', 'fastparquet'}):
                Parquet library to use. If 'auto', then the option io.parquet.engine is used. The default io.parquet.engine behavior is to try 'pyarrow',
                falling back to 'fastparquet' if 'pyarrow' is unavailable. Default is 'auto'.
            compression (str | None):
                Name of the compression to use. Use None for no compression.
                Supported options: 'snappy', 'gzip', 'brotli', 'lz4', 'zstd'. Default is 'snappy'.
            index (bool | None):
                If True, include the dataframe’s index(es) in the file output.
                If False, they will not be written to the file. If None, similar to True the dataframe's index(es) will be saved.
                However, instead of being saved as values, the RangeIndex will be stored as a range in the metadata so it doesn't require much space and is faster.
                Other indexes will be included as columns in the file output. Default is None.
            partition_cols (list | None):
                Column names by which to partition the dataset. Columns are partitioned in the order they are given.
                Must be None if path is not a string. Default is None.
            storage_options (dict | None):
                Extra options that make sense for a particular storage connection, e.g. host, port, username, password, etc.
                For HTTP(S) URLs the key-value pairs are forwarded to urllib.request.Request as header options.
                For other URLs (e.g. starting with “s3://”, and “gcs://”) the key-value pairs are forwarded to fsspec.open. Default is None.
            **kwargs:
                Any additional kwargs are passed to the engine

        Additional Information:
            https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_parquet.html
        """

    def load_data(self, path: Path, **kwargs) -> None:
        """Load the pandas dataframe from a parquet dataset via read_parquet

        Args:
            path:
                Base path to load the data from

        Kwargs:
            engine ({'auto', 'pyarrow', 'fastparquet'}):
                Parquet library to use. If 'auto', then the option io.parquet.engine is used.
                The default io.parquet.engine behavior is to try 'pyarrow', falling back to 'fastparquet' if 'pyarrow' is unavailable. Default is 'auto'.
            columns (list | None):
                If not None, only these columns will be read from the file. Default is None.
            storage_options (dict | None):
                Extra options that make sense for a particular storage connection, e.g. host, port, username, password, etc.
                For HTTP(S) URLs the key-value pairs are forwarded to urllib.request.Request as header options.
                For other URLs (e.g. starting with “s3://”, and “gcs://”) the key-value pairs are forwarded to fsspec.open. Default is None.
            use_nullable_dtypes (bool):
                If True, use dtypes that use pd.NA as missing value indicator for the resulting DataFrame.
                (only applicable for the pyarrow engine) As new dtypes are added that support pd.NA in the future, the output with this option will change to use those dtypes.
                Note: this is an experimental option, and behaviour (e.g. additional support dtypes) may change without notice. Default is False. Deprecated since version 2.0.
            dtype_backend ({'numpy_nullable', 'pyarrow'}):
                Back-end data type applied to the resultant DataFrame (still experimental).
                Behaviour is as follows:
                    - "numpy_nullable": returns nullable-dtype-backed DataFrame (default).
                    - "pyarrow": returns pyarrow-backed nullable ArrowDtype DataFrame. Default is 'numpy_nullable'.
            filesystem (fsspec | pyarrow filesystem | None):
                Filesystem object to use when reading the parquet file. Only implemented for engine="pyarrow". Default is None.
            filters (list[tuple] | list[list[tuple]] | None):
                To filter out data.
                Filter syntax:
                    [[(column, op, val), …],…] where op is [==, =, >, >=, <, <=, !=, in, not in]
                The innermost tuples are transposed into a set of filters applied through an AND operation.
                The outer list combines these sets of filters through an OR operation. A single list of tuples can also be used, meaning that no OR operation between set of filters is to be conducted.
                Using this argument will NOT result in row-wise filtering of the final partitions unless engine="pyarrow" is also specified.
                For other engines, filtering is only performed at the partition level, that is, to prevent the loading of some row-groups and/or files.
                Default is None.
            **kwargs:
                Any additional kwargs are passed to the engine.

        Additional Information:
            https://pandas.pydata.org/docs/reference/api/pandas.read_parquet.html
        """

class ArrowData(DataInterface):
    def __init__(
        self,
        data: Optional[Any] = None,
        data_splits: Optional[Union[DataSplits, List[DataSplit]]] = None,
        dependent_vars: Optional[Union[DependentVars, List[str], List[int]]] = None,
        feature_map: Optional[FeatureMap] = None,
        sql_logic: Optional[SqlLogic] = None,
    ) -> None:
        """Define a data interface

        Args:
             data (pa.Table | None):
                PyArrow Table
            dependent_vars (DependentVars | List[str] | List[int] | None):
                List of dependent variables to associate with data
            data_splits (DataSplits | List[DataSplit]):
                Optional list of `DataSplit`
            feature_map (FeatureMap | None):
                Dictionary of features -> automatically generated
            sql_logic (SqlLogic | None):
                Sql logic used to generate data represented as a dictionary.
                Key is the name to assign to the sql logic and value is either a sql query
                or a path to a .sql file.
        """

    def save_data(self, path: Path, **kwargs) -> Path:
        """Saves pyarrow table to parquet via write_table

        Args:
            path:
                Base path to save the data to

        Kwargs:
            row_group_size (int | None):
                Maximum number of rows in each written row group. If None, the row group size will be the minimum of the Table size and 1024 * 1024. Default is None.
            version ({'1.0', '2.4', '2.6'}):
                Determine which Parquet logical types are available for use. Default is '2.6'.
            use_dictionary (bool | list):
                Specify if dictionary encoding should be used in general or only for some columns. Default is True.
            compression (str | dict):
                Specify the compression codec, either on a general basis or per-column. Valid values: {'NONE', 'SNAPPY', 'GZIP', 'BROTLI', 'LZ4', 'ZSTD'}. Default is 'snappy'.
            write_statistics (bool | list):
                Specify if statistics should be written in general or only for some columns. Default is True.
            use_deprecated_int96_timestamps (bool | None):
                Write timestamps to INT96 Parquet format. Default is None.
            coerce_timestamps (str | None):
                Cast timestamps to a particular resolution. Valid values: {None, 'ms', 'us'}. Default is None.
            allow_truncated_timestamps (bool):
                Allow loss of data when coercing timestamps to a particular resolution. Default is False.
            data_page_size (int | None):
                Set a target threshold for the approximate encoded size of data pages within a column chunk (in bytes). Default is None.
            flavor ({'spark'} | None):
                Sanitize schema or set other compatibility options to work with various target systems. Default is None.
            filesystem (FileSystem | None):
                Filesystem object to use when reading the parquet file. Default is None.
            compression_level (int | dict | None):
                Specify the compression level for a codec, either on a general basis or per-column. Default is None.
            use_byte_stream_split (bool | list):
                Specify if the byte_stream_split encoding should be used in general or only for some columns. Default is False.
            column_encoding (str | dict | None):
                Specify the encoding scheme on a per column basis. Default is None.
            data_page_version ({'1.0', '2.0'}):
                The serialized Parquet data page format version to write. Default is '1.0'.
            use_compliant_nested_type (bool):
                Whether to write compliant Parquet nested type (lists). Default is True.
            encryption_properties (FileEncryptionProperties | None):
                File encryption properties for Parquet Modular Encryption. Default is None.
            write_batch_size (int | None):
                Number of values to write to a page at a time. Default is None.
            dictionary_pagesize_limit (int | None):
                Specify the dictionary page size limit per row group. Default is None.
            store_schema (bool):
                By default, the Arrow schema is serialized and stored in the Parquet file metadata. Default is True.
            write_page_index (bool):
                Whether to write a page index in general for all columns. Default is False.
            write_page_checksum (bool):
                Whether to write page checksums in general for all columns. Default is False.
            sorting_columns (Sequence[SortingColumn] | None):
                Specify the sort order of the data being written. Default is None.
            store_decimal_as_integer (bool):
                Allow decimals with 1 <= precision <= 18 to be stored as integers. Default is False.
            **kwargs:
                Additional options for ParquetWriter.

        Additional Information:
            https://arrow.apache.org/docs/python/generated/pyarrow.parquet.write_table.html
        """

    def load_data(self, path: Path, **kwargs) -> None:
        """Load the data from a file

        Args:
            path:
                Base path to load the data from

        Kwargs:
            columns (list | None):
                If not None, only these columns will be read from the file. A column name may be a prefix of a nested field, e.g. 'a' will select 'a.b', 'a.c', and 'a.d.e'. If empty, no columns will be read. Default is None.
            use_threads (bool):
                Perform multi-threaded column reads. Default is True.
            schema (Schema | None):
                Optionally provide the Schema for the parquet dataset, in which case it will not be inferred from the source. Default is None.
            use_pandas_metadata (bool):
                If True and file has custom pandas schema metadata, ensure that index columns are also loaded. Default is False.
            read_dictionary (list | None):
                List of names or column paths (for nested types) to read directly as DictionaryArray. Only supported for BYTE_ARRAY storage. Default is None.
            memory_map (bool):
                If the source is a file path, use a memory map to read file, which can improve performance in some environments. Default is False.
            buffer_size (int):
                If positive, perform read buffering when deserializing individual column chunks. Otherwise IO calls are unbuffered. Default is 0.
            partitioning (pyarrow.dataset.Partitioning | str | list of str):
                The partitioning scheme for a partitioned dataset. Default is 'hive'.
            filesystem (FileSystem | None):
                If nothing passed, will be inferred based on path. Default is None.
            filters (pyarrow.compute.Expression | list[tuple] | list[list[tuple]] | None):
                Rows which do not match the filter predicate will be removed from scanned data. Default is None.
            use_legacy_dataset (bool | None):
                Deprecated and has no effect from PyArrow version 15.0.0. Default is None.
            ignore_prefixes (list | None):
                Files matching any of these prefixes will be ignored by the discovery process. Default is ['.', '_'].
            pre_buffer (bool):
                Coalesce and issue file reads in parallel to improve performance on high-latency filesystems (e.g. S3). Default is True.
            coerce_int96_timestamp_unit (str | None):
                Cast timestamps that are stored in INT96 format to a particular resolution (e.g. 'ms'). Default is None.
            decryption_properties (FileDecryptionProperties | None):
                File-level decryption properties. Default is None.
            thrift_string_size_limit (int | None):
                If not None, override the maximum total string size allocated when decoding Thrift structures. Default is None.
            thrift_container_size_limit (int | None):
                If not None, override the maximum total size of containers allocated when decoding Thrift structures. Default is None.
            page_checksum_verification (bool):
                If True, verify the checksum for each page read from the file. Default is False.

        Additional Information:
            https://arrow.apache.org/docs/python/generated/pyarrow.parquet.read_table.html
        """

class TorchData(DataInterface):
    def __init__(
        self,
        data: Optional[Any] = None,
        data_splits: Optional[Union[DataSplits, List[DataSplit]]] = None,
        dependent_vars: Optional[Union[DependentVars, List[str], List[int]]] = None,
        feature_map: Optional[FeatureMap] = None,
        sql_logic: Optional[SqlLogic] = None,
    ) -> None:
        """Define a data interface

        Args:
             data (torch.Tensor | None):
                Torch tensor
            dependent_vars (DependentVars | List[str] | List[int] | None):
                List of dependent variables to associate with data
            data_splits (DataSplits | List[DataSplit]):
                Optional list of `DataSplit`
            feature_map (FeatureMap | None):
                Dictionary of features -> automatically generated
            sql_logic (SqlLogic | None):
                Sql logic used to generate data represented as a dictionary.
                Key is the name to assign to the sql logic and value is either a sql query
                or a path to a .sql file.
        """

    def save_data(self, path: Path, **kwargs) -> Path:
        """Saves torch tensor to a file

        Args:
            path:
                Base path to save the data to

        Kwargs:
            pickle_module (Any):
                Module used for pickling metadata and objects.
            pickle_protocol (int):
                Can be specified to override the default protocol.


        Additional Information:
           https://pytorch.org/docs/main/generated/torch.save.html
        """

    def load_data(self, path: Path, **kwargs) -> None:
        """Load the torch tensor from file

        Args:
            path:
                Base path to load the data from

        Kwargs:
            map_location:
                A function, torch.device, string or a dict specifying how to remap storage locations.
            pickle_module:
                Module used for unpickling metadata and objects (has to match the pickle_module used to serialize file).
            weights_only:
                Indicates whether unpickler should be restricted to loading only tensors, primitive types, dictionaries and any types added via torch.serialization.add_safe_globals().
            mmap:
                Indicates whether the file should be mmaped rather than loading all the storages into memory.
                Typically, tensor storages in the file will first be moved from disk to CPU memory,
                after which they are moved to the location that they were tagged with when saving, or specified by map_location.
                This second step is a no-op if the final location is CPU. When the mmap flag is set,
                instead of copying the tensor storages from disk to CPU memory in the first step, f is mmaped.
            pickle_load_args:
                (Python 3 only) optional keyword arguments passed over to pickle_module.load() and pickle_module.Unpickler(), e.g., errors=....


        Additional Information:
            https://pytorch.org/docs/stable/generated/torch.load.html
        """

class SqlData:
    data_type: DataType

    def __init__(self, sql_logic: SqlLogic) -> None:
        """Define a sql data interface

        Args:
            sql (SqlLogic):
                Sql logic used to generate data represented as a dictionary.
        """

    def save(self, path: Path, **kwargs) -> DataInterfaceSaveMetadata:
        """Save the sql logic to a file

        Args:
            path (Path):
                The path to save the sql logic to
        """

def generate_feature_schema(data: Any, data_type: DataType) -> FeatureMap:
    """Generate a feature schema

    Args:
        data:
            Data to generate the feature schema from
        data_type:
            The data type

    Returns:
        A feature map
    """

class DataCardMetadata:
    @property
    def data_type(self) -> DataType:
        """Return the data type"""

    @property
    def description(self) -> Description:
        """Return the data type"""

    @property
    def feature_map(self) -> FeatureMap:
        """Return the feature map"""

    @property
    def runcard_uid(self) -> Optional[str]:
        """Return the runcard uid"""

    @property
    def pipelinecard_uid(self) -> Optional[str]:
        """Return the runcard uid"""

    @property
    def auditcard_uid(self) -> Optional[str]:
        """Return the runcard uid"""

class DataCard:
    def __init__(
        self,
        interface: DataInterface,
        name: Optional[str] = None,
        repository: Optional[str] = None,
        contact: Optional[str] = None,
        version: Optional[str] = None,
        uid: Optional[str] = None,
        info: Optional[CardInfo] = None,
        tags: Dict[str, str] = {},
        metadata: Optional[DataCardMetadata] = None,
    ) -> None:
        """Define a data card

        Args:
            name:
                The name of the data card
            repository:
                The repository of the data card
            contact:
                The contact of the data card
            version:
                The version of the data card
            uid:
                The uid of the data card
            info:
                The info of the data card
            tags:
                The tags of the data card
        """

    @property
    def uri(self) -> str:
        """Return the uri"""

    def save(self, path: Path, **kwargs) -> DataInterfaceSaveMetadata:
        """Save the data card

        Args:
            path:
                The path to save the data card to

        Kwargs:
            Kwargs are passed to the underlying data interface for saving.
            For a complete list of options see the save method of the data interface and
            their associated libraries.
        """
