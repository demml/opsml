from pathlib import Path
from typing import Optional

from ..scouter.types import DriftType

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

class VersionType:
    Major: "VersionType"
    Minor: "VersionType"
    Patch: "VersionType"
    Pre: "VersionType"
    Build: "VersionType"
    PreBuild: "VersionType"

    def __init__(self, version_type: str) -> None: ...
    def __eq__(self, other: object) -> bool: ...

class DriftProfileUri:
    root_dir: Path
    uri: Path
    drift_type: DriftType

    def __init__(self, uri: Path, drift_type: DriftType) -> None:
        """Define a drift profile

        Args:
            root_dir:
                The root directory of the drift profile
            uri:
                The relative path to the drift profile
            drift_type:
                Drift profile type
        """
