from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, validator

from opsml_artifacts.registry import CardRegistry, RunCard
from opsml_artifacts.registry.storage.storage_system import StorageClientType


class Tags(str, Enum):
    NAME = "name"
    TEAM = "team"
    EMAIL = "user_email"
    VERSION = "version"


class ProjectInfo(BaseModel):
    """
    A project identifier.

    Projects are identified by a combination of name and team. Each project must
    be unique within a team. The full project identifier is represented as
    "name:team".
    """

    name: str = Field(
        ...,
        description="The project name",
        min_length=1,
    )
    team: str = Field(
        ...,
        description="The owning team",
        min_length=1,
    )
    user_email: Optional[str] = None

    run_id: Optional[str] = Field(
        None,
        description="An existing run_id to use. If None, a new run is created when the project is activated",
    )

    tracking_uri: Optional[str] = Field(
        None,
        description="Tracking URI. Defaults to OPSML_TRACKING_URI",
    )

    @property
    def project_id(self) -> str:
        """The unique project identifier."""
        return f"{self.team}:{self.name}"

    @property
    def project_name(self) -> str:
        """The project name."""
        return self.name

    @validator("name", "team", pre=True)
    def identifier_validator(cls, value: Optional[str]) -> Optional[str]:  # pylint: disable=no-self-argument
        """Lowers and strips an identifier.

        This ensures we don't have any potentially duplicate (by case alone)
        project identifiers."""
        if value is None:
            return None
        return value.strip().lower().replace("_", "-")


class CardRegistries(BaseModel):
    datacard: CardRegistry
    modelcard: CardRegistry
    runcard: CardRegistry
    project: CardRegistry

    class Config:
        arbitrary_types_allowed = True
        allow_mutation = True

    def set_storage_client(self, storage_client: StorageClientType):
        self.datacard.registry.storage_client = storage_client
        self.modelcard.registry.storage_client = storage_client
        self.runcard.registry.storage_client = storage_client


# dataclass inheritance doesnt handle default vals well for <= py3.9
class RunInfo:
    def __init__(
        self,
        storage_client: StorageClientType,
        registries: CardRegistries,
        runcard: RunCard,
        run_id: str,
        run_name: Optional[str] = None,
    ):
        self.storage_client = storage_client
        self.registries = registries
        self.runcard = runcard
        self.run_id = run_id
        self.run_name = run_name
