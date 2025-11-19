DataCards are used for storing, versioning, and tracking data. All DataCards require a `DataInterface` and optional metadata.

## Create a Card

```python
from opsml.data import (
    DataSplit,
    DataSplits,
    DependentVars,
    PandasData,
    ColumnSplit,
)
from opsml import DataCard, CardRegistry, RegistryType
from opsml.helpers.data import create_fake_data
import pandas as pd

registry = CardRegistry(RegistryType.Data)

# create data
X, y = cast(Tuple[pd.DataFrame, pd.DataFrame], create_fake_data(n_samples=1200))
X["target"] = y

# create data splits to store with the model (optional)
data_splits = [
    DataSplit(  # (1)
        label="train",
        start_stop_split=StartStopSplit(
            start=0,
            stop=1000,
        ),
    ),
    DataSplit(
        label="test",
        start_stop_split=StartStopSplit(
            start=1000,
            stop=1200,
        ),
    ),
]

# create DataCard
datacard = DataCard( # (3)
    interface=PandasData( # (2)
        data=X,
        data_splits=data_splits,
        dependent_vars=["target"],
    ),
    space="opsml",
    name="my_data",
    tags=["foo:bar", "baz:qux"],
)

# register DataCard
reg.data.register_card(datacard)
```

1. DataSplits allow you to create and store split logic with your DataInterface ensuring reproducibility
2. Here we are using the PandasData interface and passing in the pandas dataframe, data splits and are defining and dependent variable.
3. Create a DataCard and pass in the DataInterface, space, name, and tags.


### How it all works

