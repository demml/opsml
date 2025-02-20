# pylint: disable=dangerous-default-value

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from ..core import FeatureSchema, VersionType
from ..data import DataInterface, DataLoadKwargs, DataSaveKwargs, DataType
from ..model import ModelInterface, ModelLoadKwargs, ModelSaveKwargs

class RegistryType:
    Data: "RegistryType"
    Model: "RegistryType"
    Run: "RegistryType"
    Audit: "RegistryType"

class RegistryMode:
    Client: "RegistryMode"
    Server: "RegistryMode"

class Card:
    uid: Optional[str]
    created_at: Optional[str]
    app_env: Optional[str]
    name: str
    repository: str
    version: str
    tags: Dict[str, str]
    datacard_uids: Optional[List[str]]
    modelcard_uids: Optional[List[str]]
    runcard_uids: Optional[List[str]]
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

    def __len__(self) -> int:
        """Return the length of the card list"""

# Registry

class DataCard:
    def __init__(  # pylint: disable=dangerous-default-value
        self,
        interface: Optional[DataInterface] = None,
        repository: Optional[str] = None,
        name: Optional[str] = None,
        version: Optional[str] = None,
        uid: Optional[str] = None,
        tags: List[str] = [],
    ) -> None:
        """Define a data card

        Args:
            interface (DataInterface | None):
                The data interface
            repository (str | None):
                The repository of the card
            name (str | None):
                The name of the card
            version (str | None):
                The version of the card
            uid (str | None):
                The uid of the card
            tags (List[str]):
                The tags of the card
        """

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
    def repository(self) -> str:
        """Return the repository of the data card"""

    @repository.setter
    def repository(self, repository: str) -> None:
        """Set the repository of the data card

        Args:
            repository (str):
                The repository of the data card
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

class DataCardMetadata:
    @property
    def schema(self) -> FeatureSchema:
        """Return the feature map"""

    @property
    def runcard_uid(self) -> Optional[str]:
        """Return the runcard uid"""

    @property
    def auditcard_uid(self) -> Optional[str]:
        """Return the runcard uid"""

class RegistryTestHelper:
    """Helper class for testing the registry"""

    def __init__(self) -> None: ...
    def setup(self) -> None: ...
    def cleanup(self) -> None: ...

class ModelCardMetadata:
    @property
    def datacard_uid(self) -> str:
        """Returns the datacard uid"""

    @datacard_uid.setter
    def datacard_uid(self, datacard_uid: str) -> None:
        """Set the datacard uid"""

    @property
    def runcard_uid(self) -> str:
        """Returns the runcard uid"""

    @runcard_uid.setter
    def runcard_uid(self, runcard_uid: str) -> None:
        """Set the runcard uid"""

    @property
    def auditcard_uid(self) -> str:
        """Returns the runcard uid"""

    @auditcard_uid.setter
    def auditcard_uid(self, auditcard_uid: str) -> None:
        """Set the runcard uid"""

class ModelCard:
    def __init__(
        self,
        interface: Optional[ModelInterface] = None,
        repository: Optional[str] = None,
        name: Optional[str] = None,
        version: Optional[str] = None,
        uid: Optional[str] = None,
        tags: List[str] = [],
        metadata: ModelCardMetadata = ModelCardMetadata(),
        to_onnx: bool = False,
    ) -> None:
        """Create a ModelCard from a machine learning model.

        Cards are stored in the ModelCardRegistry and follow the naming convention of:
        {registry}/{repository}/{name}/v{version}

        Args:
            interface (ModelInterface | None):
                `ModelInterface` class containing trained model
            repository (str | None):
                Repository to associate with `ModelCard`
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
            metadata (ModelCardMetadata):
                Metadata to associate with the `ModelCard. Defaults to an empty `ModelCardMetadata` object.
            to_onnx:
                Whether to convert the model to onnx or not during registration
        """

    @property
    def app_env(self) -> str:
        """Returns the app env"""

    @property
    def created_at(self) -> datetime:
        """Returns the created at timestamp"""

    @property
    def datacard_uid(self) -> str:
        """Returns the datacard uid"""

    @datacard_uid.setter
    def datacard_uid(self, datacard_uid: str) -> None:
        """Set the datacard uid"""

    @property
    def runcard_uid(self) -> str:
        """Returns the runcard uid"""

    @runcard_uid.setter
    def runcard_uid(self, runcard_uid: str) -> None:
        """Set the runcard uid"""

    @property
    def uri(self) -> Path:
        """Returns the uri of the `ModelCard` in the
        format of {registry}/{repository}/{name}/v{version}
        """

    @property
    def interface(self) -> Any:
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
    def repository(self) -> str:
        """Returns the repository of the `ModelCard`"""

    @repository.setter
    def repository(self, repository: str) -> None:
        """Set the repository of the `ModelCard`

        Args:
            repository (str):
                The repository of the `ModelCard`
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
        onnx: bool = False,
        load_kwargs: None | ModelLoadKwargs = None,
    ) -> None:
        """Load ModelCard interface components

        Args:
            path (Path | None):
                The path to load the data card from. If no path is provided,
                the model interface will be loaded from the server.
            onnx (bool):
                Whether to load the model as onnx or not.
                Only available for models that have been converted to onnx.
            load_kwargs (ModelLoadKwargs):
                Optional kwargs to pass to `ModelInterface` load method.
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
    def model_validate_json(
        json_str: str, interface: Optional[ModelInterface] = None
    ) -> "ModelCard":
        """Validate the model json string

        Args:
            json_str (str):
                The json string to validate
            interface (ModelInterface):
                By default, the interface willbe inferred and insantiated
                from the interface metdata. If an interface is provided
                (as in the case of custom interfaces), it will be used.
        """

    def __str__(self) -> str:
        """Return a string representation of the ModelCard.

        Returns:
            String representation of the ModelCard.
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

class ActiveRun:
    def __enter__(self) -> "ActiveRun": ...
    def __exit__(self, exc_type, exc_value, traceback) -> None: ...
    def start_run(
        self,
        repository: Optional[str] = None,
        name: Optional[str] = None,
        code_dir: Optional[str] = None,
        log_hardware: bool = False,
    ) -> "ActiveRun": ...
    def log_artifact(self, artifact: Any, name: str, description: str) -> None: ...
    def log_artifacts(self, artifacts: Dict[str, Any]) -> None: ...
    def log_metric(
        self, metric: Union[int, float], name: str, description: str
    ) -> None: ...
    def log_metrics(self, metrics: Dict[str, Union[int, float]]) -> None: ...
    def log_param(
        self, param: Union[int, float, str], name: str, description: str
    ) -> None: ...
    def log_params(self, params: Dict[str, Union[int, float, str]]) -> None: ...
    def log_tag(self, tag: str) -> None: ...

class RunCard:
    def __init__(
        self,
        repository: Optional[str] = None,
        name: Optional[str] = None,
        version: Optional[str] = None,
        uid: Optional[str] = None,
        tags: List[str] = [],
    ) -> None:
        """Creates a RunCard.

        Cards are stored in the RunCard Registry and follow the naming convention of:
        {registry}/{repository}/{name}/v{version}

        Args:
            repository (str | None):
                Repository to associate with `RunCard`
            name (str | None):
                Name to associate with `RunCard`
            version (str | None):
                Current version (assigned if card has been registered). Follows
                semantic versioning.
            uid (str | None):
                Unique id (assigned if card has been registered)
            tags (List[str]):
                Tags to associate with `RunCard`. Can be a dictionary of strings or
                a `Tags` object.
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
    def repository(self) -> str:
        """Returns the repository of the `RunCard`"""

    @repository.setter
    def repository(self, repository: str) -> None:
        """Set the repository of the `RunCard`

        Args:
            repository (str):
                The repository of the `RunCard`
        """

    @property
    def version(self) -> str:
        """Returns the version of the `RunCard`"""

    @version.setter
    def version(self, version: str) -> None:
        """Set the version of the `RunCard`

        Args:
            version (str):
                The version of the `RunCard`
        """

    @property
    def uid(self) -> str:
        """Returns the uid of the `RunCard`"""

    @property
    def tags(self) -> List[str]:
        """Returns the tags of the `RuncCard`"""

    @property
    def runcard_uids(self) -> List[str]:
        """Returns the runcard uids"""

    @property
    def datacard_uids(self) -> List[str]:
        """Returns the datacard uids"""

    @property
    def modelcard_uids(self) -> List[str]:
        """Returns the modelcard uids"""

    @property
    def artifacts(self) -> List[str]:
        """Returns the artifact names"""

    @property
    def compute_environment(self) -> ComputeEnvironment:
        """Returns the compute env"""

    @property
    def registry_type(self) -> RegistryType:
        """Returns the card type of the `RunCard`"""

    @property
    def app_env(self) -> str:
        """Returns the app env"""

    @property
    def created_at(self) -> datetime:
        """Returns the created at timestamp"""

    @staticmethod
    def start_run(
        repository: Optional[str] = None,
        name: Optional[str] = None,
        code_dir: Optional[str] = None,
        log_hardware: bool = False,
    ) -> ActiveRun:
        """Start a run

        Args:
            repository (str | None):
                Repository to associate with `RunCard`
            name (str | None):
                Name to associate with `RunCard`
            code_dir (str | None):
                Directory to log code from
            log_hardware (bool):
                Whether to log hardware information or not

        Returns:
            ActiveRun
        """

class CardRegistry:
    def __init__(self, registry_type: RegistryType | str) -> None:
        """Interface for connecting to any of the Card registries

        Args:
            registry_type (RegistryType | str):
                The type of registry to connect to. Can be a `RegistryType` or a string

        Returns:
            Instantiated connection to specific Card registry


        Example:
            data_registry = CardRegistry(RegistryType.Data)
            data_registry.list_cards()

            or
            data_registry = CardRegistry("data")
            data_registry.list_cards()
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
        repository: Optional[str] = None,
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
            repository (str):
                Optional repository associated with card
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
        card: Union[DataCard, ModelCard],
        version_type: VersionType = VersionType.Minor,
        pre_tag: Optional[str] = None,
        build_tag: Optional[str] = None,
        save_kwargs=Optional[ModelSaveKwargs | DataSaveKwargs],
    ) -> None:
        """Register a Card

        Args:
            card (ArtifactCard):
                Card to register. Can be a DataCard, ModelCard,
                RunCard.
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
        repository: Optional[str] = None,
        name: Optional[str] = None,
        version: Optional[str] = None,
        interface: Optional[Union[DataInterface, ModelInterface]] = None,
    ) -> Any:
        """Load a Card from the registry

        Args:
            uid (str):
                Unique identifier for Card. If present, the uid takes precedence
            repository (str):
                Optional repository associated with card
            name (str):
                Optional name of card
            version (str):
                Optional version number of existing data. If not specified, the
                most recent version will be used
            interface (Union[DataInterface, ModelInterface]):
                Optional interface to load the card into

        Returns:
            Card
        """

    def update_card(
        self,
        card: Union[DataCard, ModelCard],
    ) -> None:
        """Update a Card in the registry.
        Note: This will only update the registry record for a given card. It
        will not re-save/update the underlying artifacts (except for metadata).

        Args:
            card (ArtifactCard):
                Card to update. Can be a DataCard, ModelCard,
                RunCard.
        """

    def delete_card(
        self,
        card: Union[DataCard, ModelCard],
    ) -> None:
        """Delete a Card from the registry. This will also remove
        the underlying artifacts associated with the card.

        Args:
            card (ArtifactCard):
                Card to delete. Can be a DataCard, ModelCard,
                RunCard.
        """
