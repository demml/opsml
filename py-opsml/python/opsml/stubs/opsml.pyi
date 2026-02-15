#### begin imports ####

import datetime
from pathlib import Path
from typing import (
    Any,
    Dict,
    Generic,
    List,
    Optional,
    Sequence,
    TypeAlias,
    TypeVar,
    Union,
    overload,
)

from .card import *
from .genai.potato import *
from .scouter.evaluate import *
from .scouter.scouter import *
from .service.agent import AgentSpec

CardInterfaceType: TypeAlias = Union["DataInterface", "ModelInterface"]
ServiceCardInterfaceType: TypeAlias = Dict[str, Union["DataInterface", "ModelInterface"]]
LoadInterfaceType: TypeAlias = Union[ServiceCardInterfaceType, ServiceCardInterfaceType]
#### end of imports ####

class DriftConfig:
    def __init__(
        self,
        active: bool = False,
        deactivate_others: bool = False,
        drift_type: List[str] = [],
    ):
        """Initialize drift detection configuration for model and prompt cards.

        Args:
            active:
                Whether drift detection is active. Defaults to False
            deactivate_others:
                Whether to deactivate previous drift config versions. Defaults to False
            drift_type:
                Types of drift detection to enable (e.g., 'psi', 'custom'). Defaults to empty list
        """

    @property
    def active(self) -> bool:
        """Whether drift detection is currently active."""

    @property
    def deactivate_others(self) -> bool:
        """Whether to deactivate other drift configurations."""

    @property
    def drift_type(self) -> List[str]:
        """List of drift detection types enabled."""

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
    TensorFlowTensor: "DataType"
    Tuple: "DataType"
    List: "DataType"
    Str: "DataType"
    OrderedDict: "DataType"
    Joblib: "DataType"
    Base: "DataType"
    Dataset: "DataType"
    NotProvided: "DataType"

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

class DriftProfileUri:
    root_dir: Path
    uri: Path
    drift_type: DriftType

class DriftArgs:
    def __init__(self, active: bool = True, deactivate_others: bool = False) -> None:
        """Define a drift config

        Args:
            active (bool):
                Whether to set the drift profile to active
            deactivate_others (bool):
                Whether to deactivate all other drift profiles of the same space and name
        """

    @property
    def active(self) -> bool:
        """Return the active status of the drift profile."""

    @property
    def deactivate_others(self) -> bool:
        """Return the deactivate_others status of the drift profile."""

class DriftProfileMap:
    def __init__(self) -> None:
        """Creates an empty drift profile map"""

    def add_profile(self, alias: str, profile: Any) -> None:
        """Add a drift profile to the map

        Args:
            alias:
                Alias to use for the drift profile
            profile:
                Drift profile to add
        """

    def __getitem__(self, key: str) -> Any:
        """Returns the drift profile at the given key"""

    def is_empty(self) -> bool:
        """Returns whether the drift profile map is empty

        Returns:
            True if the drift profile map is empty, False otherwise
        """

class ExtraMetadata:
    metadata: Dict[str, Any]

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

########################################################################################
#  This section contains the type definitions for opsml.data module
# __opsml.data__
# ######################################################################################

class DataInterfaceType:
    Base: "DataInterfaceType"
    Arrow: "DataInterfaceType"
    Numpy: "DataInterfaceType"
    Pandas: "DataInterfaceType"
    Polars: "DataInterfaceType"
    Sql: "DataInterfaceType"
    Torch: "DataInterfaceType"

class DataSaveKwargs:
    def __init__(
        self,
        data: Optional[Dict] = None,
    ) -> None:
        """Optional arguments to pass to save_model

        Args:
            data (Dict):
                Optional data arguments to use when saving model to onnx format
        """

    def __str__(self): ...
    def model_dump_json(self) -> str: ...
    @staticmethod
    def model_validate_json(json_string: str) -> "DataSaveKwargs": ...

class DataLoadKwargs:
    data: Optional[Dict]

    def __init__(
        self,
        data: Optional[Dict] = None,
    ) -> None:
        """Optional arguments to pass to load_model

        Args:
            data (Dict):
                Optional data arguments to use when loading

        """

class Inequality:
    Equal: "Inequality"
    GreaterThan: "Inequality"
    GreaterThanEqual: "Inequality"
    LesserThan: "Inequality"
    LesserThanEqual: "Inequality"

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
        column_type: ColType = ColType.Builtin,
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
                The type of the column. Defaults to ColType.Builtin. If providing ColtType.Timestamp, the
                column_value should be a float
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
    ) -> Dict[str, "Data"]:
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

class DataInterfaceSaveMetadata:
    data_uri: Path
    data_profile_uri: Optional[Path]
    sql_uri: Optional[Path]
    extra: Optional[ExtraMetadata]
    save_kwargs: DataSaveKwargs

    def __init__(
        self,
        data_uri: Path,
        data_profile_uri: Optional[Path] = None,
        sql_uri: Optional[Path] = None,
        extra: Optional[ExtraMetadata] = None,
        save_kwargs: Optional[DataSaveKwargs] = None,
    ) -> None:
        """Define interface save metadata

        Args:
            data_uri:
                The data uri
            data_profile_uri:
                The data profile uri
            sql_uri:
                The sql uri
            extra:
                Extra metadata
            save_kwargs:
                Save kwargs
        """

class DataInterfaceMetadata:
    save_metadata: DataInterfaceSaveMetadata
    schema: FeatureSchema
    extra_metadata: dict[str, str]
    sql_logic: "SqlLogic"  # pylint: disable=used-before-assignment
    interface_type: DataInterfaceType
    data_splits: DataSplits
    dependent_vars: DependentVars
    data_type: DataType

    def __init__(
        self,
        save_metadata: DataInterfaceSaveMetadata,
        schema: FeatureSchema,
        extra_metadata: dict[str, str],
        sql_logic: "SqlLogic",
        interface_type: DataInterfaceType,
        data_splits: DataSplits,
        dependent_vars: DependentVars,
        data_type: DataType,
    ) -> None:
        """Instantiate DataInterfaceMetadata object

        Args:
            save_metadata:
                The save metadata
            schema:
                The schema
            extra_metadata:
                Extra metadata
            sql_logic:
                Sql logic
            interface_type:
                The interface type
            data_splits:
                The data splits
            dependent_vars:
                Dependent variables
            data_type:
                The data type
        """

    def __str__(self) -> str:
        """Return the string representation of the model interface metadata"""

    def model_dump_json(self) -> str:
        """Dump the model interface metadata to json"""

    @staticmethod
    def model_validate_json(json_string: str) -> "DataInterfaceMetadata":
        """Validate the model interface metadata json"""

