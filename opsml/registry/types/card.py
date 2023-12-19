# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
import datetime
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel

from opsml.helpers.logging import ArtifactLogger
from opsml.registry.types.model import ModelCardMetadata

logger = ArtifactLogger.get_logger()


class RegistryType(str, Enum):
    DATA = "data"
    MODEL = "model"
    RUN = "run"
    PIPELINE = "pipeline"
    AUDIT = "audit"
    PROJECT = "project"

    @staticmethod
    def from_str(name: str) -> "RegistryType":
        l_name = name.strip().lower()
        if l_name == "data":
            return RegistryType.DATA
        if l_name == "model":
            return RegistryType.MODEL
        if l_name == "run":
            return RegistryType.RUN
        if l_name == "pipeline":
            return RegistryType.PIPELINE
        if l_name == "project":
            return RegistryType.PROJECT
        if l_name == "audit":
            return RegistryType.AUDIT
        raise NotImplementedError()


class Metric(BaseModel):
    name: str
    value: Union[float, int]
    step: Optional[int] = None
    timestamp: Optional[int] = None


class Param(BaseModel):
    name: str
    value: Union[float, int, str]


METRICS = Dict[str, List[Metric]]
PARAMS = Dict[str, List[Param]]


class Comment(BaseModel):
    name: str
    comment: str
    timestamp: str = str(datetime.datetime.today().strftime("%Y-%m-%d %H:%M"))

    def __eq__(self, other):  # type: ignore
        return self.__dict__ == other.__dict__


@dataclass
class CardInfo:

    """
    Class that holds info related to an Artifact Card

    Args:
        name:
            Name of card
        team:
            Team name
        user_email:
            Email
        uid:
            Unique id of card
        version:
            Version of card
        tags:
            Tags associated with card
    """

    name: Optional[str] = None
    team: Optional[str] = None
    user_email: Optional[str] = None
    uid: Optional[str] = None
    version: Optional[str] = None
    tags: Optional[Dict[str, str]] = None


class CardType(str, Enum):
    DATACARD = "data"
    RUNCARD = "run"
    MODELCARD = "model"
    PIPELINECARD = "pipeline"
    PROJECTCARD = "project"
    AUDITCARD = "audit"


class PipelineCardArgs(str, Enum):
    DATA_UIDS = "datacard_uids"
    MODEL_UIDS = "modelcard_uids"
    RUN_UIDS = "runcard_uids"


class RunCardArgs(str, Enum):
    DATA_UID = "datacard_uid"
    MODEL_UIDS = "modelcard_uids"
    PIPELINE_UID = "pipelinecard_uid"


class CardVersion(BaseModel):
    name: str
    version: str
    card_type: CardType


class AuditCardMetadata(BaseModel):
    audit_uri: Optional[str] = None
    datacards: List[CardVersion] = []
    modelcards: List[CardVersion] = []
    runcards: List[CardVersion] = []


NON_PIPELINE_CARDS = [card.value for card in CardType if card.value not in ["pipeline", "project", "audit"]]

AuditSectionType = Dict[str, Dict[int, Dict[str, str]]]


@dataclass
class StoragePath:
    uri: str


@dataclass
class HuggingFaceStorageArtifact:
    model_interface: Any
    metadata: ModelCardMetadata
    to_onnx: bool = False
