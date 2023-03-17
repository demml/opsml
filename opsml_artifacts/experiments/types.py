from typing import Protocol

from dataclasses import dataclass
from enum import Enum

from opsml_artifacts.registry.cards.cards import Card, CardType, VersionType


class Info(Protocol):
    _artifact_uri: str


class ActiveRun(Protocol):
    info: Info


class ExperimentType(str, Enum):
    MLFLOW = "mlflow"


@dataclass
class ExperimentInfo:
    name: str
    team: str
    user_email: str | None = None
    uid: str | None = None
    version: str | None = None


class Experiment(Protocol):
    def artifact_save_path(self) -> str:
        ...

    def experiment_id(self) -> str:
        ...

    def run_id(self) -> str:
        ...

    def register_card(self, card: Card, version_type: VersionType) -> None:
        ...

    def load_card(self, card_type: CardType, info: ExperimentInfo) -> Card:
        ...