class DataInterface:
    def __init__(
        self,
        data: Optional[Any] = None,
        data_splits: Optional[Union[DataSplits, List[DataSplit]]] = None,
        dependent_vars: Optional[Union[DependentVars, List[str], List[int]]] = None,
        sql_logic: Optional["SqlLogic"] = None,
        data_profile: Optional[DataProfile] = None,
    ) -> None:
        """Define a data interface

        Args:
            data (Any):
                Data. Can be a pyarrow table, pandas dataframe, polars dataframe
                or numpy array
            dependent_vars (DependentVars):
                List of dependent variables to associate with data
            data_splits (DataSplits):
                Optional list of `DataSplit`
            sql_logic (SqlLogic):
                SqlLogic class used to generate data.
            data_profile (DataProfile):
                Data profile
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
    def schema(self) -> FeatureSchema:
        """Returns the feature map."""

    @schema.setter
    def schema(self, schema: FeatureSchema) -> None:
        """Sets the feature map"""

    @property
    def sql_logic(self) -> "SqlLogic":
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

    def save(
        self,
        path: Path,
        save_kwargs: Optional[DataSaveKwargs] = None,
    ) -> DataInterfaceMetadata:
        """Saves all data interface component to the given path. This used as part of saving a
        DataCard

        Methods called in save:
            - save_sql: Saves all sql logic to files(s)
            - create_schema: Creates a FeatureSchema from the associated data
            - save_data: Saves the data to a file

        Args:
            path (Path):
                The path to save the data interface components to.
            save_kwargs (DataSaveKwargs):
                The save kwargs to use.

        """

    def load(
        self,
        path: Path,
        metadata: DataInterfaceSaveMetadata,
        load_kwargs: Optional[DataLoadKwargs] = None,
    ) -> None:
        """Load the data from a file

        Args:
            path (Path):
                Base path to load the data from
            metadata (DataInterfaceSaveMetadata):
                Metadata associated with the data
            load_kwargs (DataLoadKwargs):
                Additional kwargs to pass in.
        """

    def split_data(self) -> Dict[str, Data]:
        """Split the data

        Returns:
            A dictionary of data splits
        """

    def create_data_profile(
        self,
        bin_size: Optional[int] = 20,
        compute_correlations: Optional[bool] = False,
    ) -> DataProfile:
        """Create a data profile


        Args:
            bin_size (int):
                The bin size for the data profile
            compute_correlations (bool):
                Whether to compute correlations
        """

    @property
    def data_profile(self) -> Optional[DataProfile]:
        """Return the data profile

        Returns:
            The data profile
        """

    @data_profile.setter
    def data_profile(self, data_profile: Optional[DataProfile]) -> None:
        """Set the data profile

        Args:
            data_profile (DataProfile | None):
                The data profile to set
        """

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

class NumpyData(DataInterface):
    def __init__(
        self,
        data: Optional[Any] = None,
        data_splits: Optional[Union[DataSplits, List[DataSplit]]] = None,
        dependent_vars: Optional[Union[DependentVars, List[str], List[int]]] = None,
        sql_logic: Optional[SqlLogic] = None,
        data_profile: Optional[DataProfile] = None,
    ) -> None:
        """Define a data interface

        Args:
            data (np.NDArray | None):
                Numpy array
            dependent_vars (DependentVars | List[str] | List[int] | None):
                List of dependent variables to associate with data
            data_splits (DataSplits | List[DataSplit]):
                Optional list of `DataSplit`
            sql_logic (SqlLogic | None):
                Sql logic used to generate data represented as a dictionary.
            data_profile (DataProfile | None):
                Data profile
        """

    def save(
        self,
        path: Path,
        save_kwargs: Optional[DataSaveKwargs] = None,
    ) -> DataInterfaceMetadata:
        """Save data using numpy save format

        Args:
            path (Path):
                Base path to save the data to.
            save_kwargs (DataSaveKwargs):
                Additional kwargs to pass in.

        Acceptable save kwargs:

            see: https://numpy.org/doc/stable/reference/generated/numpy.save.html

            allow_pickle (bool):
                Allow saving object arrays using Python pickles.
            fix_imports (bool):
                The fix_imports flag is deprecated and has no effect

        """

    def load(
        self,
        path: Path,
        metadata: DataInterfaceSaveMetadata,
        load_kwargs: Optional[DataLoadKwargs] = None,
    ) -> None:
        """Load the data via numpy.load

        Args:
            path (Path):
                Base path to load the data from.
            metadata (DataInterfaceSaveMetadata):
                Metadata associated with the data
            load_kwargs (DataLoadKwargs):
                Additional kwargs to use when loading

        Acceptable load kwargs:

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
        sql_logic: Optional[SqlLogic] = None,
        data_profile: Optional[DataProfile] = None,
    ) -> None:
        """Define a data interface

        Args:
            data (pl.DataFrame | None):
                Pandas dataframe
            dependent_vars (DependentVars | List[str] | List[int] | None):
                List of dependent variables to associate with data
            data_splits (DataSplits | List[DataSplit]):
                Optional list of `DataSplit`
            sql_logic (SqlLogic | None):
                Sql logic used to generate data represented as a dictionary.
            data_profile (DataProfile | None):
                Data profile

        """

    def save(self, path: Path, save_kwargs: Optional[DataSaveKwargs] = None) -> DataInterfaceMetadata:
        """Saves polars dataframe to parquet dataset via write_parquet

        Args:
            path (Path):
                Base path to save the data to.
            save_kwargs (DataSaveKwargs):
                Additional kwargs to pass in.

        Acceptable save kwargs:
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

    def load(
        self,
        path: Path,
        metadata: DataInterfaceSaveMetadata,
        load_kwargs: Optional[DataLoadKwargs] = None,
    ) -> None:
        """Load the data from a file

        Args:
            path (Path):
                Base path to load the data from.
            metadata (DataInterfaceSaveMetadata):
                Metadata associated with the data
            load_kwargs (DataLoadKwargs):
                Additional kwargs to pass in.

        Acceptable load kwargs:
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
        sql_logic: Optional[SqlLogic] = None,
        data_profile: Optional[DataProfile] = None,
    ) -> None:
        """Define a data interface

        Args:
            data (pd.DataFrame | None):
                Pandas dataframe
            dependent_vars (DependentVars | List[str] | List[int] | None):
                List of dependent variables to associate with data
            data_splits (DataSplits | List[DataSplit]):
                Optional list of `DataSplit`
            sql_logic (SqlLogic | None):
                Sql logic used to generate data represented as a dictionary.
            data_profile (DataProfile | None):
                Data profile
        """

    def save(self, path: Path, save_kwargs: Optional[DataSaveKwargs] = None) -> DataInterfaceMetadata:
        """Saves pandas dataframe as parquet file via to_parquet

        Args:
            path (Path):
                Base path to save the data to.
            save_kwargs (DataSaveKwargs):
                Additional kwargs to pass in.

        Acceptable save kwargs:
            engine ({'auto', 'pyarrow', 'fastparquet'}):
                Parquet library to use. If 'auto', then the option io.parquet.engine is used.
                The default io.parquet.engine behavior is to try 'pyarrow',
                falling back to 'fastparquet' if 'pyarrow' is unavailable. Default is 'auto'.
            compression (str | None):
                Name of the compression to use. Use None for no compression.
                Supported options: 'snappy', 'gzip', 'brotli', 'lz4', 'zstd'. Default is 'snappy'.
            index (bool | None):
                If True, include the dataframe's index(es) in the file output.
                If False, they will not be written to the file. If None, similar to True the dataframe's index(es) will be saved.
                However, instead of being saved as values, the RangeIndex will be stored as a range in the metadata so it doesn't
                require much space and is faster.
                Other indexes will be included as columns in the file output. Default is None.
            partition_cols (list | None):
                Column names by which to partition the dataset. Columns are partitioned in the order they are given.
                Must be None if path is not a string. Default is None.
            storage_options (dict | None):
                Extra options that make sense for a particular storage connection, e.g. host, port, username, password, etc.
                For HTTP(S) URLs the key-value pairs are forwarded to urllib.request.Request as header options.
                For other URLs (e.g. starting with “s3://”, and “gcs://”) the key-value pairs are forwarded to fsspec.open.
                Default is None.
            **kwargs:
                Any additional kwargs are passed to the engine

        Additional Information:
            https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_parquet.html
        """

    def load(
        self,
        path: Path,
        metadata: DataInterfaceSaveMetadata,
        load_kwargs: Optional[DataLoadKwargs] = None,
    ) -> None:
        """Load the pandas dataframe from a parquet dataset via read_parquet

        Args:
            path (Path):
                Base path to load the data from.
            metadata (DataInterfaceSaveMetadata):
                Metadata associated with the data
            load_kwargs (DataLoadKwargs):
                Additional kwargs to pass in.

        Acceptable load kwargs:
            engine ({'auto', 'pyarrow', 'fastparquet'}):
                Parquet library to use. If 'auto', then the option io.parquet.engine is used.
                The default io.parquet.engine behavior is to try 'pyarrow',
                falling back to 'fastparquet' if 'pyarrow' is unavailable. Default is 'auto'.
            columns (list | None):
                If not None, only these columns will be read from the file. Default is None.
            storage_options (dict | None):
                Extra options that make sense for a particular storage connection, e.g. host, port, username, password, etc.
                For HTTP(S) URLs the key-value pairs are forwarded to urllib.request.Request as header options.
                For other URLs (e.g. starting with “s3://”, and “gcs://”) the key-value pairs are forwarded to fsspec.open.
                Default is None.
            use_nullable_dtypes (bool):
                If True, use dtypes that use pd.NA as missing value indicator for the resulting DataFrame.
                (only applicable for the pyarrow engine) As new dtypes are added that support pd.NA in the future,
                the output with this option will change to use those dtypes.
                Note: this is an experimental option, and behaviour (e.g. additional support dtypes) may change without notice.
                Default is False. Deprecated since version 2.0.
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
                The outer list combines these sets of filters through an OR operation. A single list of tuples can also be used,
                meaning that no OR operation between set of filters is to be conducted.
                Using this argument will NOT result in row-wise filtering of the final partitions unless engine="pyarrow"
                is also specified.
                For other engines, filtering is only performed at the partition level, that is,
                to prevent the loading of some row-groups and/or files. Default is None.
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
        sql_logic: Optional[SqlLogic] = None,
        data_profile: Optional[DataProfile] = None,
    ) -> None:
        """Define a data interface

        Args:
             data (pa.Table | None):
                PyArrow Table
            dependent_vars (DependentVars | List[str] | List[int] | None):
                List of dependent variables to associate with data
            data_splits (DataSplits | List[DataSplit]):
                Optional list of `DataSplit`
            sql_logic (SqlLogic | None):
                Sql logic used to generate data represented as a dictionary.
            data_profile (DataProfile | None):
                Data profile
        """

    def save(self, path: Path, save_kwargs: Optional[DataSaveKwargs] = None) -> DataInterfaceMetadata:
        """Saves pyarrow table to parquet via write_table

        Args:
            path (Path):
                Base path to save the data to.
            save_kwargs (DataSaveKwargs):
                Additional kwargs to pass in.

        Acceptable save kwargs:
            row_group_size (int | None):
                Maximum number of rows in each written row group. If None, the row group size will be the minimum of the
                Table size and 1024 * 1024. Default is None.
            version ({'1.0', '2.4', '2.6'}):
                Determine which Parquet logical types are available for use. Default is '2.6'.
            use_dictionary (bool | list):
                Specify if dictionary encoding should be used in general or only for some columns. Default is True.
            compression (str | dict):
                Specify the compression codec, either on a general basis or per-column.
                Valid values: {'NONE', 'SNAPPY', 'GZIP', 'BROTLI', 'LZ4', 'ZSTD'}. Default is 'snappy'.
            write_statistics (bool | list):
                Specify if statistics should be written in general or only for some columns. Default is True.
            use_deprecated_int96_timestamps (bool | None):
                Write timestamps to INT96 Parquet format. Default is None.
            coerce_timestamps (str | None):
                Cast timestamps to a particular resolution. Valid values: {None, 'ms', 'us'}. Default is None.
            allow_truncated_timestamps (bool):
                Allow loss of data when coercing timestamps to a particular resolution. Default is False.
            data_page_size (int | None):
                Set a target threshold for the approximate encoded size of data pages within a column chunk (in bytes).
                Default is None.
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

    def load(
        self,
        path: Path,
        metadata: DataInterfaceSaveMetadata,
        load_kwargs: Optional[DataLoadKwargs] = None,
    ) -> None:
        """Load the data from a file

        Args:
            path (Path):
                Base path to load the data from.
            metadata (DataInterfaceSaveMetadata):
                Metadata associated with the data
            load_kwargs (DataLoadKwargs):
                Additional kwargs to pass in.

        Acceptable load kwargs:
            columns (list | None):
                If not None, only these columns will be read from the file. A column name may be a prefix of a nested field,
                e.g. 'a' will select 'a.b', 'a.c', and 'a.d.e'. If empty, no columns will be read. Default is None.
            use_threads (bool):
                Perform multi-threaded column reads. Default is True.
            schema (Schema | None):
                Optionally provide the Schema for the parquet dataset, in which case it will not be inferred from the source.
                Default is None.
            use_pandas_metadata (bool):
                If True and file has custom pandas schema metadata, ensure that index columns are also loaded. Default is False.
            read_dictionary (list | None):
                List of names or column paths (for nested types) to read directly as DictionaryArray.
                Only supported for BYTE_ARRAY storage. Default is None.
            memory_map (bool):
                If the source is a file path, use a memory map to read file, which can improve performance in some environments.
                Default is False.
            buffer_size (int):
                If positive, perform read buffering when deserializing individual column chunks.
                Otherwise IO calls are unbuffered. Default is 0.
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
                Coalesce and issue file reads in parallel to improve performance on high-latency filesystems (e.g. S3).
                Default is True.
            coerce_int96_timestamp_unit (str | None):
                Cast timestamps that are stored in INT96 format to a particular resolution (e.g. 'ms'). Default is None.
            decryption_properties (FileDecryptionProperties | None):
                File-level decryption properties. Default is None.
            thrift_string_size_limit (int | None):
                If not None, override the maximum total string size allocated when decoding Thrift structures. Default is None.
            thrift_container_size_limit (int | None):
                If not None, override the maximum total size of containers allocated when decoding Thrift structures.
                Default is None.
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
        sql_logic: Optional[SqlLogic] = None,
        data_profile: Optional[DataProfile] = None,
    ) -> None:
        """Define a data interface

        Args:
            data (torch.Tensor | None):
                Torch tensor
            dependent_vars (DependentVars | List[str] | List[int] | None):
                List of dependent variables to associate with data
            data_splits (DataSplits | List[DataSplit]):
                Optional list of `DataSplit`
            sql_logic (SqlLogic | None):
                Sql logic used to generate data represented as a dictionary.
            data_profile (DataProfile | None):
                Data profile
        """

    def save(self, path: Path, save_kwargs: Optional[DataSaveKwargs] = None) -> DataInterfaceMetadata:
        """Saves torch tensor to a file

        Args:
            path (Path):
                Base path to save the data to.
            save_kwargs (DataSaveKwargs):
                Additional kwargs to pass in.

        Acceptable save kwargs:
            pickle_module (Any):
                Module used for pickling metadata and objects.
            pickle_protocol (int):
                Can be specified to override the default protocol.


        Additional Information:
           https://pytorch.org/docs/main/generated/torch.save.html
        """

    def load(
        self,
        path: Path,
        metadata: DataInterfaceSaveMetadata,
        load_kwargs: Optional[DataLoadKwargs] = None,
    ) -> None:
        """Load the torch tensor from file

        Args:
            path (Path):
                Base path to load the data from.
            metadata (DataInterfaceSaveMetadata):
                Metadata associated with the data
            load_kwargs (DataLoadKwargs):
                Additional kwargs to pass in.

        Acceptable load kwargs:
            map_location:
                A function, torch.device, string or a dict specifying how to remap storage locations.
            pickle_module:
                Module used for unpickling metadata and objects (has to match the pickle_module used to serialize file).
            weights_only:
                Indicates whether unpickler should be restricted to loading only tensors, primitive types,
                dictionaries and any types added via torch.serialization.add_safe_globals().
            mmap:
                Indicates whether the file should be mmaped rather than loading all the storages into memory.
                Typically, tensor storages in the file will first be moved from disk to CPU memory,
                after which they are moved to the location that they were tagged with when saving, or specified by map_location.
                This second step is a no-op if the final location is CPU. When the mmap flag is set,
                instead of copying the tensor storages from disk to CPU memory in the first step, f is mmaped.
            pickle_load_args:
                (Python 3 only) optional keyword arguments passed over to pickle_module.load() and pickle_module.Unpickler(),
                e.g., errors=....


        Additional Information:
            https://pytorch.org/docs/stable/generated/torch.load.html
        """

class SqlData:
    data_type: DataType

    def __init__(
        self,
        sql_logic: SqlLogic,
        data_profile: Optional[DataProfile] = None,
    ) -> None:
        """Define a sql data interface

        Args:
            sql (SqlLogic):
                Sql logic used to generate data represented as a dictionary.
            data_profile (DataProfile | None):
                Data profile
        """

    def save(
        self,
        path: Path,
        save_kwargs: Optional[DataSaveKwargs] = None,
    ) -> DataInterfaceMetadata:
        """Save the sql logic to a file

        Args:
            path (Path):
                The path to save the sql logic to.
            save_kwargs (DataSaveKwargs):
                Additional kwargs to pass in.
        """

def generate_feature_schema(data: Any, data_type: DataType) -> FeatureSchema:
    """Generate a feature schema

    Args:
        data:
            Data to generate the feature schema from
        data_type:
            The data type

    Returns:
        A feature map
    """

########################################################################################
#  This section contains the type definitions for opsml.model module
# __opsml.model__
# ######################################################################################
DriftProfileType = Dict[str, Union[SpcDriftProfile | PsiDriftProfile | CustomDriftProfile]]

class ProcessorType:
    Preprocessor: "ProcessorType"
    Tokenizer: "ProcessorType"
    FeatureExtractor: "ProcessorType"
    ImageProcessor: "ProcessorType"

# Utils

class OnnxSchema:
    def __init__(
        self,
        input_features: FeatureSchema,
        output_features: FeatureSchema,
        onnx_version: str,
        feature_names: Optional[List[str]] = None,
    ) -> None:
        """Define an onnx schema

        Args:
            input_features (FeatureSchema):
                The input features of the onnx schema
            output_features (FeatureSchema):
                The output features of the onnx schema
            onnx_version (str):
                The onnx version of the schema
            feature_names (List[str] | None):
                The feature names and order for onnx.

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

