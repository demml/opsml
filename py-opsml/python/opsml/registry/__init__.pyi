from typing import List, Optional, Union
from datetime import datetime
from ..card import ModelCard, DataCard
from ..core import VersionType, SaveKwargs

ArtifactCard = Union[ModelCard, DataCard]

class Card:
    @property
    def uid(self) -> str: ...
    @property
    def created_at(self) -> Optional[datetime]: ...
    @property
    def app_env(self) -> str: ...
    @property
    def repository(self) -> str: ...
    @property
    def name(self) -> str: ...
    @property
    def version(self) -> str: ...
    @property
    def contact(self) -> str: ...
    @property
    def tags(self) -> List[str]: ...
    @property
    def datacard_uids(self) -> List[str]: ...
    @property
    def modelcard_uids(self) -> List[str]: ...
    @property
    def runcard_uids(self) -> List[str]: ...
    @property
    def pipelinecard_uid(self) -> str: ...
    @property
    def auditcard_uid(self) -> str: ...
    @property
    def interface_type(self) -> Optional[str]: ...
    @property
    def data_type(self) -> Optional[str]: ...
    @property
    def model_type(self) -> Optional[str]: ...
    @property
    def task_type(self) -> Optional[str]: ...
    def __str__(self): ...

class CardList:
    """List of Cards from a registry"""

    cards: List[Card]

    def __str__(self): ...

class RegistryType:
    Data: "RegistryType"
    Model: "RegistryType"
    Run: "RegistryType"
    Project: "RegistryType"
    Audit: "RegistryType"
    Pipeline: "RegistryType"

class RegistryMode:
    Client: "RegistryMode"
    Server: "RegistryMode"

class CardRegistry:
    def __init___(self, registry_type: RegistryType):
        """Interface for connecting to any of the Card registries

        Args:
            registry_type (RegistryType):
                The type of registry to connect to

        Returns:
            Instantiated connection to specific Card registry


        Example:
            data_registry = CardRegistry(RegistryType.DATA)
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
        card: ArtifactCard,
        version_type: VersionType,
        pre_tag: Optional[str] = None,
        build_tag: Optional[str] = None,
        save_kwargs=Optional[SaveKwargs],
    ) -> None:
        """Register a Card

        Args:
            card (ArtifactCard):
                Card to register. Can be a DataCard, ModelCard,
                RunCard, ProjectCard
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
