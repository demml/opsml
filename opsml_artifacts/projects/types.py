from typing import Optional, Protocol

from pydantic import BaseModel, Field, validator

from opsml_artifacts import VersionType
from opsml_artifacts.registry.cards import cards


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


class Project(Protocol):
    """A project is a top level container for storing artifacts.

    Each project contains one or more runs. A run is typically an instance of a
    model training run. Artifacts (cards) are associated with a run.
    """

    @property
    def artifact_save_path(self) -> str:
        ...

    @property
    def project_id(self) -> str:
        ...

    @property
    def run_id(self) -> Optional[str]:
        ...

    def register_card(self, card: cards.ArtifactCard, version_type: VersionType) -> None:
        ...

    def load_card(self, card_type: cards.CardType, info: cards.CardInfo) -> cards.ArtifactCard:
        ...