class PromptSaveKwargs:
    """Additional kwargs to pass when registering a PromptCard"""

    def __init__(
        self,
        drift: DriftArgs,
    ) -> None:
        """Optional arguments to pass to save_prompt

        Args:
            drift (DriftArgs):
                Drift args to use when saving and registering a prompt.
        """

class ModelSaveKwargs:
    def __init__(
        self,
        onnx: Optional[Dict | "HuggingFaceOnnxArgs"] = None,
        model: Optional[Dict] = None,
        preprocessor: Optional[Dict] = None,
        save_onnx: bool = False,
        drift: Optional[DriftArgs] = None,
    ) -> None:
        """Optional arguments to pass to save_model

        Args:
            onnx (Dict or HuggingFaceOnnxArgs):
                Optional onnx arguments to use when saving model to onnx format
            model (Dict):
                Optional model arguments to use when saving. This is a pass-through that will
                be directly injected as kwargs to the underlying library's save method. For instance,
                pytorch models are saved with `torch.save` so any kwargs that torch.save supports can be
                used here.
            preprocessor (Dict):
                Optional preprocessor arguments to use when saving
            save_onnx (bool):
                Whether to save the onnx model. Defaults to false. This is independent of the
                onnx argument since it's possible to convert a model to onnx without additional kwargs.
                If onnx args are provided, this will be set to true.
            drift (DriftArgs):
                Optional drift args to use when saving and registering a model.
        """

    def __str__(self): ...
    def model_dump_json(self) -> str: ...
    @staticmethod
    def model_validate_json(json_string: str) -> "ModelSaveKwargs": ...

