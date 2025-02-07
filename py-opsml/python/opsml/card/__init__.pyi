from pathlib import Path
from typing import Dict, List, Optional, Union

from ..core import Description, FeatureSchema, SaveKwargs, Tags, LoadKwargs
from ..model import ModelInterface
from ..data import DataInterface, DataInterfaceSaveMetadata, DataType

class CardType:
    Data: "CardType"
    Model: "CardType"
    Run: "CardType"
    Project: "CardType"
    Audit: "CardType"
    Pipeline: "CardType"

class RegistryType:
    Data: "RegistryType"
    Model: "RegistryType"
    Run: "RegistryType"
    Project: "RegistryType"
    Audi: "RegistryType"
    Pipeline: "RegistryType"

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

# Registry

class DataCard:
    def __init__(  # pylint: disable=dangerous-default-value
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
            **kwargs:
                Additional kwargs to pass in.

        Kwargs:
            Kwargs are passed to the underlying data interface for saving.
            For a complete list of options see the save method of the data interface and
            their associated libraries.
        """

class DataCardMetadata:
    @property
    def data_type(self) -> DataType:
        """Return the data type"""

    @property
    def description(self) -> Description:
        """Return the data type"""

    @property
    def feature_map(self) -> FeatureSchema:
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

class ModelCardMetadata:
    @property
    def datacard_uid(self) -> str:
        """Returns the datacard uid"""

    @property
    def runcard_uid(self) -> str:
        """Returns the runcard uid"""

    @property
    def pipelinecard_uid(self) -> str:
        """Returns the runcard uid"""

    @property
    def auditcard_uid(self) -> str:
        """Returns the runcard uid"""

class ModelCard:
    def __init__(
        self,
        interface: ModelInterface,
        repository: Optional[str] = None,
        name: Optional[str] = None,
        contact: Optional[str] = None,
        verison: Optional[str] = None,
        uid: Optional[str] = None,
        info: Optional[CardInfo] = None,
        tags: Optional[Union[Dict[str, str], Tags]] = None,
        to_onnx: bool = False,
    ) -> None:
        """Create a ModelCard from a machine learning model.

        Cards are stored in the ModelCardRegistry and follow the naming convention of:
        {registry}/{repository}/{name}/v{version}

        Args:
            interface:
                `ModelInterface` class containing trained model
            repository:
                Repository to associate with `ModelCard`
            name:
                Name to associate with `ModelCard`
            contact:
                Contact to associate with `ModelCard`
            version:
                Current version (assigned if card has been registered). Follows
                semantic versioning.
            uid:
                Unique id (assigned if card has been registered)
            info:
                `CardInfo` object containing additional metadata. If provided, it will override any
                values provided for `name`, `repository`, `contact`, and `version`.

                Name, repository, and contact are required arguments for all cards. They can be provided
                directly or through a `CardInfo` object.
            tags:
                Tags to associate with `ModelCard`. Can be a dictionary of strings or
                a `Tags` object.
            to_onnx:
                Whether to convert the model to onnx or not during registration
        """

    @property
    def uri(self) -> Path:
        """Returns the uri of the `ModelCard` in the
        format of {registry}/{repository}/{name}/v{version}
        """

    @property
    def interface(self) -> ModelInterface:
        """Returns the `ModelInterface` associated with the `ModelCard`"""

    @interface.setter
    def interface(self, interface: ModelInterface) -> None:
        """Set the `ModelInterface` associated with the `ModelCard`"""

    @property
    def name(self) -> str:
        """Returns the name of the `ModelCard`"""

    @property
    def repository(self) -> str:
        """Returns the repository of the `ModelCard`"""

    @property
    def contact(self) -> str:
        """Returns the contact of the `ModelCard`"""

    @property
    def version(self) -> str:
        """Returns the version of the `ModelCard`"""

    @property
    def uid(self) -> str:
        """Returns the uid of the `ModelCard`"""

    @property
    def tags(self) -> Tags:
        """Returns the tags of the `ModelCard`"""

    @property
    def metadata(self) -> ModelCardMetadata:
        """Returns the metadata of the `ModelCard`"""

    @property
    def card_type(self) -> CardType:
        """Returns the card type of the `ModelCard`"""

    def save(self, path: Path, save_kwargs: Optional[SaveKwargs] = None) -> None:
        """Save the model card to a directory

        Args:
            path (Path):
                Path to save the model card.
            save_kwargs (SaveKwargs):
                Optional kwargs to pass to `ModelInterface` save method.
        """

    def load(
        self,
        path: Path,
        model: bool = True,
        onnx: bool = False,
        drift_profile: bool = False,
        sample_data: bool = False,
        load_kwargs: None | LoadKwargs = None,
    ) -> None:
        """Load ModelInterface components

        Args:
            path (Path):
                Path to load the model
            model (bool):
                Whether to load the model. Defaults to True.
            onnx (bool):
                Whether to load the onnx model. Defaults to False.
            drift_profile (bool):
                Whether to load the drift profile. Defaults to False.
            sample_data (bool):
                Whether to load the sample data. Defaults to False.
            load_kwargs (LoadKwargs):
                Optional kwargs to pass to `ModelInterface` load method.
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
