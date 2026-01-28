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
#  This section contains the type definitions for opsml.card module
# __opsml.card__
# ######################################################################################

class ServiceType:
    """
    Enum representing the type of service.

    Attributes:
        Api: REST API service
        Mcp: Model Context Protocol service
        Agent: Agentic workflow service
    """

    Api: "ServiceType"
    Mcp: "ServiceType"
    Agent: "ServiceType"

class RegistryType:
    Data: "RegistryType"
    Model: "RegistryType"
    Experiment: "RegistryType"
    Audit: "RegistryType"
    Prompt: "RegistryType"
    Service: "RegistryType"

class RegistryMode:
    Client: "RegistryMode"
    Server: "RegistryMode"

class CardRecord:
    uid: Optional[str]
    created_at: Optional[str]
    app_env: Optional[str]
    name: str
    space: str
    version: str
    tags: Dict[str, str]
    datacard_uids: Optional[List[str]]
    modelcard_uids: Optional[List[str]]
    experimentcard_uids: Optional[List[str]]
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
    cards: List[CardRecord]

    def __getitem__(self, key: int) -> Optional[CardRecord]:
        """Return the card at the specified index"""

    def __iter__(self) -> CardRecord:
        """Return an iterator for the card list"""

    def as_table(self) -> None:
        """Print cards as a table"""

    def __len__(self) -> int:
        """Return the length of the card list"""

# Registry

