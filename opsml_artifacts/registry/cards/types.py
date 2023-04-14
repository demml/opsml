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


# class CardType(str, Enum):
# DATA = "data"
# MODEL = "model"
# RUN = "run"
# PIPELINE = "pipeline"


class CardType(str, Enum):
    DATACARD = "data"
    RUNCARD = "run"
    MODELCARD = "model"
    PIPELINECARD = "pipeline"
    PROJECTCARD = "project"


class PipelineCardArgs(str, Enum):
    DATA_UIDS = "datacard_uids"
    MODEL_UIDS = "modelcard_uids"
    RUN_UIDS = "runcard_uids"


class RunCardArgs(str, Enum):
    DATA_UID = "datacard_uid"
    MODEL_UIDS = "modelcard_uids"
    PIPELINE_UID = "pipelinecard_uid"


NON_PIPELINE_CARDS = [card.value for card in CardType if card.value not in ["pipeline", "project"]]
