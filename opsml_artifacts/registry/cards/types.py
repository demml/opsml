from dataclasses import dataclass
from enum import Enum
from typing import Optional


@dataclass
class StoragePath:
    uri: str


@dataclass
class CardInfo:
    name: Optional[str] = None
    team: Optional[str] = None
    user_email: Optional[str] = None
    uid: Optional[str] = None
    version: Optional[str] = None


class ArtifactStorageTypes(str, Enum):
    DATAFRAME = "DataFrame"
    ARROW_TABLE = "Table"
    NDARRAY = "ndarray"
    TF_MODEL = "keras"
    PYTORCH = "pytorch"
    JSON = "json"
    BOOSTER = "booster"


class CardType(str, Enum):
    DATA = "data"
    MODEL = "model"
    EXPERIMENT = "experiment"
    PIPELINE = "pipeline"


class CardName(str, Enum):
    DATACARD = "data"
    EXPERIMENTCARD = "experiment"
    MODELCARD = "model"
    PIPELINECARD = "pipeline"


NON_PIPELINE_CARDS = [card.value for card in CardType if card.value != "pipeline"]
DATA_ARTIFACTS = list(ArtifactStorageTypes)
