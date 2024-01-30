# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
import time
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, ConfigDict, model_validator

from opsml.types import CardVersion, CommonKwargs, RegistryType


def get_timestamp() -> int:
    return int(round(time.time() * 1_000_000))


class RunUris(BaseModel):
    runcard_uri: str


class SaveRecord(BaseModel):
    name: str
    repository: str
    contact: str
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
        values["sample_data_type"] = metadata["data_schema"]["data_type"]
        values["model_type"] = values["interface"]["model_type"]
        values["runcard_uid"] = metadata["runcard_uid"]
        values["pipelinecard_uid"] = metadata["pipelinecard_uid"]
        values["auditcard_uid"] = metadata["auditcard_uid"]
        values["datacard_uid"] = values.get("datacard_uid") or CommonKwargs.UNDEFINED.value

        return values


class RunRegistryRecord(SaveRecord):
    datacard_uids: Optional[List[str]] = None
    modelcard_uids: Optional[List[str]] = None
    pipelinecard_uid: Optional[str] = None
    project: Optional[str] = None
    artifact_uris: Optional[Dict[str, Dict[str, str]]] = None
    tags: Dict[str, Union[str, int]]
    timestamp: int = get_timestamp()


class PipelineRegistryRecord(SaveRecord):
    pipeline_code_uri: Optional[str] = None
    datacard_uids: List[str]
    modelcard_uids: List[str]
    runcard_uids: List[str]
    timestamp: int = get_timestamp()


class ProjectRegistryRecord(BaseModel):
    uid: str
    name: str
    repository: str
    project_id: int
    version: Optional[str] = None
    timestamp: int = get_timestamp()


class AuditRegistryRecord(SaveRecord):
    approved: bool
    datacards: List[CardVersion]
    modelcards: List[CardVersion]
    runcards: List[CardVersion]
    timestamp: int = get_timestamp()

    @model_validator(mode="before")
    @classmethod
    def set_metadata(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        metadata: Dict[str, Any] = values["metadata"]
        values["datacards"] = metadata["datacards"]
        values["modelcards"] = metadata["modelcards"]
        values["runcards"] = metadata["runcards"]

        return values


registry_name_record_map: Dict[str, Any] = {
    RegistryType.DATA.value: DataRegistryRecord,
    RegistryType.MODEL.value: ModelRegistryRecord,
    RegistryType.RUN.value: RunRegistryRecord,
    RegistryType.PIPELINE.value: PipelineRegistryRecord,
    RegistryType.AUDIT.value: AuditRegistryRecord,
    RegistryType.PROJECT.value: ProjectRegistryRecord,
}
