# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
import tempfile
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import joblib
from pydantic import BaseModel, ConfigDict, model_validator

from opsml.registry.storage import client
from opsml.registry.types import (
    CardVersion,
    Suffix,
)


def get_timestamp() -> int:
    return int(round(time.time() * 1_000_000))


def load_card(rpath: str, object_path: str) -> Dict[str, Any]:
    """Loads an ArtifactCard definition from a server path

    Args:
        rpath:
            server path
        object_path:
            object-specific name for pathing

    Returns:
        Dictionary to be inserted into ArtifactCard
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        lpath = Path(tmp_dir)

        load_lpath = Path(lpath, object_path).with_suffix(Suffix.JOBLIB.value)
        load_rpath = Path(rpath, object_path).with_suffix(Suffix.JOBLIB.value)

        client.storage_client.get(load_rpath, load_lpath)

        card: Dict[str, Any] = joblib.load(load_lpath)
        return card


class RunUris(BaseModel):
    runcard_uri: str


class AuditUris(BaseModel):
    audit_uri: str


class SaveRecord(BaseModel):
    name: str
    team: str
    user_email: str
    uid: Optional[str] = None
    version: str
    tags: Dict[str, str]


class DataRegistryRecord(SaveRecord):
    data_type: Optional[str] = None
    timestamp: int = get_timestamp()
    runcard_uid: Optional[str] = None
    pipelinecard_uid: Optional[str] = None
    auditcard_uid: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def set_metadata(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        metadata: Dict[str, Any] = values["metadata"]
        values["data_type"] = metadata["data_type"]
        values["runcard_uid"] = metadata["runcard_uid"]
        values["pipelinecard_uid"] = metadata["pipelinecard_uid"]
        values["auditcard_uid"] = metadata["auditcard_uid"]

        return values


class ModelRegistryRecord(SaveRecord):
    datacard_uid: str
    sample_data_type: str
    model_type: str
    timestamp: int = get_timestamp()
    runcard_uid: Optional[str] = None
    pipelinecard_uid: Optional[str] = None
    auditcard_uid: Optional[str] = None

    model_config = ConfigDict(protected_namespaces=("protect_",))

    @model_validator(mode="before")
    @classmethod
    def set_metadata(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        metadata: Dict[str, Any] = values["metadata"]
        values["sample_data_type"] = metadata["sample_data_type"]
        values["model_type"] = metadata["model_type"]
        values["runcard_uid"] = metadata["runcard_uid"]
        values["pipelinecard_uid"] = metadata["pipelinecard_uid"]
        values["auditcard_uid"] = metadata["auditcard_uid"]

        return values


class RunRegistryRecord(SaveRecord):
    datacard_uids: Optional[List[str]] = None
    modelcard_uids: Optional[List[str]] = None
    pipelinecard_uid: Optional[str] = None
    project_id: Optional[str] = None
    artifact_uris: Optional[Dict[str, str]] = None
    tags: Dict[str, str]
    timestamp: int = get_timestamp()
    runcard_uri: str


class PipelineRegistryRecord(SaveRecord):
    pipeline_code_uri: Optional[str] = None
    datacard_uids: List[str]
    modelcard_uids: List[str]
    runcard_uids: List[str]
    timestamp: int = get_timestamp()


class ProjectRegistryRecord(BaseModel):
    uid: str
    name: str
    team: str
    project_id: str
    version: Optional[str] = None
    description: Optional[str] = None
    timestamp: int = get_timestamp()


class AuditRegistryRecord(SaveRecord):
    approved: bool
    audit_uri: str
    datacards: List[CardVersion]
    modelcards: List[CardVersion]
    runcards: List[CardVersion]
    timestamp: int = get_timestamp()

    @model_validator(mode="before")
    @classmethod
    def set_metadata(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        metadata: Dict[str, Any] = values["metadata"]
        values["audit_uri"] = metadata["audit_uri"]
        values["datacards"] = metadata["datacards"]
        values["modelcards"] = metadata["modelcards"]
        values["runcards"] = metadata["runcards"]

        return values


RegistryRecord = Union[
    DataRegistryRecord,
    ModelRegistryRecord,
    RunRegistryRecord,
    PipelineRegistryRecord,
    ProjectRegistryRecord,
    AuditRegistryRecord,
]
