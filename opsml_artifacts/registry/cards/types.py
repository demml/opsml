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
    RUN = "run"
    PIPELINE = "pipeline"


class CardName(str, Enum):
    DATACARD = "data"
    RUNCARD = "run"
    MODELCARD = "model"
    PIPELINECARD = "pipeline"


class PipelineCardArgs(str, Enum):
    DATA_UIDs = "datacard_uids"
    MODEL_UIDs = "modelcard_uids"
    RUN_UIDS = "runcard_uids"


class RunCardArgs(str, Enum):
    DATA_UID = "datacard_uid"
    MODEL_UIDs = "modelcard_uids"
    PIPELINE_UID = "pipelinecard_uid"


NON_PIPELINE_CARDS = [card.value for card in CardType if card.value != "pipeline"]
DATA_ARTIFACTS = list(ArtifactStorageTypes)