class DataCard:
    def __init__(  # pylint: disable=dangerous-default-value
        self,
        interface: Optional[DataInterface] = None,
        space: Optional[str] = None,
        name: Optional[str] = None,
        version: Optional[str] = None,
        uid: Optional[str] = None,
        tags: List[str] = [],
    ) -> None:
        """Define a data card

        Args:
            interface (DataInterface | None):
                The data interface
            space (str | None):
                The space of the card
            name (str | None):
                The name of the card
            version (str | None):
                The version of the card
            uid (str | None):
                The uid of the card
            tags (List[str]):
                The tags of the card

        Example:
        ```python
        from opsml import DataCard, CardRegistry, RegistryType, PandasData

        # for testing purposes
        from opsml.helpers.data import create_fake_data

        # pandas data
        X, _ = create_fake_data(n_samples=1200)

        interface = PandasData(data=X)
        datacard = DataCard(
            interface=interface,
            space="my-repo",
            name="my-name",
            tags=["foo:bar", "baz:qux"],
        )

        # register card
        registry = CardRegistry(RegistryType.Data)
        registry.register_card(datacard)
        ```
        """

    @property
    def data(self) -> Any:
        """Return the data. This is a special property that is used to
        access the data from the interface. It is not settable. It will also
        raise an error if the interface is not set or if the data
        has not been loaded.
        """

    @property
    def experimentcard_uid(self) -> Optional[str]:
        """Return the experimentcard uid"""

    @experimentcard_uid.setter
    def experimentcard_uid(self, experimentcard_uid: Optional[str]) -> None:
        """Set the experimentcard uid"""

    @property
    def interface(self) -> Optional[DataInterface]:
        """Return the data interface"""

    @interface.setter
    def interface(self, interface: Any) -> None:
        """Set the data interface

        Args:
            interface (DataInterface):
                The data interface to set. Must inherit from DataInterface
        """

    @property
    def app_env(self) -> str:
        """Returns the app env"""

    @property
    def created_at(self) -> datetime.datetime:
        """Returns the created at timestamp"""

    @property
    def name(self) -> str:
        """Return the name of the data card"""

    @name.setter
    def name(self, name: str) -> None:
        """Set the name of the data card

        Args:
            name (str):
                The name of the data card
        """

    @property
    def space(self) -> str:
        """Return the space of the data card"""

    @space.setter
    def space(self, space: str) -> None:
        """Set the space of the data card

        Args:
            space (str):
                The space of the data card
        """

    @property
    def version(self) -> str:
        """Return the version of the data card"""

    @version.setter
    def version(self, version: str) -> None:
        """Set the version of the data card

        Args:
            version (str):
                The version of the data card
        """

    @property
    def uid(self) -> str:
        """Return the uid of the data card"""

    @property
    def tags(self) -> List[str]:
        """Return the tags of the data card"""

    @tags.setter
    def tags(self, tags: List[str]) -> None:
        """Set the tags of the data card

        Args:
            tags (List[str]):
                The tags of the data card
        """

    @property
    def metadata(self) -> "DataCardMetadata":  # pylint: disable=used-before-assignment
        """Return the metadata of the data card"""

    @property
    def registry_type(self) -> RegistryType:
        """Return the card type of the data card"""

    @property
    def data_type(self) -> DataType:
        """Return the data type"""

    def save(
        self,
        path: Path,
        save_kwargs: Optional[DataSaveKwargs] = None,
    ) -> None:
        """Save the data card

        Args:
            path (Path):
                The path to save the data card to
            save_kwargs (DataSaveKwargs | None):
                Optional save kwargs to that will be passed to the
                data interface save method

        Acceptable save kwargs:
            Kwargs are passed to the underlying data interface for saving.
            For a complete list of options see the save method of the data interface and
            their associated libraries.
        """

    def load(
        self,
        path: Optional[Path] = None,
        load_kwargs: Optional[DataLoadKwargs] = None,
    ) -> None:
        """Load the data card

        Args:
            path (Path | None):
                The path to load the data card from. If no path is provided,
                the data interface will be loaded from the server.
            load_kwargs (DataLoadKwargs | None):
                Optional load kwargs to that will be passed to the
                data interface load method
        """

    def download_artifacts(self, path: Optional[Path] = None) -> None:
        """Download artifacts associated with the DataCard

        Args:
            path (Path):
                Path to save the artifacts. If not provided, the artifacts will be saved
                to a directory called "card_artifacts"
        """

    def model_dump_json(self) -> str:
        """Return the model dump as a json string"""

    @staticmethod
    def model_validate_json(json_string: str, interface: Optional[DataInterface] = None) -> "ModelCard":
        """Validate the model json string

        Args:
            json_string (str):
                The json string to validate
            interface (DataInterface):
                By default, the interface will be inferred and instantiated
                from the interface metadata. If an interface is provided
                (as in the case of custom interfaces), it will be used.
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

    def split_data(self) -> Dict[str, Data]:
        """Split the data according to the data splits defined in the interface

        Returns:
            Dict[str, Any]:
                A dictionary containing the split data
        """

class DataCardMetadata:
    @property
    def schema(self) -> FeatureSchema:
        """Return the feature map"""

    @property
    def experimentcard_uid(self) -> Optional[str]:
        """Return the experimentcard uid"""

    @property
    def auditcard_uid(self) -> Optional[str]:
        """Return the experimentcard uid"""

class ModelCardMetadata:
    def __init__(
        self,
        datacard_uid: Optional[str] = None,
        experimentcard_uid: Optional[str] = None,
        auditcard_uid: Optional[str] = None,
    ) -> None:
        """Create a ModelCardMetadata object

        Args:
            datacard_uid (str | None):
                The datacard uid
            experimentcard_uid (str | None):
                The experimentcard uid
            auditcard_uid (str | None):
                The auditcard uid
        """

    @property
    def datacard_uid(self) -> str:
        """Returns the datacard uid"""

    @datacard_uid.setter
    def datacard_uid(self, datacard_uid: str) -> None:
        """Set the datacard uid"""

    @property
    def experimentcard_uid(self) -> str:
        """Returns the experimentcard uid"""

    @experimentcard_uid.setter
    def experimentcard_uid(self, experimentcard_uid: str) -> None:
        """Set the experimentcard uid"""

    @property
    def auditcard_uid(self) -> str:
        """Returns the experimentcard uid"""

    @auditcard_uid.setter
    def auditcard_uid(self, auditcard_uid: str) -> None:
        """Set the experimentcard uid"""

class ModelCard:
    def __init__(
        self,
        interface: Optional[ModelInterface] = None,
        space: Optional[str] = None,
        name: Optional[str] = None,
        version: Optional[str] = None,
        uid: Optional[str] = None,
        tags: List[str] = [],
        datacard_uid: Optional[str] = None,
        metadata: ModelCardMetadata = ModelCardMetadata(),
    ) -> None:
        """Create a ModelCard from a machine learning model.

        Cards are stored in the ModelCardRegistry and follow the naming convention of:
        {registry}/{space}/{name}/v{version}

        Args:
            interface (ModelInterface | None):
                `ModelInterface` class containing trained model
            space (str | None):
                space to associate with `ModelCard`
            name (str | None):
                Name to associate with `ModelCard`
            version (str | None):
                Current version (assigned if card has been registered). Follows
                semantic versioning.
            uid (str | None):
                Unique id (assigned if card has been registered)
            tags (List[str]):
                Tags to associate with `ModelCard`. Can be a dictionary of strings or
                a `Tags` object.
            datacard_uid (str | None):
                The datacard uid to associate with the model card. This is used to link the
                model card to the data card. Datacard uid can also be set in card metadata.
            metadata (ModelCardMetadata):
                Metadata to associate with the `ModelCard. Defaults to an empty `ModelCardMetadata` object.

        Example:
        ```python
        from opsml import ModelCard, CardRegistry, RegistryType, SklearnModel, TaskType
        from sklearn import ensemble

        # for testing purposes
        from opsml.helpers.data import create_fake_data

        # pandas data
        X, y = create_fake_data(n_samples=1200)

        # train model
        reg = ensemble.RandomForestClassifier(n_estimators=5)
        reg.fit(X_train.to_numpy(), y_train)

        # create interface and card
        interface = SklearnModel(
            model=reg,
            sample_data=X_train,
            task_type=TaskType.Classification,
        )

        modelcard = ModelCard(
            interface=random_forest_classifier,
            space="my-repo",
            name="my-model",
            tags=["foo:bar", "baz:qux"],
        )

        # register card
        registry = CardRegistry(RegistryType.Model, save_kwargs=ModelSaveKwargs(save_onnx=True)) # convert to onnx
        registry.register_card(modelcard)
        ```
        """

    @property
    def model(self) -> Any:
        """Returns the model. This is a special property that is used to
        access the model from the interface. It is not settable. It will also
        raise an error if the interface is not set or if the model
        has not been loaded.
        """

    @property
    def onnx_session(self) -> Optional[OnnxSession]:
        """Returns the onnx session. This is a special property that is used to
        access the onnx session from the interface. It is not settable. It will also
        raise an error if the interface is not set or if the model
        has not been loaded.
        """

    @property
    def app_env(self) -> str:
        """Returns the app env"""

    @property
    def created_at(self) -> datetime.datetime:
        """Returns the created at timestamp"""

    @property
    def datacard_uid(self) -> str:
        """Returns the datacard uid"""

    @datacard_uid.setter
    def datacard_uid(self, datacard_uid: str) -> None:
        """Set the datacard uid"""

    @property
    def experimentcard_uid(self) -> str:
        """Returns the experimentcard uid"""

    @experimentcard_uid.setter
    def experimentcard_uid(self, experimentcard_uid: str) -> None:
        """Set the experimentcard uid"""

    @property
    def uri(self) -> Path:
        """Returns the uri of the `ModelCard` in the
        format of {registry}/{space}/{name}/v{version}
        """

    @property
    def interface(self) -> Optional[ModelInterface]:
        """Returns the `ModelInterface` associated with the `ModelCard`"""

    @interface.setter
    def interface(self, interface: Any) -> None:
        """Set the `ModelInterface` associated with the `ModelCard`"""

    @property
    def name(self) -> str:
        """Returns the name of the `ModelCard`"""

    @name.setter
    def name(self, name: str) -> None:
        """Set the name of the `ModelCard`

        Args:
            name (str):
                The name of the `ModelCard`
        """

    @property
    def space(self) -> str:
        """Returns the space of the `ModelCard`"""

    @space.setter
    def space(self, space: str) -> None:
        """Set the space of the `ModelCard`

        Args:
            space (str):
                The space of the `ModelCard`
        """

    @property
    def version(self) -> str:
        """Returns the version of the `ModelCard`"""

    @version.setter
    def version(self, version: str) -> None:
        """Set the version of the `ModelCard`

        Args:
            version (str):
                The version of the `ModelCard`
        """

    @property
    def uid(self) -> str:
        """Returns the uid of the `ModelCard`"""

    @property
    def tags(self) -> List[str]:
        """Returns the tags of the `ModelCard`"""

    @property
    def metadata(self) -> ModelCardMetadata:
        """Returns the metadata of the `ModelCard`"""

    @property
    def registry_type(self) -> RegistryType:
        """Returns the card type of the `ModelCard`"""

    def save(self, path: Path, save_kwargs: Optional[ModelSaveKwargs] = None) -> None:
        """Save the model card to a directory

        Args:
            path (Path):
                Path to save the model card.
            save_kwargs (SaveKwargs):
                Optional kwargs to pass to `ModelInterface` save method.
        """

    def load(
        self,
        path: Optional[Path] = None,
        load_kwargs: None | ModelLoadKwargs = None,
    ) -> None:
        """Load ModelCard interface components

        Args:
            path (Path | None):
                The path to load the data card from. If no path is provided,
                the model interface will be loaded from the server.
            load_kwargs (ModelLoadKwargs):
                Optional kwargs to pass to `ModelInterface` load method.
        """

    @staticmethod
    def load_from_path(
        path: Path,
        load_kwargs: None | ModelLoadKwargs = None,
        interface: Optional[ModelInterface] = None,
    ) -> "ModelCard":
        """Staticmethod to load a ModelCard from a path. Typically used when
        a `ModelCard`s artifacts have already been downloaded to a path.

        This is commonly used in API workflows where a user may download artifacts to
        a directory and load the contents during API/Application startup.

        Args:
            path (Path):
                The path to load the ModelCard from.
            load_kwargs (ModelLoadKwargs):
                Optional kwargs to pass to `ModelInterface` load method.
            interface (ModelInterface):
                Optional interface for the model. Used with Custom interfaces.

        Returns:
            ModelCard:
                The loaded ModelCard.

        Example:

            ```python
            # shell command
            opsml run get model --space <space_name> --name <model_name> --write-dir <path>

            # Within python application
            model_card = ModelCard.load_from_path(<path>)
            ```
        """

    def download_artifacts(self, path: Optional[Path] = None) -> None:
        """Download artifacts associated with the ModelCard

        Args:
            path (Path):
                Path to save the artifacts. If not provided, the artifacts will be saved
                to a directory called "card_artifacts"
        """

    def model_dump_json(self) -> str:
        """Return the model dump as a json string"""

    @staticmethod
    def model_validate_json(json_string: str, interface: Optional[ModelInterface] = None) -> "ModelCard":
        """Validate the model json string

        Args:
            json_string (str):
                The json string to validate
            interface (ModelInterface):
                By default, the interface will be inferred and instantiated
                from the interface metadata. If an interface is provided
                (as in the case of custom interfaces), it will be used.
        """

    def drift_profile_path(self, alias: str) -> Path:
        """Helper method that returns the path to a specific drift profile.
        This method will fail if there is no drift profile map or the alias
        does not exist.

        Args:
            alias (str):
                The alias of the drift profile

        Returns:
            Path to the drift profile
        """

    def __str__(self) -> str:
        """Return a string representation of the ModelCard.

        Returns:
            String representation of the ModelCard.
        """

    @property
    def drift_profile(self) -> DriftProfileMap:
        """Return the drift profile map from the model interface.

        Returns:
            DriftProfileMap
        """

class ComputeEnvironment:
    cpu_count: int
    total_memory: int
    total_swap: int
    system: str
    os_version: str
    hostname: str
    python_version: str

    def __str__(self): ...

class UidMetadata:
    datacard_uids: List[str]
    modelcard_uids: List[str]
    promptcard_uids: List[str]
    service_card_uids: List[str]
    experimentcard_uids: List[str]

class ExperimentCard:
    def __init__(
        self,
        space: Optional[str] = None,
        name: Optional[str] = None,
        version: Optional[str] = None,
        uid: Optional[str] = None,
        tags: List[str] = [],
    ) -> None:
        """Instantiates a ExperimentCard.

        Cards are stored in the ExperimentCard Registry and follow the naming convention of:
        {registry}/{space}/{name}/v{version}

        Args:
            space (str | None):
                space to associate with `ExperimentCard`
            name (str | None):
                Name to associate with `ExperimentCard`
            version (str | None):
                Current version (assigned if card has been registered). Follows
                semantic versioning.
            uid (str | None):
                Unique id (assigned if card has been registered)
            tags (List[str]):
                Tags to associate with `ExperimentCard`. Can be a dictionary of strings or
                a `Tags` object.

        Example:
        ```python
        from opsml import start_experiment

        # start an experiment
        with start_experiment(space="test", log_hardware=True) as exp:
            exp.log_metric("accuracy", 0.95)
            exp.log_parameter("epochs", 10)
        ```
        """

    def get_metrics(
        self,
        names: Optional[list[str]] = None,
    ) -> Metrics:
        """
        Get metrics of an experiment

        Args:
            names (list[str] | None):
                Names of the metrics to get. If None, all metrics will be returned.

        Returns:
            Metrics
        """

    def get_parameters(
        self,
        names: Optional[list[str]] = None,
    ) -> "Parameters":
        """
        Get parameters of an experiment

        Args:
            names (list[str] | None):
                Names of the parameters to get. If None, all parameters will be returned.

        Returns:
            Parameters
        """

    @property
    def name(self) -> str:
        """Returns the name of the `ModelCard`"""

    @name.setter
    def name(self, name: str) -> None:
        """Set the name of the `ModelCard`

        Args:
            name (str):
                The name of the `ModelCard`
        """

    @property
    def space(self) -> str:
        """Returns the space of the `experimentcard`"""

    @space.setter
    def space(self, space: str) -> None:
        """Set the space of the `experimentcard`

        Args:
            space (str):
                The space of the `experimentcard`
        """

    @property
    def version(self) -> str:
        """Returns the version of the `experimentcard`"""

    @version.setter
    def version(self, version: str) -> None:
        """Set the version of the `experimentcard`

        Args:
            version (str):
                The version of the `experimentcard`
        """

    @property
    def eval_metrics(self) -> "EvalMetrics":
        """Returns the eval metrics of the `experimentcard`"""

    @eval_metrics.setter
    def eval_metrics(self, metrics: "EvalMetrics") -> None:
        """Set the eval metrics of the `experimentcard`

        Args:
            metrics (EvalMetrics):
                The eval metrics of the `experimentcard`
        """

    @property
    def uid(self) -> str:
        """Returns the uid of the `experimentcard`"""

    @property
    def uids(self) -> UidMetadata:
        """Returns the uids of the `experimentcard`"""

    @property
    def tags(self) -> List[str]:
        """Returns the tags of the `ExperimentCard`"""

    @property
    def artifacts(self) -> List[str]:
        """Returns the artifact names"""

    @property
    def compute_environment(self) -> ComputeEnvironment:
        """Returns the compute env"""

    @property
    def registry_type(self) -> RegistryType:
        """Returns the card type of the `experimentcard`"""

    @property
    def app_env(self) -> str:
        """Returns the app env"""

    @property
    def created_at(self) -> datetime.datetime:
        """Returns the created at timestamp"""

    def add_child_experiment(self, uid: str) -> None:
        """Add a child experiment to the experiment card

        Args:
            uid (str):
                The experiment card uid to add
        """

    def list_artifacts(self, path: Optional[Path]) -> List[str]:
        """List the artifacts associated with the experiment card

        Args:
            path (Path):
                Specific path you wish to list artifacts from. If not provided,
                all artifacts will be listed.

                Example:
                    You logged artifacts with the following paths:
                    - "data/processed/my_data.csv"
                    - "model/my_model.pkl"

                    If you wanted to list all artifacts in the "data" directory,
                    you would pass Path("data") as the path.
        """

    def download_artifacts(
        self,
        path: Optional[Path] = None,
        lpath: Optional[Path] = None,
    ) -> None:
        """Download artifacts associated with the ExperimentCard

        Args:
            path (Path | None):
                Specific path you wish to download artifacts from. If not provided,
                all artifacts will be downloaded.

            lpath (Path | None):
                Local path to save the artifacts. If not provided, the artifacts will be saved
                to a directory called "artifacts"
        """

    def download_artifact(
        self,
        path: Path,
        lpath: Optional[Path] = None,
    ) -> None:
        """Download a specific artifact associated with the ExperimentCard

        Args:
            path (Path):
                Path to the artifact to download
            lpath (Path | None):
                Local path to save the artifact. If not provided, the artifact will be saved
                to a directory called "artifacts"

        Examples:

        ```python
        # artifact logged to artifacts/data.csv
        download_artifact(Path("artifacts/data.csv"))
        #or
        download_artifact(Path("data.csv"))
        ```
        """

    @staticmethod
    def model_validate_json(json_string: str) -> "ExperimentCard":
        """Load card from json string

        Args:
            json_string (str):
                The json string to validate
        """

    def __str__(self) -> str:
        """Return a string representation of the `ExperimentCard`.

        Returns:
            String representation of the ModelCard.
        """

class PromptCard:
    def __init__(
        self,
        prompt: Prompt,
        space: Optional[str] = None,
        name: Optional[str] = None,
        version: Optional[str] = None,
        uid: Optional[str] = None,
        tags: List[str] = [],
        drift_profile: Optional[Dict[str, GenAIEvalProfile]] = None,
    ) -> None:
        """Creates a `PromptCard`.

        Cards are stored in the PromptCard Registry and follow the naming convention of:
        {registry}/{space}/{name}/v{version}


        Args:
            prompt (Prompt):
                Prompt to associate with `PromptCard`
            space (str | None):
                space to associate with `PromptCard`
            name (str | None):
                Name to associate with `PromptCard`
            version (str | None):
                Current version (assigned if card has been registered). Follows
                semantic versioning.
            uid (str | None):
                Unique id (assigned if card has been registered)
            tags (List[str]):
                Tags to associate with `PromptCard`. Can be a dictionary of strings or
                a `Tags` object.
            drift_profile:
                Drift profile(s) to associate with the model. Must be a dictionary of
                alias and drift profile. Currently supports GenAI evaluation profiles.
        Example:
        ```python
        from opsml import Prompt, PromptCard, CardRegistry, RegistryType

        # create prompt
        prompt = Prompt(
            model="openai:gpt-4o",
            messages=[
                "My prompt $1 is $2",
                "My prompt $3 is $4",
            ],
            system_instructions="system_prompt",
        )

        # create card
        card = PromptCard(
            prompt=prompt,
            space="my-repo",
            name="my-prompt",
            version="0.0.1",
            tags=["gpt-4o", "prompt"],
        )

        # register card
        registry = CardRegistry(RegistryType.Prompt)
        registry.register_card(card)
        ```
        """

    @property
    def prompt(self) -> Prompt:
        """Returns the prompt"""

    @prompt.setter
    def prompt(self, prompt: Prompt) -> None:
        """Set the prompt

        Args:
            prompt (Prompt):
                The prompt to set
        """

    @property
    def experimentcard_uid(self) -> str:
        """Returns the experimentcard uid"""

    @experimentcard_uid.setter
    def experimentcard_uid(self, experimentcard_uid: str) -> None:
        """Set the experimentcard uid"""

    @property
    def name(self) -> str:
        """Returns the name of the `ModelCard`"""

    @name.setter
    def name(self, name: str) -> None:
        """Set the name of the `ModelCard`

        Args:
            name (str):
                The name of the `ModelCard`
        """

    @property
    def space(self) -> str:
        """Returns the space of the `ModelCard`"""

    @space.setter
    def space(self, space: str) -> None:
        """Set the space of the `ModelCard`

        Args:
            space (str):
                The space of the `ModelCard`
        """

    @property
    def version(self) -> str:
        """Returns the version of the `ModelCard`"""

    @version.setter
    def version(self, version: str) -> None:
        """Set the version of the `ModelCard`

        Args:
            version (str):
                The version of the `ModelCard`
        """

    @property
    def uid(self) -> str:
        """Returns the uid of the `ModelCard`"""

    @property
    def tags(self) -> List[str]:
        """Returns the tags of the `ModelCard`"""

    def save(self, path: Path) -> None:
        """Save the `PromptCard` to a directory

        Args:
            path (Path):
                Path to save the prompt card.
        """

    @staticmethod
    def model_validate_json(json_string: str) -> "PromptCard":
        """Load card from json string

        Args:
            json_string (str):
                The json string to validate
        """

    def __str__(self): ...
    def create_eval_profile(
        self,
        alias: str,
        config: GenAIEvalConfig,
        tasks: Sequence[LLMJudgeTask | AssertionTask],
    ) -> None:
        """Initialize a GenAIEvalProfile for LLM evaluation and drift detection.

        LLM evaluations are run asynchronously on the scouter server.

        Overview:
            GenAI evaluations are defined using assertion tasks and LLM judge tasks.
            Assertion tasks evaluate specific metrics based on model responses, and do not require
            the use of an LLM judge or extra call. It is recommended to use assertion tasks whenever possible
            to reduce cost and latency. LLM judge tasks leverage an additional LLM call to evaluate
            model responses based on more complex criteria. Together, these tasks provide a flexible framework
            for monitoring LLM performance and detecting drift over time.


        Args:
            config (GenAIEvalConfig):
                The configuration for the GenAI drift profile containing space, name,
                version, and alert settings.
            tasks (List[LLMJudgeTask | AssertionTask]):
                List of evaluation tasks to include in the profile. Can contain
                both AssertionTask and LLMJudgeTask instances. At least one task
                (assertion or LLM judge) is required.

        Returns:
            GenAIEvalProfile: Configured profile ready for GenAI drift monitoring.

        Raises:
            ProfileError: If workflow validation fails, metrics are empty when no
                workflow is provided, or if workflow tasks don't match metric names.

        Examples:
            Basic usage with metrics only:

            >>> config = GenAIEvalConfig("my_space", "my_model", "1.0")
            >>>  tasks = [
            ...     LLMJudgeTask(
            ...         id="response_relevance",
            ...         prompt=relevance_prompt,
            ...         expected_value=7,
            ...         field_path="score",
            ...         operator=ComparisonOperator.GreaterThanOrEqual,
            ...         description="Ensure relevance score >= 7"
            ...     )
            ... ]
            >>> profile = Drifter().create_genai_drift_profile(config, tasks)

        """

    @property
    def eval_profile(self) -> DriftProfileMap:
        """Return the drift profile map from the model interface.

        Returns:
            DriftProfileMap
        """

    @eval_profile.setter
    def eval_profile(self, eval_profile: DriftProfileMap) -> None:
        """Set the drift profile map for the prompt card.

        Args:
            eval_profile (DriftProfileMap):
                The drift profile map to set.
        """

class Card:
    """Represents a card from a given registry that can be used in a service card"""

    def __init__(
        self,
        alias: str,
        registry_type: Optional[RegistryType] = None,
        space: Optional[str] = None,
        name: Optional[str] = None,
        version: Optional[str] = None,
        uid: Optional[str] = None,
        card: Optional["CardT"] = None,
        drift: Optional[DriftConfig] = None,
    ) -> None:
        """Initialize the service card. Card accepts either a combination of
        space and name (with version as optional) or a uid. If only space and name are
        provided with no version, the latest version for a given space and name will be used
        (e.g. {space}/{name}/v*). If a version is provided, it must follow semver rules that
        are compatible with opsml (e.g. v1.*, v1.2.3, v2.3.4-alpha, etc.). If both space/name and uid
        are provided, the uid will take precedence. If neither space/name nor uid are provided,
        an error will be raised.

        Alias is used to identify the card in the service card and is not necessarily the name of
        the card. It is recommended to use a short and descriptive alias that is easy to remember.

        Example:

        ```python
        service = ServiceCard(...)
        service["my_alias"]
        ```


        Args:
            alias (str):
                The alias of the card
            registry_type (RegistryType):
                The type of registry the service card belongs to. This is
                required if no card is provided.
            space (str):
                The space of the service card
            name (str):
                The name of the service card
            version (str):
                The version of the service card
            uid (str):
                The uid of the service card
            card (Union[DataCard, ModelCard, PromptCard, ExperimentCard]):
                Optional card to add to the service. If provided, arguments will
                be extracted from the card. This card must be registered in a registry.
            drift (DriftConfig | None):
                Optional drift configuration for the card. This is used to
                configure drift detection for the card in the service.


        Example:

        ```python
        from opsml import Card, ServiceCard, RegistryType

        # With arguments
        card = Card(
            alias="my_alias",
            registry_type=RegistryType.Model,
            space="my_space",
            name="my_name",
            version="1.0.0",
        )

        # With card uid
        card = Card(
            alias="my_alias",
            registry_type=RegistryType.Model,
            uid="my_uid",
        )

        # With registered card
        card = Card(
            alias="my_alias",
            card=model_card,  # ModelCard object
        )
        ```

        """

    @property
    def alias(self) -> str:
        """Alias used to reference this card within the service."""

    @property
    def space(self) -> str:
        """Space this card belongs to."""

    @property
    def name(self) -> str:
        """Name of the card."""

    @property
    def version(self) -> Optional[str]:
        """Version specifier for the card."""

    @property
    def registry_type(self) -> RegistryType:
        """Registry type of the card."""

    @property
    def drift(self) -> Optional[DriftConfig]:
        """Drift detection configuration if enabled."""

    @property
    def uid(self) -> Optional[str]:
        """Unique identifier of the card."""

class McpCapability:
    """
    Enum representing Model Context Protocol capabilities.

    Attributes:
        Resources: Resource access capability
        Tools: Tool invocation capability
        Prompts: Prompt template capability
    """

    Resources: "McpCapability"
    Tools: "McpCapability"
    Prompts: "McpCapability"

class McpTransport:
    """
    Enum representing Model Context Protocol transport types.

    Attributes:
        Http: HTTP-based transport
        Stdio: Standard I/O transport
    """

    Http: "McpTransport"
    Stdio: "McpTransport"

class McpConfig:
    def __init__(
        self,
        capabilities: List[McpCapability],
        transport: McpTransport,
    ):
        """Initialize MCP service configuration.

        Required when service type is 'Mcp'.

        Args:
            capabilities: List of MCP capabilities to enable (resources, tools, prompts)
            transport: Transport protocol to use (http or stdio)

        Raises:
            ValueError: If capabilities list is empty
        """

    @property
    def capabilities(self) -> List[McpCapability]:
        """List of enabled MCP capabilities."""

    @property
    def transport(self) -> McpTransport:
        """Transport protocol for MCP communication."""

class ServiceCard:
    """Creates a ServiceCard to hold a collection of cards."""

    def __init__(
        self,
        space: str,
        name: str,
        cards: List[Card],
        version: Optional[str] = None,
        service_type: Optional[ServiceType] = None,
        load_spec: bool = False,
    ) -> None:
        """Initialize the service card

        Args:
            space (str):
                The space of the service card
            name (str):
                The name of the service card
            cards (List[Card]):
                The cards in the service card
            version (str | None):
                The version of the service card. If not provided, the latest version
                for a given space and name will be used (e.g. {space}/{name}/v*).
            service_type (ServiceType | None):
                The type of service (Api, Mcp, Agent). If not provided, defaults to Api.
            load_spec (bool):
                Whether to load the opsmlspec.yaml file if it exists in the service card directory.
                This is useful when you have additional metadata in the opsmlspec.yaml file that you want
                to include in the service card. Defaults to False.
        """

    @property
    def space(self) -> str:
        """Return the space of the service card"""

    @property
    def name(self) -> str:
        """Return the name of the service card"""

    @property
    def version(self) -> str:
        """Return the version of the service card"""

    @property
    def uid(self) -> str:
        """Return the uid of the service card"""

    @property
    def created_at(self) -> datetime.datetime:
        """Return the created at timestamp"""

    @property
    def cards(self) -> List["CardT"]:
        """Return the cards in the service card"""

    @property
    def opsml_version(self) -> str:
        """Return the opsml version"""

    def save(self, path: Path) -> None:
        """Save the service card to a directory

        Args:
            path (Path):
                Path to save the service card.
        """

    def model_validate_json(self, json_string: str) -> "ServiceCard":
        """Load service card from json string

        Args:
            json_string (str):
                The json string to validate
        """

    def load(
        self,
        load_kwargs: Optional[Dict[str, ModelLoadKwargs | DataLoadKwargs]] = None,
    ) -> None:
        """Call the load method on each Card that requires additional loading.
        This applies to ModelCards and DataCards. PromptCards and ExperimentCards
        do not require additional loading and are loaded automatically when loading
        the ServiceCard from the registry.

        Args:
            load_kwargs (Dict[str, ModelLoadKwargs | DataLoadKwargs]):
                Optional kwargs for loading cards. Expected format:
                {
                    "card_alias":  DataLoadKwargs | ModelLoadKwargs
                }
        """

    @staticmethod
    def from_path(
        path: Optional[Path] = None,
        load_kwargs: Optional[Dict[str, Dict[str, Any]]] = None,
    ) -> "ServiceCard":
        """Loads a service card and its associated cards from a filesystem path.

        Args:
            path (Path):
                Path to load the service card from. Defaults to "service".
            load_kwargs (Dict[str, Dict[str, Any]]):
                Optional kwargs for loading cards. Expected format:
                {
                    "card_alias": {
                        "interface": interface_object,
                        "load_kwargs": DataLoadKwargs | ModelLoadKwargs
                    }
                }

        Returns:
            ServiceCard: The loaded service card with all cards instantiated.

        Raises:
            PyError: If service card JSON cannot be read
            PyError: If cards cannot be loaded
            PyError: If invalid kwargs are provided

        Example:
            ```python
            # Load with custom kwargs for model loading
            load_kwargs = {
                "model_card": {
                    "load_kwargs": ModelLoadKwargs(load_onnx=True)
                }
            }
            service = ServiceCard.from_path(load_kwargs=load_kwargs)
            ```
        """

    def __getitem__(self, alias: str) -> Union[DataCard, ModelCard, PromptCard, ExperimentCard]:
        """Get a card from the service card by alias

        Args:
            alias (str):
                The alias of the card to get

        Returns:
            Card:
                The card with the given alias
        """

    def download_artifacts(self, path: Optional[Path] = None) -> None:
        """Download artifacts associated with each card in the service card. This method
        will always overwrite existing artifacts.

        If the path is not provided, the artifacts will be saved to a directory.

        ```
        service/
        |-- {name}-{version}/
            |-- alias1/
            |-- alias2/
            |-- alias3/
        `-- ...
        ```

        Args:
            path (Path):
                Top-level Path to download the artifacts to. If not provided, the artifacts will be saved
                to a directory using the ServiceCard name.
        """

# Define a TypeVar that can only be one of our card types
CardT = TypeVar(
    "CardT",
    DataCard,
    ModelCard,
    PromptCard,
    ExperimentCard,
    ServiceCard,
)

class CardRegistry(Generic[CardT]):
    def __init__(self, registry_type: Union[RegistryType, str]) -> None:
        """Interface for connecting to any of the Card registries

        Args:
            registry_type (RegistryType | str):
                The type of registry to connect to. Can be a `RegistryType` or a string

        Returns:
            Instantiated connection to specific Card registry


        Example:
        ```python
            data_registry = CardRegistry(RegistryType.Data)
            data_registry.list_cards()

            or
            data_registry = CardRegistry("data")
            data_registry.list_cards()
        ```
        """

    @property
    def registry_type(self) -> RegistryType:
        """Returns the type of registry"""

    @property
    def table_name(self) -> str:
        """Returns the table name for the registry"""

    @property
    def mode(self) -> RegistryMode:
        """Returns the mode of the registry"""

    def list_cards(
        self,
        uid: Optional[str] = None,
        space: Optional[str] = None,
        name: Optional[str] = None,
        version: Optional[str] = None,
        max_date: Optional[str] = None,
        tags: Optional[List[str]] = None,
        sort_by_timestamp: Optional[bool] = False,
        limit: int = 25,
    ) -> CardList:
        """Retrieves records from registry

        Args:
            uid (str):
                Unique identifier for Card. If present, the uid takes precedence
            space (str):
                Optional space associated with card
            name (str):
                Optional name of card
            version (str):
                Optional version number of existing data. If not specified, the
                most recent version will be used
            tags (List[str]):
                Optional list of tags to search for
            max_date (str):
                Optional max date to search. (e.g. "2023-05-01" would search for cards up to and including "2023-05-01").
                Must be in the format "YYYY-MM-DD"
            sort_by_timestamp:
                If True, sorts by timestamp descending
            limit (int):
                Places a limit on result list. Results are sorted by SemVer.
                Defaults to 25.

        Returns:
            List of Cards
        """

    def register_card(
        self,
        card: CardT,
        version_type: VersionType = VersionType.Minor,
        pre_tag: Optional[str] = None,
        build_tag: Optional[str] = None,
        save_kwargs: Optional[ModelSaveKwargs | DataSaveKwargs] = None,
    ) -> None:
        """Register a Card

        Args:
            card (ArtifactCard):
                Card to register. Can be a DataCard, ModelCard,
                experimentcard.
            version_type (VersionType):
                How to increment the version SemVer.
            pre_tag (str):
                Optional pre tag to associate with the version.
            build_tag (str):
                Optional build_tag to associate with the version.
            save_kwargs (SaveKwargs):
                Optional SaveKwargs to pass to the Card interface (If using DataCards
                and ModelCards).

        """

    def load_card(
        self,
        uid: Optional[str] = None,
        space: Optional[str] = None,
        name: Optional[str] = None,
        version: Optional[str] = None,
        interface: Optional[LoadInterfaceType] = None,
    ) -> CardT:
        """Load a Card from the registry

        Args:
            uid (str, optional):
                Unique identifier for Card. If present, the uid takes precedence over space/name/version.
            space (str, optional):
                Space associated with the card.
            name (str, optional):
                Name of the card.
            version (str, optional):
                Version number of existing card. If not specified, the most recent version will be used.
            interface (LoadInterfaceType, optional):
                Interface to load the card with. Required for cards registered with custom interfaces.
                The expected interface type depends on the registry:

                - DataCard registry: DataInterface
                - ModelCard registry: ModelInterface
                - ExperimentCard registry: Not used
                - PromptCard registry: Not used
                - ServiceCard registry: Dict[str, Union[DataInterface, ModelInterface]]
                  Keys should be card aliases within the service.

        Returns:
            Union[DataCard, ModelCard, PromptCard, ExperimentCard, ServiceCard]:
                The loaded card instance from the registry.
        """

    def update_card(
        self,
        card: CardT,
    ) -> None:
        """Update a Card in the registry.
        Note: This will only update the registry record for a given card. It
        will not re-save/update the underlying artifacts (except for metadata).

        Args:
            card (ArtifactCard):
                Card to update. Can be a DataCard, ModelCard,
                experimentcard.
        """

    def delete_card(
        self,
        card: CardT,
    ) -> None:
        """Delete a Card from the registry. This will also remove
        the underlying artifacts associated with the card.

        Args:
            card (ArtifactCard):
                Card to delete. Can be a DataCard, ModelCard,
                experimentcard.
        """

class ModelCardRegistry(CardRegistry):
    def register_card(
        self,
        card: ModelCard,
        version_type: VersionType = VersionType.Minor,
        pre_tag: Optional[str] = None,
        build_tag: Optional[str] = None,
        save_kwargs: Optional[ModelSaveKwargs] = None,  # type: ignore
    ) -> None:
        """Register a Card

        Args:
            card (ModelCard):
                ModelCard to register.
            version_type (VersionType):
                How to increment the version SemVer.
            pre_tag (str):
                Optional pre tag to associate with the version.
            build_tag (str):
                Optional build_tag to associate with the version.
            save_kwargs (ModelSaveKwargs):
                Optional SaveKwargs to pass to the Card interface

        """

    def load_card(
        self,
        uid: Optional[str] = None,
        space: Optional[str] = None,
        name: Optional[str] = None,
        version: Optional[str] = None,
        interface: Optional[ModelInterface] = None,  # type: ignore
    ) -> ModelCard:
        """Load a Card from the registry

        Args:
            uid (str, optional):
                Unique identifier for Card. If present, the uid takes precedence over space/name/version.
            space (str, optional):
                Space associated with the card.
            name (str, optional):
                Name of the card.
            version (str, optional):
                Version number of existing card. If not specified, the most recent version will be used.
            interface (ModelInterface, optional):
                Interface to load the card with. Required for cards registered with custom interfaces.

        Returns:
            ModelCard
        """

    def update_card(
        self,
        card: ModelCard,
    ) -> None:
        """Update a Card in the registry.
        Note: This will only update the registry record for a given card. It
        will not re-save/update the underlying artifacts (except for metadata).

        Args:
            card (ModelCard):
                Card to update
        """

    def delete_card(
        self,
        card: ModelCard,
    ) -> None:
        """Delete a Card from the registry. This will also remove
        the underlying artifacts associated with the card.

        Args:
            card (ModelCard):
                Card to delete. Can be a DataCard, ModelCard,
                experimentcard.
        """

class DataCardRegistry(CardRegistry):
    def register_card(
        self,
        card: DataCard,
        version_type: VersionType = VersionType.Minor,
        pre_tag: Optional[str] = None,
        build_tag: Optional[str] = None,
        save_kwargs: Optional[DataSaveKwargs] = None,  # type: ignore
    ) -> None:
        """Register a Card

        Args:
            card (DataCard):
                DataCard to register.
            version_type (VersionType):
                How to increment the version SemVer.
            pre_tag (str):
                Optional pre tag to associate with the version.
            build_tag (str):
                Optional build_tag to associate with the version.
            save_kwargs (DataSaveKwargs):
                Optional SaveKwargs to pass to the Card interface

        """

    def load_card(
        self,
        uid: Optional[str] = None,
        space: Optional[str] = None,
        name: Optional[str] = None,
        version: Optional[str] = None,
        interface: Optional[DataInterface] = None,  # type: ignore
    ) -> DataCard:
        """Load a Card from the registry

        Args:
            uid (str, optional):
                Unique identifier for Card. If present, the uid takes precedence over space/name/version.
            space (str, optional):
                Space associated with the card.
            name (str, optional):
                Name of the card.
            version (str, optional):
                Version number of existing card. If not specified, the most recent version will be used.
            interface (DataInterface, optional):
                Interface to load the card with. Required for cards registered with custom interfaces.

        Returns:
            DataCard
        """

    def update_card(
        self,
        card: DataCard,
    ) -> None:
        """Update a Card in the registry.
        Note: This will only update the registry record for a given card. It
        will not re-save/update the underlying artifacts (except for metadata).

        Args:
            card (DataCard):
                Card to update
        """

    def delete_card(
        self,
        card: DataCard,
    ) -> None:
        """Delete a Card from the registry. This will also remove
        the underlying artifacts associated with the card.

        Args:
            card (DataCard):
                Card to delete
        """

class ExperimentCardRegistry(CardRegistry):
    def register_card(  # type: ignore
        self,
        card: ExperimentCard,
        version_type: VersionType = VersionType.Minor,
        pre_tag: Optional[str] = None,
        build_tag: Optional[str] = None,
    ) -> None:
        """Register a Card

        Args:
            card (ExperimentCard):
                ExperimentCard to register.
            version_type (VersionType):
                How to increment the version SemVer.
            pre_tag (str):
                Optional pre tag to associate with the version.
            build_tag (str):
                Optional build_tag to associate with the version.

        """

    def load_card(  # type: ignore
        self,
        uid: Optional[str] = None,
        space: Optional[str] = None,
        name: Optional[str] = None,
        version: Optional[str] = None,
    ) -> ExperimentCard:
        """Load a Card from the registry

        Args:
            uid (str, optional):
                Unique identifier for Card. If present, the uid takes precedence over space/name/version.
            space (str, optional):
                Space associated with the card.
            name (str, optional):
                Name of the card.
            version (str, optional):
                Version number of existing card. If not specified, the most recent version will be used.

        Returns:
            ExperimentCard
        """

    def update_card(
        self,
        card: ExperimentCard,
    ) -> None:
        """Update a Card in the registry.
        Note: This will only update the registry record for a given card. It
        will not re-save/update the underlying artifacts (except for metadata).

        Args:
            card (ExperimentCard):
                Card to update.
        """

    def delete_card(
        self,
        card: ExperimentCard,
    ) -> None:
        """Delete a Card from the registry. This will also remove
        the underlying artifacts associated with the card.

        Args:
            card (ExperimentCard):
                Card to delete
        """

class PromptCardRegistry(CardRegistry):
    def register_card(  # type: ignore
        self,
        card: PromptCard,
        version_type: VersionType = VersionType.Minor,
        pre_tag: Optional[str] = None,
        build_tag: Optional[str] = None,
    ) -> None:
        """Register a Card

        Args:
            card (PromptCard):
                PromptCard to register.
            version_type (VersionType):
                How to increment the version SemVer.
            pre_tag (str):
                Optional pre tag to associate with the version.
            build_tag (str):
                Optional build_tag to associate with the version.

        """

    def load_card(  # type: ignore
        self,
        uid: Optional[str] = None,
        space: Optional[str] = None,
        name: Optional[str] = None,
        version: Optional[str] = None,
    ) -> PromptCard:
        """Load a Card from the registry

        Args:
            uid (str, optional):
                Unique identifier for Card. If present, the uid takes precedence over space/name/version.
            space (str, optional):
                Space associated with the card.
            name (str, optional):
                Name of the card.
            version (str, optional):
                Version number of existing card. If not specified, the most recent version will be used.

        Returns:
            PromptCard
        """

    def update_card(
        self,
        card: PromptCard,
    ) -> None:
        """Update a Card in the registry.
        Note: This will only update the registry record for a given card. It
        will not re-save/update the underlying artifacts (except for metadata).

        Args:
            card (PromptCard):
                Card to update
        """

    def delete_card(
        self,
        card: PromptCard,
    ) -> None:
        """Delete a Card from the registry. This will also remove
        the underlying artifacts associated with the card.

        Args:
            card (PromptCard):
                Card to delete
        """

class ServiceCardRegistry(CardRegistry):
    def register_card(  # type: ignore
        self,
        card: ServiceCard,
        version_type: VersionType = VersionType.Minor,
        pre_tag: Optional[str] = None,
        build_tag: Optional[str] = None,
    ) -> None:
        """Register a Card

        Args:
            card (ServiceCard):
                ServiceCard to register.
            version_type (VersionType):
                How to increment the version SemVer.
            pre_tag (str):
                Optional pre tag to associate with the version.
            build_tag (str):
                Optional build_tag to associate with the version.

        """

    def load_card(  # type: ignore
        self,
        uid: Optional[str] = None,
        space: Optional[str] = None,
        name: Optional[str] = None,
        version: Optional[str] = None,
    ) -> ServiceCard:
        """Load a Card from the registry

        Args:
            uid (str, optional):
                Unique identifier for Card. If present, the uid takes precedence over space/name/version.
            space (str, optional):
                Space associated with the card.
            name (str, optional):
                Name of the card.
            version (str, optional):
                Version number of existing card. If not specified, the most recent version will be used.

        Returns:
            ServiceCard
        """

    def update_card(
        self,
        card: ServiceCard,
    ) -> None:
        """Update a Card in the registry.
        Note: This will only update the registry record for a given card. It
        will not re-save/update the underlying artifacts (except for metadata).

        Args:
            card (ServiceCard):
                Card to update
        """

    def delete_card(
        self,
        card: ServiceCard,
    ) -> None:
        """Delete a Card from the registry. This will also remove
        the underlying artifacts associated with the card.

        Args:
            card (ServiceCard):
                Card to delete
        """

class CardRegistries:
    def __init__(self) -> None: ...
    @property
    def data(self) -> DataCardRegistry: ...
    @property
    def model(self) -> ModelCardRegistry: ...
    @property
    def experiment(self) -> ExperimentCardRegistry: ...
    @property
    def audit(self) -> CardRegistry: ...
    @property
    def prompt(self) -> PromptCardRegistry: ...
    @property
    def service(self) -> ServiceCardRegistry: ...

def download_service(
    write_dir: Path,
    space: Optional[str] = None,
    name: Optional[str] = None,
    version: Optional[str] = None,
    uid: Optional[str] = None,
) -> None:
    """Download a service from the registry.

    Args:
        space (str):
            Space associated with the service.
        name (str):
            Name of the service.
        version (str):
            Version number of the service.
        uid (str):
            Unique identifier for the service.
        write_dir (str):
            Directory to write the downloaded service to.
    """

class ExperimentMetric:
    def __init__(
        self,
        name: str,
        value: float,
        step: Optional[int] = None,
        timestamp: Optional[int] = None,
        created_at: Optional[datetime.datetime] = None,
    ) -> None:
        """
        Initialize a Metric

        Args:
            name (str):
                Name of the metric
            value (float):
                Value of the metric
            step (int | None):
                Step of the metric
            timestamp (int | None):
                Timestamp of the metric
            created_at (datetime | None):
                Created at of the metric
        """

    @property
    def name(self) -> str:
        """
        Name of the metric
        """

    @property
    def value(self) -> float:
        """
        Value of the metric
        """

    @property
    def step(self) -> Optional[int]:
        """
        Step of the metric
        """

    @property
    def timestamp(self) -> Optional[int]:
        """
        Timestamp of the metric
        """

    @property
    def created_at(self) -> Optional[datetime.datetime]:
        """
        Created at of the metric
        """

class ExperimentMetrics:
    def __str__(self): ...
    def __getitem__(self, index: int) -> Metric: ...
    def __iter__(self): ...
    def __len__(self) -> int: ...

class Parameter:
    def __init__(
        self,
        name: str,
        value: Union[int, float, str],
    ) -> None:
        """
        Initialize a Parameter

        Args:
            name (str):
                Name of the parameter
            value (int | float | str):
                Value of the parameter
        """

    @property
    def name(self) -> str:
        """
        Name of the parameter
        """

    @property
    def value(self) -> Union[int, float, str]:
        """
        Value of the parameter
        """

class Parameters:
    def __str__(self): ...
    def __getitem__(self, index: int) -> Parameter: ...
    def __iter__(self): ...
    def __len__(self) -> int: ...

class Experiment:
    def start_experiment(
        self,
        space: Optional[str] = None,
        name: Optional[str] = None,
        code_dir: Optional[Path] = None,
        log_hardware: bool = False,
        experiment_uid: Optional[str] = None,
    ) -> "Experiment":
        """
        Start an Experiment

        Args:
            space (str | None):
                space to associate with `ExperimentCard`
            name (str | None):
                Name to associate with `ExperimentCard`
            code_dir (Path | None):
                Directory to log code from
            log_hardware (bool):
                Whether to log hardware information or not
            experiment_uid (str | None):
                Experiment UID. If provided, the experiment will be loaded from the server.

        Returns:
            Experiment
        """

    def __enter__(self) -> "Experiment":
        pass

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        pass

    def log_metric(
        self,
        name: str,
        value: float,
        step: Optional[int] = None,
        timestamp: Optional[int] = None,
        created_at: Optional[datetime.datetime] = None,
    ) -> None:
        """
        Log a metric

        Args:
            name (str):
                Name of the metric
            value (float):
                Value of the metric
            step (int | None):
                Step of the metric
            timestamp (int | None):
                Timestamp of the metric
            created_at (datetime | None):
                Created at of the metric
        """

    def log_metrics(self, metrics: list[ExperimentMetric]) -> None:
        """
        Log multiple metrics

        Args:
            metrics (list[Metric]):
                List of metrics to log
        """

    def log_eval_metrics(self, metrics: "EvalMetrics") -> None:
        """
        Log evaluation metrics

        Args:
            metrics (EvalMetrics):
                Evaluation metrics to log
        """

    def log_parameter(
        self,
        name: str,
        value: Union[int, float, str],
    ) -> None:
        """
        Log a parameter

        Args:
            name (str):
                Name of the parameter
            value (int | float | str):
                Value of the parameter
        """

    def log_parameters(self, parameters: list[Parameter] | Dict[str, Union[int, float, str]]) -> None:
        """
        Log multiple parameters

        Args:
            parameters (list[Parameter] | Dict[str, Union[int, float, str]]):
                Parameters to log
        """

    def log_artifact(
        self,
        lpath: Path,
        rpath: Optional[str] = None,
    ) -> None:
        """
        Log an artifact

        Args:
            lpath (Path):
                The local path where the artifact has been saved to
            rpath (Optional[str]):
                The path to associate with the artifact in the experiment artifact directory
                {experiment_path}/artifacts. If not provided, defaults to
                {experiment}/artifacts/{filename}
        """

    def log_figure_from_path(
        self,
        lpath: Path,
        rpath: Optional[str] = None,
    ) -> None:
        """
        Log a figure

        Args:
            lpath (Path):
                The local path where the figure has been saved to. Must be an image type
                (e.g. jpeg, tiff, png, etc.)
            rpath (Optional[str]):
                The path to associate with the figure in the experiment artifact directory
                {experiment_path}/artifacts/figures. If not provided, defaults to
                {experiment}/artifacts/figures/{filename}

        """

    def log_figure(self, name: str, figure: Any, kwargs: Optional[Dict[str, Any]] = None) -> None:
        """
        Log a figure. This method will log a matplotlib Figure object to the experiment artifacts.

        Args:
            name (str):
                Name of the figure including its file extension
            figure (Any):
                Figure to log
            kwargs (Optional[Dict[str, Any]]):
                Additional keyword arguments
        """

    def log_artifacts(
        self,
        paths: Path,
    ) -> None:
        """
        Log multiple artifacts

        Args:
            paths (Path):
                Paths to a directory containing artifacts.
                All files in the directory will be logged.
        """

    @property
    def card(self) -> "ExperimentCard":
        """
        ExperimentCard associated with the Experiment
        """

    def register_card(
        self,
        card: Union[DataCard, ModelCard, PromptCard],
        version_type: VersionType = VersionType.Minor,
        pre_tag: Optional[str] = None,
        build_tag: Optional[str] = None,
        save_kwargs: Optional[ModelSaveKwargs | DataSaveKwargs] = None,
    ) -> None:
        """Register a Card as part of an experiment

        Args:
            card (DataCard | ModelCard):
                Card to register. Can be a DataCard or a ModelCard
            version_type (VersionType):
                How to increment the version SemVer. Default is VersionType.Minor.
            pre_tag (str):
                Optional pre tag to associate with the version.
            build_tag (str):
                Optional build_tag to associate with the version.
            save_kwargs (SaveKwargs):
                Optional SaveKwargs to pass to the Card interface (If using DataCards
                and ModelCards).

        """

def start_experiment(
    space: Optional[str] = None,
    name: Optional[str] = None,
    code_dir: Optional[Path] = None,
    log_hardware: bool = False,
    experiment_uid: Optional[str] = None,
) -> Experiment:
    """
    Start an Experiment

    Args:
        space (str | None):
            space to associate with `ExperimentCard`
        name (str | None):
            Name to associate with `ExperimentCard`
        code_dir (Path | None):
            Directory to log code from
        log_hardware (bool):
            Whether to log hardware information or not
        experiment_uid (str | None):
            Experiment UID. If provided, the experiment will be loaded from the server.

    Returns:
        Experiment
    """

class EvalMetrics:
    """
    Map of metrics used that can be used to evaluate a model.
    The metrics are also used when comparing a model with other models
    """

    def __init__(self, metrics: Dict[str, float]) -> None:
        """
        Initialize EvalMetrics

        Args:
            metrics (Dict[str, float]):
                Dictionary of metrics containing the name of the metric as the key and its value as the value.
        """

    def __getitem__(self, key: str) -> float:
        """Get the value of a metric by name. A RuntimeError will be raised if the metric does not exist."""

def get_experiment_metrics(
    experiment_uid: str,
    names: Optional[list[str]] = None,
) -> Metrics:
    """
    Get metrics of an experiment

    Args:
        experiment_uid (str):
            UID of the experiment
        names (list[str] | None):
            Names of the metrics to get. If None, all metrics will be returned.

    Returns:
        Metrics
    """

def get_experiment_parameters(
    experiment_uid: str,
    names: Optional[list[str]] = None,
) -> Parameters:
    """
    Get parameters of an experiment

    Args:
        experiment_uid (str):
            UID of the experiment
        names (list[str] | None):
            Names of the parameters to get. If None, all parameters will be returned.

    Returns:
        Parameters
    """

def download_artifact(
    experiment_uid: str,
    path: Path,
    lpath: Optional[Path] = None,
) -> None:
    """
    Download an artifact from an experiment
    Args:
        experiment_uid (str):
            UID of the experiment
        path (Path):
            Path of the artifact to download
        lpath (Path | None):
            Local path to download the artifact to. If None, the artifact will be downloaded to the current working directory.
    """

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

class ServiceSpec:
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
            spec = ServiceSpec(
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

    def from_path(self, path: Optional[Path] = None) -> "ServiceSpec":
        """Load the service specification from an opsmlspec.yaml file or
        a provided path.

        Args:
            path (Optional[Path]):
                Optional path to the opsmlspec.yaml file. If not provided,
                the method will look for opsmlspec.yaml in the root_path.
        """

    def __str__(self) -> str:
        """String representation of the ServiceSpec."""

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
    "Card",
    "CardRecord",
    "CardList",
    "CardRegistry",
    "CardRegistries",
    "DataCard",
    "DataCardMetadata",
    "RegistryType",
    "RegistryMode",
    "ModelCard",
    "ModelCardMetadata",
    "ExperimentCard",
    "ComputeEnvironment",
    "PromptCard",
    "ServiceCard",
    "ServiceType",
    "download_service",
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
    "Experiment",
    "start_experiment",
    "ExperimentMetric",
    "ExperimentMetrics",
    "EvalMetrics",
    "Parameter",
    "Parameters",
    "get_experiment_metrics",
    "get_experiment_parameters",
    "download_artifact",
    "OpsmlTestServer",
    "OpsmlServerContext",
    "RegistryTestHelper",
]
