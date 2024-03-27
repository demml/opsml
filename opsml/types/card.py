# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
from __future__ import annotations

import datetime
import os
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Union

from pydantic import BaseModel, SerializeAsAny


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


class RunGraph(BaseModel):
    name: str
    x_label: str
    y_label: str
    x: List[Union[float, int]]
    y: Union[Dict[str, List[Union[float, int]]], List[Union[float, int]]]
    graph_type: str = "single"
    graph_style: str = "line"


class Artifact(BaseModel):
    local_path: str
    remote_path: str
    name: str


Metrics = Dict[str, List[Metric]]
Params = Dict[str, List[Param]]
ArtifactUris = Dict[str, Artifact]


class Comment(BaseModel):
    name: str
    comment: str
    timestamp: str = str(datetime.datetime.today().strftime("%Y-%m-%d %H:%M"))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Comment):
            return False
        return self.__dict__ == other.__dict__


@dataclass
class CardInfo:
    """
    Class that holds info related to an Artifact Card

    Args:
        name:
            Name of card
        repository:
            repository name
        contact:
            Contact information
        uid:
            Unique id of card
        version:
            Version of card
        tags:
            Tags associated with card
    """

    name: Optional[str] = None
    repository: Optional[str] = None
    contact: Optional[str] = None
    uid: Optional[str] = None
    version: Optional[str] = None
    tags: Optional[Dict[str, str]] = None

    def set_env(self) -> "CardInfo":
        """Helper to set environment variables for the current runtime environment"""

        for key in ["name", "repository", "contact"]:
            value = getattr(self, key)

            if value is not None:
                os.environ[f"OPSML_RUNTIME_{key.upper()}"] = value

        return self


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
    datacards: List[SerializeAsAny[CardVersion]] = []
    modelcards: List[SerializeAsAny[CardVersion]] = []
    runcards: List[SerializeAsAny[CardVersion]] = []


NON_PIPELINE_CARDS = [card.value for card in CardType if card.value not in ["pipeline", "project", "audit"]]

AuditSectionType = Dict[str, Dict[int, Dict[str, str]]]
