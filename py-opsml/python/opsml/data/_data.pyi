from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from ..model import ExtraMetadata, FeatureSchema
from ..scouter.profile import DataProfile

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
    sql_logic: SqlLogic  # pylint: disable=used-before-assignment
    interface_type: DataInterfaceType
    data_splits: DataSplits
    dependent_vars: DependentVars
    data_type: DataType

    def __init__(
        self,
        save_metadata: DataInterfaceSaveMetadata,
        schema: FeatureSchema,
        extra_metadata: dict[str, str],
        sql_logic: SqlLogic,
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
        sql_logic: Optional[SqlLogic] = None,
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
    def data_profile(self) -> Optional[DataProfile]: ...

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
