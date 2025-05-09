DataCards are used for storing, versioning, and tracking data. All DataCards require a `DataInterface` and optional metadata. 

## Create a Card

```python
from opsml.helpers.data import create_fake_data
import pandas as pd

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
???success "Data Splits"


### Sql Logic
???success "Sql Logic"