class ModelLoadKwargs:
    onnx: Optional[Dict]
    model: Optional[Dict]
    preprocessor: Optional[Dict]
    load_onnx: bool

    def __init__(
        self,
        onnx: Optional[Dict] = None,
        model: Optional[Dict] = None,
        preprocessor: Optional[Dict] = None,
        load_onnx: bool = False,
    ) -> None:
        """Optional arguments to pass to load_model

        Args:
            onnx (Dict):
                Optional onnx arguments to use when loading
            model (Dict):
                Optional model arguments to use when loading
            preprocessor (Dict):
                Optional preprocessor arguments to use when loading
            load_onnx (bool):
                Whether to load the onnx model. Defaults to false unless onnx args are
                provided. If true, the onnx model will be loaded.

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
    """Generic class that holds uri information for data preprocessors and postprocessors"""

    name: str
    uri: Path
    type: ProcessorType

    def __init__(self, name: str, uri: Path) -> None:
        """Define a data processor

        Args:
            name:
                Name of the data processor
            uri:
                Path to the data processor
        """

    def __str__(self): ...

# Define interface save and metadata arguments
class ModelInterfaceSaveMetadata:
    model_uri: Path
    data_processor_map: Dict[str, DataProcessor]
    sample_data_uri: Path
    onnx_model_uri: Optional[Path]
    drift_profile_uri_map: Optional[Dict[str, DriftProfileUri]]
    extra: Optional[ExtraMetadata]
    save_kwargs: Optional[ModelSaveKwargs]

    def __init__(
        self,
        model_uri: Path,
        data_processor_map: Optional[Dict[str, DataProcessor]] = {},  # type: ignore
        sample_data_uri: Optional[Path] = None,
        onnx_model_uri: Optional[Path] = None,
        drift_profile_uri_map: Optional[Dict[str, DriftProfileUri]] = None,
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
            drift_profile_uri_map:
                Dictionary of drift profiles
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
    Undefined: "TaskType"

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
        input_feed: Dict[str, Any],
        output_names: Optional[list[str]] = None,
        run_options: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Run the onnx session

        Args:
            input_feed:
                Dictionary of input data
            output_names:
                List of output names
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
    version: str

    def __init__(
        self,
        save_metadata: ModelInterfaceSaveMetadata,
        task_type: TaskType = TaskType.Undefined,
        model_type: ModelType = ModelType.Unknown,
        data_type: DataType = DataType.NotProvided,
        schema: FeatureSchema = FeatureSchema(),
        onnx_session: Optional[OnnxSession] = None,
        extra_metadata: dict[str, str] = {},  # type: ignore
        version: str = "undefined",
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
            version:
                Package version of the model being used (sklearn.__version__, torch.__version__, etc)
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
        model: Any = None,
        sample_data: Any = None,
        task_type: Optional[TaskType] = None,
        drift_profile: Optional[DriftProfileType] = None,
    ) -> None:
        """Base class for ModelInterface

        Args:
            model:
                Model to associate with interface.
            sample_data:
                Sample data to use to make predictions
            task_type:
                The type of task the model performs
            drift_profile:
                Drift profile(s) to associate with the model. Must be a dictionary of
                alias and drift profile.
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
    ) -> DriftProfileMap:
        """Returns the drift profile mapping"""

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
        alias: str,
        data: CustomMetric | List[CustomMetric],
        config: CustomMetricDriftConfig,
        data_type: Optional[DataType] = None,
    ) -> CustomDriftProfile: ...
    @overload
    def create_drift_profile(
        self,
        alias: str,
        data: Any,
        config: SpcDriftConfig,
        data_type: Optional[DataType] = None,
    ) -> SpcDriftProfile: ...
    @overload
    def create_drift_profile(
        self,
        alias: str,
        data: Any,
        config: PsiDriftConfig,
        data_type: Optional[DataType] = None,
    ) -> PsiDriftProfile: ...
    @overload
    def create_drift_profile(
        self,
        alias: str,
        data: Any,
        data_type: Optional[DataType] = None,
    ) -> SpcDriftProfile: ...
    def create_drift_profile(  # type: ignore
        self,
        alias: str,
        data: Any,
        config: None | SpcDriftConfig | PsiDriftConfig | CustomMetricDriftConfig = None,
        data_type: None | DataType = None,
    ) -> Any:
        """Create a drift profile and append it to the drift profile list

        Args:
            alias:
                Alias to use for the drift profile
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
        save_kwargs: None | ModelSaveKwargs = None,
    ) -> ModelInterfaceMetadata:
        """Save the model interface

        Args:
            path (Path):
                Path to save the model
            save_kwargs (ModelSaveKwargs):
                Optional kwargs to pass to the various underlying methods. This is a passthrough object meaning
                that the kwargs will be passed to the underlying methods as is and are expected to be supported by
                the underlying library.

                - model: Kwargs that will be passed to save_model. See save_model for more details.
                - preprocessor: Kwargs that will be passed to save_preprocessor
                - onnx: Library specific kwargs to pass to the onnx conversion. Independent of save_onnx.
                - save_onnx: Whether to save the onnx model. Defaults to false.
        """

    def load(
        self,
        path: Path,
        metadata: ModelInterfaceSaveMetadata,
        load_kwargs: None | ModelLoadKwargs = None,
    ) -> None:
        """Load ModelInterface components

        Args:
            path (Path):
                Path to load the model
            metadata (ModelInterfaceSaveMetadata):
                Metadata to use to load the model
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
    """OpsML interface for scikit-learn models"""

    def __init__(
        self,
        model: Optional[Any] = None,
        preprocessor: Optional[Any] = None,
        sample_data: Optional[Any] = None,
        task_type: Optional[TaskType] = None,
        drift_profile: Optional[DriftProfileType] = None,
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
            drift_profile:
                Drift profile(s) to associate with the model. Must be a dictionary of
                alias and drift profile.
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
        drift_profile: Optional[DriftProfileType] = None,
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
            drift_profile:
                Drift profile(s) to associate with the model. Must be a dictionary of
                alias and drift profile.
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
        drift_profile: Optional[DriftProfileType] = None,
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
            drift_profile:
                Drift profile(s) to associate with the model. Must be a dictionary of
                alias and drift profile.
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
        drift_profile: Optional[DriftProfileType] = None,
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
            drift_profile:
                Drift profile(s) to associate with the model. Must be a dictionary of
                alias and drift profile.
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
        save_kwargs: None | ModelSaveKwargs = None,
    ) -> ModelInterfaceMetadata:
        """Save the TorchModel interface. Torch models are saved
        as state_dicts as is the standard for PyTorch.

        Args:
            path (Path):
                Base path to save artifacts
            save_kwargs (ModelSaveKwargs):
                Optional kwargs to pass to the various underlying methods. This is a passthrough object meaning
                that the kwargs will be passed to the underlying methods as is and are expected to be supported by
                the underlying library.
        """

