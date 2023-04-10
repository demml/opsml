from typing import Optional, Protocol
from enum import Enum
from dataclasses import dataclass
from pydantic import BaseModel, Field, validator

from opsml_artifacts import CardRegistry, VersionType
from opsml_artifacts.registry.cards.cards import ArtifactCard
from opsml_artifacts.registry.cards.types import CardInfo, CardType
from opsml_artifacts.registry.storage.storage_system import StorageClientType


class Tags(str, Enum):
    NAME = "name"
    TEAM = "team"
    EMAIL = "user_email"


class ProjectInfo(BaseModel):
    """A project identifier.

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

    @property
    def project_id(self) -> str:
        """The unique project identifier."""
        return f"{self.team}:{self.name}"

    @validator("name", "team", pre=True)
    def identifier_validator(cls, value: Optional[str]) -> Optional[str]:  # pylint: disable=no-self-argument
        """Lowers and strips an identifier.

        This ensures we don't have any potentially duplicate (by case alone)
        project identifiers."""
        if value is None:
            return None
        return value.strip().lower()


class CardRegistries(BaseModel):
    datacard: CardRegistry
    modelcard: CardRegistry
    runcard: CardRegistry

    class Config:
        arbitrary_types_allowed = True
        allow_mutation = True

    def set_storage_client(self, storage_client: StorageClientType):
        self.datacard.registry.storage_client = storage_client
        self.modelcard.registry.storage_client = storage_client
        self.runcard.registry.storage_client = storage_client


@dataclass
class RunInfo:
    run_id: str
    project_info: ProjectInfo
    storage_client: StorageClientType
    registries: CardRegistries
    run_name: Optional[str] = None
