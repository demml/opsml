from dataclasses import dataclass
from typing import Protocol

from opsml_artifacts.registry.cards.cards import Card, CardType, VersionType


class Info(Protocol):
    _artifact_uri: str


class ActiveRun(Protocol):
    info: Info


@dataclass
class CardInfo:
    name: str
    team: str
    user_email: str | None = None
    uid: str | None = None
    version: str | None = None


@dataclass
class ExperimentInfo:
    name: str
    team: str
    user_email: str


class Experiment(Protocol):
    @property
    def artifact_save_path(self) -> str:
        ...

    @property
    def experiment_id(self) -> str:
        ...

    @property
    def run_id(self) -> str:
        ...

    def register_card(self, card: Card, version_type: VersionType) -> None:
        ...

    def load_card(self, card_type: CardType, info: CardInfo) -> Card:
        ...