class LightningModel(ModelInterface):
    def __init__(
        self,
        trainer: Optional[Any] = None,
        preprocessor: Optional[Any] = None,
        sample_data: Optional[Any] = None,
        task_type: Optional[TaskType] = None,
        drift_profile: Optional[DriftProfileType] = None,
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
            drift_profile:
                Drift profile(s) to associate with the model. Must be a dictionary of
                alias and drift profile.
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
        save_kwargs: None | ModelSaveKwargs = None,
    ) -> ModelInterfaceMetadata:
        """Save the LightningModel interface. Lightning models are saved via checkpoints.

        Args:
            path (Path):
                Base path to save artifacts
            save_kwargs (ModelSaveKwargs):
                Optional kwargs to pass to the various underlying methods. This is a passthrough object meaning
                that the kwargs will be passed to the underlying methods as is and are expected to be supported by
                the underlying library.

                - model: Kwargs that will be passed to save_model. See save_model for more details.
                - preprocessor: Kwargs that will be passed to save_preprocessor
                - onnx: Library specific kwargs to pass to the onnx conversion. Independent of save_onnx.
                - save_onnx: Whether to save the onnx model. Defaults to false.
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
        drift_profile: Optional[DriftProfileType] = None,
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
            drift_profile:
                Drift profile(s) to associate with the model. Must be a dictionary of
                alias and drift profile.
        """

    def save(
        self,
        path: Path,
        save_kwargs: None | ModelSaveKwargs = None,
    ) -> ModelInterfaceMetadata:
        """Save the HuggingFaceModel interface

        Args:
            path (Path):
                Base path to save artifacts
            save_kwargs (ModelSaveKwargs):
                Optional kwargs to pass to the various underlying methods. This is a passthrough object meaning
                that the kwargs will be passed to the underlying methods as is and are expected to be supported by
                the underlying library.

                - model: Kwargs that will be passed to save_model. See save_model for more details.
                - preprocessor: Kwargs that will be passed to save_preprocessor
                - onnx: Kwargs that will be passed when saving the onnx model
                    - For the HuggingFaceModel, this should be an instance of HuggingFaceOnnxArgs
                - save_onnx: Whether to save the onnx model. Defaults to false.
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
        drift_profile: Optional[DriftProfileType] = None,
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
            drift_profile:
                Drift profile(s) to associate with the model. Must be a dictionary of
                alias and drift profile.
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
        drift_profile: Optional[DriftProfileType] = None,
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
            drift_profile:
                Drift profile(s) to associate with the model. Must be a dictionary of
                alias and drift profile.
        """

    @property
    def preprocessor(self) -> Optional[Any]:
        """Returns the preprocessor"""

    @preprocessor.setter
    def preprocessor(self, preprocessor: Any) -> None:
        """Sets the preprocessor

        Args:
            preprocessor:
                Preprocessor to associate with the model
        """

    @property
    def preprocessor_name(self) -> Optional[str]:
        """Returns the preprocessor name"""

