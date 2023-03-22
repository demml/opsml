from typing import Optional, Protocol

from pydantic import BaseModel, Field

from opsml_artifacts.registry.cards import cards


class ProjectInfo(BaseModel):
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


class Project(Protocol):
    @property
    def artifact_save_path(self) -> str:
        ...

    @property
    def project_id(self) -> str:
        ...

    @property
    def run_id(self) -> Optional[str]:
        ...

    def register_card(self, card: cards.ArtifactCard, version_type: cards.VersionType) -> None:
        ...

    def load_card(self, card_type: cards.CardType, info: cards.CardInfo) -> cards.ArtifactCard:
        ...
