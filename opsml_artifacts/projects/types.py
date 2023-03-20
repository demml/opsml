from dataclasses import dataclass
from typing import Optional, Protocol

from opsml_artifacts.registry.cards import cards


@dataclass
class ProjectInfo:
    name: str
    team: str
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

    def register_card(self, card: cards.Card, version_type: cards.VersionType) -> None:
        ...

    def load_card(self, card_type: cards.CardType, info: cards.CardInfo) -> cards.Card:
        ...