class OnnxModel(ModelInterface):
    def __init__(
        self,
        model: Optional[Any] = None,
        sample_data: Optional[Any] = None,
        task_type: Optional[TaskType] = None,
        drift_profile: Optional[DriftProfileType] = None,
    ) -> None:
        """Interface for saving an OnnxModel

        Args:
            model:
                Onnx model to associate with the interface. This model must be an Onnx ModelProto
            sample_data:
                Sample data to use to make predictions
            task_type:
                The type of task the model performs
            drift_profile:
                Drift profile(s) to associate with the model. Must be a dictionary of
                alias and drift profile.

        Example:
            ```python
            from sklearn.datasets import load_iris  # type: ignore
            from sklearn.model_selection import train_test_split  # type: ignore
            from sklearn.ensemble import RandomForestClassifier  # type: ignore
            from skl2onnx import to_onnx  # type: ignore
            import onnxruntime as rt  # type: ignore

            iris = load_iris()

            X, y = iris.data, iris.target
            X = X.astype(np.float32)
            X_train, X_test, y_train, y_test = train_test_split(X, y)
            clr = RandomForestClassifier()
            clr.fit(X_train, y_train)

            onx = to_onnx(clr, X[:1])

            interface = OnnxModel(model=onx, sample_data=X_train)
            ```
        """

    @property
    def session(self) -> OnnxSession:
        """Returns the onnx session. This will error if the OnnxSession is not set"""

########################################################################################
#  This section contains the type definitions for opsml.app module
# __opsml.app__
# ######################################################################################

class ReloadConfig:
    """Reload configuation to use with an Opsml AppState object. Defines the reload logic
    for checking, downloading and reloading ServiceCards and ScouterQueues associated with
    an AppState
    """

    def __init__(
        self,
        cron: str,
        max_retries: int = 3,
        write_path: Optional[Path] = None,
    ):
        """Initialize the reload configuration.

        Args:
            cron (str):
                The cron expression for the reload schedule.
            max_retries (int):
                The maximum number of retries for loading the service card.
                Defaults to 3.
            write_path (Optional[Path]):
                The optional path to write the service card. Defaults to Path({current directory})/ service_reload
        """

    @property
    def cron(self) -> str:
        """Get the cron expression for the reload schedule."""

    @cron.setter
    def cron(self, value: str):
        """Set the cron expression for the reload schedule."""

