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

class RegistryType:
    Data: "RegistryType"
    Model: "RegistryType"
    Run: "RegistryType"
    Project: "RegistryType"
    Audi: "RegistryType"
    Pipeline: "RegistryType"

class DataType:
    Pandas: "DataType"
    PyArrow: "DataType"
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
class ModelInterfaceSaveMetadata:
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

    def save_data(self, path: Path) -> None:
        """Save the data to a file

        Args:
            path:
                Base path to save the data to
        """

    def load_data(self, path: Path) -> None:
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

class NumpyData:
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

class PolarsData:
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
                Polars dataframe
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

    def save_data(self, path: Path, **kwargs) -> None:
        """Save the data to a file

        Args:
            path:
                Base path to save the data to
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
