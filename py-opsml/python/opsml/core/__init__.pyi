from pathlib import Path
from typing import Dict, List, Optional

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
    Model: "SaveName"
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

class InterfaceType:
    Data: "InterfaceType"
    Model: "InterfaceType"

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

class FeatureSchema:
    def __init__(self, items: Optional[dict[str, Feature]] = None) -> None:
        """Define a feature map

        Args:
            features:
                The features to use in the feature map
        """

    def __str__(self) -> str:
        """Return a string representation of the FeatureSchema."""

    def __getitem__(self, key: str) -> Feature:
        """Returns the feature at the given key."""

# Utils

class OnnxSchema:
    def __init__(
        self,
        input_features: FeatureSchema,
        output_features: FeatureSchema,
        onnx_version: str,
        feature_names: List[str],
    ) -> None:
        """Define an onnx schema

        Args:
            input_features:
                The input features of the onnx schema
            output_features:
                The output features of the onnx schema
            onnx_version:
                The onnx version of the schema
            feature_names:
                The feature names and order for onnx
        """

    def __str__(self) -> str:
        """Return a string representation of the OnnxSchema.

        Returns:
            String representation of the OnnxSchema.
        """

    @property
    def input_features(self) -> FeatureSchema:
        """Return the input features of the OnnxSchema."""

    @property
    def output_features(self) -> FeatureSchema:
        """Return the output features of the OnnxSchema."""

    @property
    def onnx_version(self) -> str:
        """Return the onnx version of the OnnxSchema."""

    @property
    def feature_names(self) -> List[str]:
        """Return the feature names and order for onnx."""

class DataSchema:
    data_type: str
    input_features: Optional[FeatureSchema]
    output_features: Optional[FeatureSchema]
    onnx_schema: Optional[OnnxSchema]

    def __init__(
        self,
        data_type: str,
        input_features: Optional[FeatureSchema] = None,
        output_features: Optional[FeatureSchema] = None,
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