class AppState:
    """OpsML application state object. This is typically used in API
    workflows where you wish create a shared state to share among all requests.
    The OpsML app state provides a convenient way to load and store artifacts.
    Most notably, it provides an integration with Scouter so that you can load a `ServiceCard`
    along with a `ScouterQueue` for drift detection. Future iterations of this class may
    include other convenience methods that simplify common API tasks.
    """

    @staticmethod
    def from_path(
        path: Path,
        transport_config: Optional[
            Union[
                KafkaConfig,
                RabbitMQConfig,
                RedisConfig,
                HttpConfig,
            ]
        ] = None,
        reload_config: Optional[ReloadConfig] = None,
        load_kwargs: Optional[Dict[str, Dict[str, Any]]] = None,
    ) -> "AppState":
        """
        Load the AppState from a file path.

        Args:
            path (str):
                The file path to load the AppState from. This is typically the path
                pointing to the directory containing the `ServiceCard`.

            transport_config (KafkaConfig | RabbitMQConfig | RedisConfig | HttpConfig | None):
                Optional transport configuration for the queue publisher
                Can be KafkaConfig, RabbitMQConfig RedisConfig, or HttpConfig. If not provided,
                the queue will not be initialized.

            reload_config (ReloadConfig | None):
                Optional reload configuration for the AppState. If provided,
                the AppState will periodically check for updates to the ServiceCard
                and reload it if necessary.

            load_kwargs (Dict[str, Dict[str, Any]]):
                Optional kwargs for loading cards. Expected format:
                {
                    "card_alias": {
                        "interface": interface_object,
                        "load_kwargs": DataLoadKwargs | ModelLoadKwargs
                    }
                }

        Example:
            ```python
            from opsml.app import AppState
            from opsml.scouter import KafkaConfig

            app_state = AppState.from_path(
                "/path/to/service",
                transport_config=KafkaConfig(),
                )

            # Access the service card and queue
            service = app_state.service
            queue = app_state.queue
            ```

        Returns:
            AppState: The loaded AppState.
        """

    @property
    def service(self) -> ServiceCard:
        """Get the service card."""

    @property
    def queue(self) -> ScouterQueue:
        """Get the Scouter queue."""

    @property
    def reloader_running(self) -> bool:
        """Check if the ServiceReloader is currently running."""

    def reload(self) -> None:
        """Forces `AppState` to check for new `ServiceCards` and reload if necessary."""

    def start_reloader(self) -> None:
        """Starts the `AppState` reloader."""

    def stop_reloader(self) -> None:
        """Stops the `AppState` reloader."""

    def shutdown(self) -> None:
        """Shuts down the `AppState` `ScouterQueue` and reloader if running.
        This is a destructive operation and will attempt to close all background threads
        associated with the `ScouterQueue` and reloader. Only use this method with graceful
        shutdown procedures in mind.
        """

########################################################################################
#  This section contains the type definitions for the opsmlspec file
# ######################################################################################

class SpaceConfig:
    """Configuration for service space or team designation.

    A service must belong to either a space or a team (mutually exclusive).
    """

    def __init__(self, space: Optional[str] = None, team: Optional[str] = None):
        """Initialize space configuration.

        Args:
            space: Space name for general use
            team: Team name for team-based organization

        Raises:
            ValueError: If both or neither space and team are provided
        """

    @property
    def space(self) -> Optional[str]:
        """Return the space name if this is a space-based config."""

    @property
    def team(self) -> Optional[str]:
        """Return the team name if this is a team-based config."""

class ServiceMetadata:
    def __init__(
        self,
        description: str,
        language: Optional[str] = None,
        tags: List[str] = [],
    ):
        """Initialize service metadata.

        Args:
            description:
                Description of the service (required)
            language:
                Programming language used (e.g., 'python'). Defaults to None
            tags:
                Tags for categorization and search. Defaults to empty list
        """

    @property
    def description(self) -> str:
        """Service description."""

    @property
    def language(self) -> Optional[str]:
        """Programming language used by the service."""

    @property
    def tags(self) -> List[str]:
        """Tags for categorization."""

class ServiceConfig:
    def __init__(
        self,
        version: Optional[str] = None,
        cards: Optional[List[Card]] = None,
        write_dir: Optional[str] = None,
        mcp: Optional[McpConfig] = None,
        agent: Optional[AgentSpec] = None,
    ):
        """Initialize service configuration.

        Args:
            version:
                Version of the service. Defaults to None
            cards:
                List of cards included in the service. Defaults to None
            write_dir:
                Directory to write service artifacts to. Defaults to 'opsml_service'
            mcp:
                MCP configuration (required if service type is Mcp). Defaults to None
            agent:
                Agent specification (required if service type is Agent). Defaults to None
        """

    @property
    def version(self) -> Optional[str]:
        """Service version."""

    @property
    def cards(self) -> Optional[List[Card]]:
        """Cards included in this service."""

    @property
    def write_dir(self) -> Optional[str]:
        """Directory for writing service artifacts."""

    @property
    def mcp(self) -> Optional[McpConfig]:
        """MCP configuration if service type is Mcp."""

    @property
    def agent(self) -> Optional[AgentSpec]:
        """Agent specification if service type is Agent."""

class GpuConfig:
    def __init__(
        self,
        gpu_type: str,
        count: int,
        memory: str,
    ):
        """Initialize GPU resource configuration.

        Args:
            gpu_type:
                GPU type identifier (e.g., 'nvidia-tesla-t4')
            count:
                Number of GPUs required
            memory:
                GPU memory per device (e.g., '16Gi')

        Raises:
            ValueError: If count is not positive or memory format is invalid
        """

    @property
    def gpu_type(self) -> str:
        """GPU type identifier."""

    @property
    def count(self) -> int:
        """Number of GPUs."""

    @property
    def memory(self) -> str:
        """GPU memory specification."""

class Resources:
    def __init__(
        self,
        cpu: int,
        memory: str,
        storage: str,
        gpu: Optional[GpuConfig] = None,
    ):
        """Initialize resource requirements for deployment.

        Args:
            cpu:
                Number of CPUs required
            memory:
                Amount of memory (e.g., '16Gi')
            storage:
                Storage capacity (e.g., '100Gi')
            gpu:
                GPU configuration if GPU resources are needed. Defaults to None

        Raises:
            ValueError: If cpu is not positive or memory/storage format is invalid
        """

    @property
    def cpu(self) -> int:
        """Number of CPUs required."""

    @property
    def memory(self) -> str:
        """Memory requirement specification."""

    @property
    def storage(self) -> str:
        """Storage requirement specification."""

    @property
    def gpu(self) -> Optional[GpuConfig]:
        """GPU configuration if enabled."""

class DeploymentConfig:
    def __init__(
        self,
        environment: str,
        endpoints: List[str],
        provider: Optional[str] = None,
        location: Optional[List[str]] = None,
        resources: Optional[Resources] = None,
        links: Optional[Dict[str, str]] = None,
    ):
        """Initialize deployment configuration.

        Args:
            environment:
                Deployment environment (e.g., 'development', 'production')
            endpoints:
                List of endpoint URLs for the deployed service
            provider:
                Cloud provider (e.g., 'gcp', 'aws'). Defaults to None
            location:
                Deployment locations/regions. Defaults to None
            resources:
                Resource requirements for deployment. Defaults to None
            links:
                Related links (e.g., logging, monitoring URLs). Defaults to None

        Raises:
            ValueError: If endpoints list is empty
        """

    @property
    def environment(self) -> str:
        """Deployment environment name."""

    @property
    def provider(self) -> Optional[str]:
        """Cloud provider identifier."""

    @property
    def location(self) -> Optional[List[str]]:
        """Deployment locations/regions."""

    @property
    def endpoints(self) -> List[str]:
        """Service endpoint URLs."""

    @property
    def resources(self) -> Optional[Resources]:
        """Resource requirements for this deployment."""

    @property
    def links(self) -> Optional[Dict[str, str]]:
        """Related links for monitoring, logging, etc."""