As you can tell in the example above, `DataCards` are created by passing in a `DataInterface`, some required args and some optional args. The `DataInterface` is the interface is a library-specific interface for saving and extracting metadata from the data. It also allows us to standardize how data is saved (by following the library's guidelines) and ensures reproducibility.

## Load a Card's Components

By default, `OpsML` **does not** load any of the data components (data, preprocessor, etc.) when loading a card. This is to ensure that the card is loaded as quickly as possible. If you wish to load the data components, you can do so by calling the `load` method on the `DataCard` and provide any additional arguments via the `load_kwargs` argument.

```python
from opsml import CardRegistry, RegistryType

# start registries
reg = CardRegistry(RegistryType.Data)

# load the card
datacard = reg.load_card(uid="{{data uid}}")

# load the data
datacard.load()
```

???success "DataCard"
    ```python
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
        def created_at(self) -> datetime:
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
        def metadata(self) -> DataCardMetadata:  # pylint: disable=used-before-assignment
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
    ```

## Data Interface

The `DataInterface` is the primary interface for working with data in `Opsml`. It is designed to be subclassed and can be used to store data in a variety of formats depending on the library. Out of the box the following subclasses are available:

- `PandasData`: Stores data from a pytorch lightning model - [link](#pandasdata)
- `PolarsData`: Stores data from a huggingface model - [link](#polarsdata)
- `ArrowData`: Stores data from a sklearn model - [link](#arrowdata)
- `NumpyData`: Stores data from a pytorch model - [link](#numpydata)
- `TorchData`: Stores data from a tensorflow model - [link](#torchdata)
- `SqlData`: Stores data from a xgboost model - [link](#sqldata)


### Shared Arguments for all Data Interfaces

| Argument     | Description                          |
| ----------- | ------------------------------------ |
| <span class="text-alert">**data**</span>       | Data to associate with interface  |
| <span class="text-alert">**data_splits**</span>  | Optional data splits to associate with the data |
| <span class="text-alert">**dependent_vars**</span>    | Optional dependent variables to associate with the data. Can be one of `DependentVars`, List[str] or List[int]. Will be converted to `DependentVars`. dependent_vars is used in conjunction with data_splits to split data into X and y datasets based on the defined criteria. |
| <span class="text-alert">**sql_logic**</span> | Optional `SqlLogic` to associate with the interface |

???success "DataInterface"
    ```python
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

        def save(self, path: Path, save_kwargs: Optional[DataSaveKwargs] = None) -> DataInterfaceMetadata:
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
    ```

### Data Splits

With DataInterfaces it's possible to define a data split that can be used to split your data into different sets. This is typically useful for traditional ML models where you want to split your data into train, test and validation sets. The `DataSplit` class ensures reproducibility by storing the split logic with the data.

DataInterfaces support the following types of splits:

- `ColumnSplit`: Split the data based on a column value. This is common when using pandas or polars dataframes. `ColumnSplit` expects a column name, value, type (either builtin or timestamp) and an optional inequality (defualts to ==).
- `StartStopSplit`: Split the data based on a start and stop index. This is common when using numpy arrays or pyarrow tables. `StartStopSplit` expects a start and stop index.
- `IndiceSplit`: Split the data based on a list of indices. This is common when using numpy arrays or pyarrow tables. `IndiceSplit` expects a list of indices.

When creating a `DataSplit`, you must provide a label and at least one of the following: `ColumnSplit`, `StartStopSplit` or `IndiceSplit`

#### Creating Data Splits

```python
from opsml.data import DataSplit, ColumnSplit, StartStopSplit, IndiceSplit, Inequality, ColType

# Example of ColumnSplit
split = ColumnSplit(
    column_name="foo",
    column_value=3,
    column_type=ColType.Builtin,
    inequality=Inequality.LesserThan, # "<" will also work
)

# timestamp example
split = ColumnSplit(
    column_name="timestamp",
    column_value=datetime.datetime(2022, 1, 1).timestamp(),
    column_type=ColType.Timestamp,
    inequality=">",
)

# Example of StartStopSplit
split = DataSplit(
    label="train",
    start_stop_split=StartStopSplit(start=3, stop=5),
)

# Example of IndiceSplit
split = DataSplit(
    label="train",
    indice_split=IndiceSplit(
        indices=[0, 3],
    ),
)
```

???success "Data Splits"
    ```python

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
    ```

#### Using Data Splits

To split your data, you can use the `split_data` method on the `DataInterface`. This will return a dictionary mapping the split label and a `Data` object. The `Data` object holds both an x and y dataset. If your DataInterface contains a `DependentVars` object, the x and y datasets will be split based on the dependent variables. If no dependent variables are provided, only the x dataset will be returned.

```python
interface = PandasData(
    data=X,
    data_splits=[
        DataSplit(
            label="train",
            column_name="col_1",
            column_value=0.5,
            inequality=">="
            ),
        DataSplit(
            label="test",
            column_name="col_1",
            column_value=0.5,
            inequality="<"
        ),
    ],
    dependent_vars=["target"],
)

# Create and register datacard
datasets = interface.split_data()

# access the datasets
datasets["train"].x
datasets["train"].y
```

### Sql Logic

A DataInterface also accepts `SqlLogic` in the event a user wishes to store the sql logic used to create the data. This is useful as SQL logic tends to change frequently and having the logic that created the current data is helpful from a compliance and governance perspective.

The `SqlLogic` class is created by providing a dictionary of queries where each key is a unique name to provide to the query and the value is either a path to a `.sql` file or a string containing the SQL query.

```python
from opsml.data import SqlLogic

sql_logic = SqlLogic(queries={"sql": "test_sql.sql"})
sql_logic = SqlLogic(queries={"test": "SELECT * FROM TEST_TABLE"})
```

???success "Sql Logic"
    ```python
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
    ```
## PandasData

Interface for saving a Pandas DataFrame

**Example**: [`Link`](https://github.com/demml/opsml/tree/main/py-opsml/examples/data/pandas_data.py)

| Argument     | Description                          |
| ----------- | ------------------------------------ |
| <span class="text-alert">**data**</span>       | Data to associate with interface. This data must be a Pandas DataFrame  |
| <span class="text-alert">**data_splits**</span>  | Optional data splits to associate with the data |
| <span class="text-alert">**dependent_vars**</span>    | Optional dependent variables to associate with the data. Can be one of `DependentVars`, List[str] or List[int]. Will be converted to `DependentVars`. dependent_vars is used in conjunction with data_splits to split data into X and y datasets based on the defined criteria. |
| <span class="text-alert">**sql_logic**</span> | Optional `SqlLogic` to associate with the interface |interface. |
| <span class="text-alert">**data_profile**</span> | Optional `Scouter` data profile to associate with the data. This is a convenience argument if you already created a data profile. You can also use interface.create_data_profile(..) to create a data profile from the model interface. |

???success "PandasData"
    ```python
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

        def save(
            self, path: Path, save_kwargs: Optional[DataSaveKwargs] = None
        ) -> DataInterfaceMetadata:
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
    ```

### Nuts and Bolts

The `PandasData` interface uses the `to_parquet` method to save the data as a parquet file.

## PolarsData

Interface for saving a Polars DataFrame

**Example**: [`Link`](https://github.com/demml/opsml/tree/main/py-opsml/examples/data/polars_data.py)

| Argument     | Description                          |
| ----------- | ------------------------------------ |
| <span class="text-alert">**data**</span>       | Data to associate with interface. This data must be a Polars DataFrame  |
| <span class="text-alert">**data_splits**</span>  | Optional data splits to associate with the data |
| <span class="text-alert">**dependent_vars**</span>    | Optional dependent variables to associate with the data. Can be one of `DependentVars`, List[str] or List[int]. Will be converted to `DependentVars`. dependent_vars is used in conjunction with data_splits to split data into X and y datasets based on the defined criteria. |
| <span class="text-alert">**sql_logic**</span> | Optional `SqlLogic` to associate with the interface |interface. |
| <span class="text-alert">**data_profile**</span> | Optional `Scouter` data profile to associate with the data. This is a convenience argument if you already created a data profile. You can also use interface.create_data_profile(..) to create a data profile from the model interface. |

???success "PolarsData"
    ```python
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

        def save(
            self, path: Path, save_kwargs: Optional[DataSaveKwargs] = None
        ) -> DataInterfaceMetadata:
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
    ```

### Nuts and Bolts

The `PolarsData` interface uses the `write_parquet` method to save the data as a parquet file.

## ArrowData

Interface for saving pyarrow Table

**Example**: [`Link`](https://github.com/demml/opsml/tree/main/py-opsml/examples/data/arrow_data.py)

| Argument     | Description                          |
| ----------- | ------------------------------------ |
| <span class="text-alert">**data**</span>       | Data to associate with interface. This data must be a PyArrow table  |
| <span class="text-alert">**data_splits**</span>  | Optional data splits to associate with the data |
| <span class="text-alert">**dependent_vars**</span>    | Optional dependent variables to associate with the data. Can be one of `DependentVars`, List[str] or List[int]. Will be converted to `DependentVars`. dependent_vars is used in conjunction with data_splits to split data into X and y datasets based on the defined criteria. |
| <span class="text-alert">**sql_logic**</span> | Optional `SqlLogic` to associate with the interface |interface. |
| <span class="text-alert">**data_profile**</span> | Optional `Scouter` data profile to associate with the data. This is a convenience argument if you already created a data profile. You can also use interface.create_data_profile(..) to create a data profile from the model interface. |

???success "ArrowData"
    ```python
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

        def save(
            self, path: Path, save_kwargs: Optional[DataSaveKwargs] = None
        ) -> DataInterfaceMetadata:
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
    ```

### Nuts and Bolts

Arrow data is saved to parquet using the pyarrow library.

## NumpyData

Interface for saving a Numpy ndarray

**Example**: [`Link`](https://github.com/demml/opsml/tree/main/py-opsml/examples/data/numpy_data.py)

| Argument     | Description                          |
| ----------- | ------------------------------------ |
| <span class="text-alert">**data**</span>       | Data to associate with interface. This data must be a Numpy ndarray  |
| <span class="text-alert">**data_splits**</span>  | Optional data splits to associate with the data |
| <span class="text-alert">**dependent_vars**</span>    | Optional dependent variables to associate with the data. Can be one of `DependentVars`, List[str] or List[int]. Will be converted to `DependentVars`. dependent_vars is used in conjunction with data_splits to split data into X and y datasets based on the defined criteria. |
| <span class="text-alert">**sql_logic**</span> | Optional `SqlLogic` to associate with the interface |interface. |
| <span class="text-alert">**data_profile**</span> | Optional `Scouter` data profile to associate with the data. This is a convenience argument if you already created a data profile. You can also use interface.create_data_profile(..) to create a data profile from the model interface. |

???success "NumpyData"
    ```python
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
    ```

### Nuts and Bolts

Numpy data is saved to `npy` format using the `numpy.save` method.

## TorchData

Interface for saving a Torch Tensor or Torch Dataset

| Argument     | Description                          |
| ----------- | ------------------------------------ |
| <span class="text-alert">**data**</span>       | Data to associate with interface. This can be either a Torch tensor or Torch Dataset  |
| <span class="text-alert">**data_splits**</span>  | Optional data splits to associate with the data |
| <span class="text-alert">**dependent_vars**</span>    | Optional dependent variables to associate with the data. Can be one of `DependentVars`, List[str] or List[int]. Will be converted to `DependentVars`. dependent_vars is used in conjunction with data_splits to split data into X and y datasets based on the defined criteria. |
| <span class="text-alert">**sql_logic**</span> | Optional `SqlLogic` to associate with the interface |interface. |
| <span class="text-alert">**data_profile**</span> | Optional `Scouter` data profile to associate with the data. This is a convenience argument if you already created a data profile. You can also use interface.create_data_profile(..) to create a data profile from the model interface. |

???success "TorchData"
    ```python
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

        def save(
            self, path: Path, save_kwargs: Optional[DataSaveKwargs] = None
        ) -> DataInterfaceMetadata:
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
    ```

### Nuts and Bolts

Torch data is saved to to `pt` format using the `torch.save` method.

## SqlData

Interface for saving a SqlLogic. The `SqlData` interface is great for instances where you may not want to save the actual data object but want to have a record of the sql used to produce the data.

| Argument     | Description                          |
| ----------- | ------------------------------------ |
| <span class="text-alert">**sql_logic**</span> | Optional `SqlLogic` to associate with the interface |interface. |
| <span class="text-alert">**data_profile**</span> | Optional `Scouter` data profile to associate with the data. This is a convenience argument if you already created a data profile. You can also use interface.create_data_profile(..) to create a data profile from the model interface. |

???success "SqlData"
    ```python
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
    ```

## CustomData

**Example**: [`Link`](https://github.com/demml/opsml/tree/main/py-opsml/examples/data/custom_data.py)

While the above interfaces cover the most common use cases, there may be times where you want to create your own custom data interface similar to how ModelInterfaces work. By design, the `DataInterface` can be subclassed in cases where a more flexible implementation is needed. However to make sure all other components work nicely together, you will need to implement the following.

### Custom Save

- **save**: This method is called when saving the model. It should save the model and any other artifacts to the specified path. The method should return a `ModelInterfaceMetadata` object.

| Argument     | Description                          |
| ----------- | ------------------------------------ |
| <span class="text-alert">**path**</span>       | The base path to save artifacts to. **note** - this is typically injected at the time of saving. See the below example for how it should be used |
| <span class="text-alert">**save_kwargs**</span>       | Optional DataSaveKwargs to use when saving the data |


### Custom Load

To load custom data, you will need to implement the `load` method. This method is called when loading the data. It should load the data and any other artifacts from the specified path.

- **load**: This method is called when loading the data

| Argument     | Description                          |
| ----------- | ------------------------------------ |
| <span class="text-alert">**path**</span>       | The base path to load artifacts from. **note** - this is typically injected at the time of loading. See the below example for how it should be used |
| <span class="text-alert">**metadata**</span>       | `DataInterfaceSaveMetadata`. This will be injected by Opsml when the card is loaded from a registry  |
| <span class="text-alert">**load_kwargs**</span>       | Optional `DataLoadKwargs`. Additional load kwargs used to load a model and it's artifacts |