class OpsmlServiceSpec:
    """Service specification representing the opsmlspec.yaml structure."""

    def __init__(
        self,
        name: str,
        space_config: SpaceConfig,
        service_type: ServiceType,
        metadata: Optional[ServiceMetadata] = None,
        service: Optional[ServiceConfig] = None,
        deploy: Optional[List[DeploymentConfig]] = None,
        root_path: Path = Path("."),
    ):
        """Initialize a service specification from opsmlspec.yaml.

        This class represents the complete service definition including
        metadata, card dependencies, and deployment configurations.

        Args:
            name:
                Name of the service (required)
            space_config:
                Space or team configuration (required)
            service_type:
                Type of service (Api, Mcp, or Agent) (required)
            metadata:
                Additional service metadata. Defaults to None
            service:
                Service configuration including cards and MCP settings. Defaults to None
            deploy:
                List of deployment configurations. Defaults to None
            root_path: Root path for the service specification file. Defaults to current directory

        Example:
            ```python
            spec = OpsmlServiceSpec(
                name="recommendation-api",
                space_config=SpaceConfig(space="data-science"),
                service_type=ServiceType.Api,
                metadata=ServiceMetadata(
                    description="Recommendation service",
                    language="python",
                    tags=["ml", "production"],
                ),
                service=ServiceConfig(
                    version="1.0.0",
                    cards=[
                        Card(
                            alias="recommender",
                            name="recommender-model",
                            registry_type=RegistryType.Model,
                            version="1.*",
                        )
                    ],
                ),
            )
            ```
        """

    @property
    def name(self) -> str:
        """Service name."""

    @name.setter
    def name(self, name: str) -> None:
        """Set the service name."""

    @property
    def space_config(self) -> SpaceConfig:
        """Space or team configuration."""

    @property
    def service_type(self) -> ServiceType:
        """Type of service (Api, Mcp, or Agent)."""

    @property
    def metadata(self) -> Optional[ServiceMetadata]:
        """Service metadata."""

    @property
    def service(self) -> Optional[ServiceConfig]:
        """Service configuration."""

    @property
    def deploy(self) -> Optional[List[DeploymentConfig]]:
        """Deployment configurations."""

    @property
    def root_path(self) -> Path:
        """Root path of the service specification file."""

    def from_path(self, path: Optional[Path] = None) -> "OpsmlServiceSpec":
        """Load the service specification from an opsmlspec.yaml file or
        a provided path.

        Args:
            path (Optional[Path]):
                Optional path to the opsmlspec.yaml file. If not provided,
                the method will look for opsmlspec.yaml in the root_path.
        """

    def __str__(self) -> str:
        """String representation of the OpsmlServiceSpec."""

class RegistryTestHelper:
    """Helper class for testing the registry"""

    def __init__(self) -> None: ...
    def setup(self) -> None: ...
    def cleanup(self) -> None: ...

class OpsmlTestServer:
    def __init__(self, cleanup: bool = True, base_path: Optional[Path] = None) -> None:
        """Instantiates the test server.

        When the test server is used as a context manager, it will start the server
        in a background thread and set the appropriate env vars so that the client
        can connect to the server. The server will be stopped when the context manager
        exits and the env vars will be reset.

        Args:
            cleanup (bool, optional):
                Whether to cleanup the server after the test. Defaults to True.
            base_path (Optional[Path], optional):
                The base path for the server. Defaults to None. This is primarily
                used for testing loading attributes from a pyproject.toml file.
        """

    def start_server(self) -> None:
        """Starts the test server."""

    def stop_server(self) -> None:
        """Stops the test server."""

    def __enter__(self) -> "OpsmlTestServer":
        """Starts the test server."""

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        """Stops the test server."""

    def set_env_vars_for_client(self) -> None:
        """Sets the env vars for the client to connect to the server."""

    def remove_env_vars_for_client(self) -> None:
        """Removes the env vars for the client to connect to the server."""

    @staticmethod
    def cleanup() -> None:
        """Cleans up the test server."""

class OpsmlServerContext:
    def __init__(self) -> None:
        """Instantiates the server context.
        This is helpful when you are running tests in server mode to
        aid in background cleanup of resources
        """

    def __enter__(self) -> "OpsmlServerContext":
        """Starts the server context."""

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        """Stops the server context."""

    @property
    def server_uri(self) -> str:
        """Returns the server URI."""

__all__ = [
    "AppState",
    "ReloadConfig",
    "ColType",
    "ColValType",
    "ColumnSplit",
    "StartStopSplit",
    "IndiceSplit",
    "DataSplit",
    "DataSplits",
    "Data",
    "DependentVars",
    "Inequality",
    "DataSplitter",
    "DataInterface",
    "SqlLogic",
    "DataInterfaceSaveMetadata",
    "DataInterfaceMetadata",
    "NumpyData",
    "PolarsData",
    "PandasData",
    "ArrowData",
    "TorchData",
    "SqlData",
    "generate_feature_schema",
    "DataSaveKwargs",
    "DataLoadKwargs",
    "DataInterfaceType",
    "HuggingFaceORTModel",
    "HuggingFaceOnnxArgs",
    "ModelInterfaceMetadata",
    "ModelInterfaceSaveMetadata",
    "ModelInterfaceType",
    "ModelInterface",
    "TaskType",
    "SklearnModel",
    "DataProcessor",
    "LightGBMModel",
    "ModelType",
    "XGBoostModel",
    "TorchModel",
    "LightningModel",
    "HuggingFaceTask",
    "HuggingFaceModel",
    "OnnxModel",
    "CatBoostModel",
    "OnnxSession",
    "TensorFlowModel",
    "PromptSaveKwargs",
    "ModelLoadKwargs",
    "ModelSaveKwargs",
    "OnnxSchema",
    "ProcessorType",
    "CommonKwargs",
    "SaveName",
    "Suffix",
    "VersionType",
    "DriftProfileUri",
    "DriftArgs",
    "DriftProfileMap",
    "DataType",
    "ExtraMetadata",
    "Feature",
    "FeatureSchema",
    "OpsmlTestServer",
    "OpsmlServerContext",
    "RegistryTestHelper",
]
