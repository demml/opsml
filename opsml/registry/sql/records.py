# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
import time
from typing import Any, Dict, List, Optional, Union, cast

from pydantic import BaseModel, ConfigDict, model_validator

from opsml.registry.types import (
    METRICS,
    PARAMS,
    AuditCardMetadata,
    CardVersion,
    Comment,
    DataCardMetadata,
    ModelCardMetadata,
    RegistryType,
)


def get_timestamp() -> int:
    return int(round(time.time() * 1_000_000))


class DataUris(BaseModel):
    data_uri: str
    datacard_uri: str
    profile_uri: Optional[str] = None
    profile_html_uri: Optional[str] = None


class ModelUris(BaseModel):
    trained_model_uri: str
    sample_data_uri: str
    modelcard_uri: str
    model_metadata_uri: str
    onnx_model_uri: Optional[str] = None
    preprocessor_uri: Optional[str] = None


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
    uris: DataUris

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
    uris: ModelUris

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


class LoadRecord(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow")

    version: str
    name: str
    team: str
    uid: str
    user_email: str
    tags: Dict[str, str]

    @staticmethod
    def validate_table(registry_type: RegistryType) -> bool:
        raise NotImplementedError


class LoadedDataRecord(LoadRecord):
    dependent_vars: Optional[List[Union[int, str]]] = None
    metadata: DataCardMetadata
    uris: DataUris

    @model_validator(mode="before")
    @classmethod
    def load_attributes(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        uris = values["uris"]

        datacard_definition = cls.load_datacard_definition(values)

        if datacard_definition.get("metadata") is None:  # this is None for previous v1 cards
            datacard_definition["metadata"] = cls.convert_data_metadata(datacard_definition)
        datacard_definition["metadata"]["auditcard_uid"] = values.get("auditcard_uid")
        datacard_definition["uris"] = uris
        return datacard_definition

    @classmethod
    def convert_data_metadata(cls, card_def: Dict[str, Any]) -> Dict[str, Any]:
        """This classmethod is used for backward compatibility"""
        return DataCardMetadata(**card_def).model_dump()

    @classmethod
    def load_datacard_definition(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Loads a model card definition from current attributes

        Returns:
            Dictionary to be parsed by DataCard.model_validate()
        """
        ...
        # datacard_definition = load_artifact_from_storage(
        #    artifact_type=AllowedDataType.DICT,
        #    storage_request=StorageRequest(
        #        registry_type=RegistryType.DATA,
        #        card_uid=values["uid"],
        #        uri_name=UriNames.DATACARD_URI.value,
        #        uri_path=values["uris"][UriNames.DATACARD_URI.value],
        #    ),
        # )
        # return cast(Dict[str, Any], datacard_definition)

    @staticmethod
    def validate_table(registry_type: RegistryType) -> bool:
        return registry_type == RegistryType.DATA


class LoadedModelRecord(LoadRecord):
    datacard_uid: str
    metadata: ModelCardMetadata
    uris: ModelUris

    model_config = ConfigDict(protected_namespaces=("protect_",))

    @model_validator(mode="before")
    @classmethod
    def load_model_attr(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        # storage_client = cast(StorageClient, values["storage_client"])
        # modelcard_definition = cls.load_modelcard_definition(
        #    values=values,
        #    storage_client=storage_client,
        # )
        # if modelcard_definition.get("metadata") is None:
        #    modelcard_definition["metadata"] = cls.convert_model_metadata(modelcard_definition)
        #
        # modelcard_definition["metadata"]["auditcard_uid"] = values.get("auditcard_uid")
        # modelcard_definition["metadata"]["sample_data_type"] = values.get("sample_data_type")
        # modelcard_definition["metadata"]["model_type"] = values.get("model_type", "undefined")
        #
        # return modelcard_definition
        ...

    @classmethod
    def load_modelcard_definition(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Loads a model card definition from current attributes

        Returns:
            Dictionary to be parsed by ModelCard.parse_obj()
        """
        ...
        # model_card_definition = load_artifact_from_storage(
        #    artifact_type=AllowedDataType.DICT,
        #    storage_request=StorageRequest(
        #        registry_type=RegistryType.MODEL,
        #        card_uid=values["uid"],
        #        uri_name=UriNames.MODELCARD_URI,
        #        uri_path=values["uris"][UriNames.MODELCARD_URI.value],
        #    ),
        # )

    #
    # return cast(Dict[str, Any], model_card_definition)

    @classmethod
    def convert_model_metadata(cls, card_def: Dict[str, Any]) -> Dict[str, Any]:
        """This classmethod is used for backward compatibility"""
        return ModelCardMetadata(**card_def).model_dump()

    @staticmethod
    def validate_table(registry_type: RegistryType) -> bool:
        return registry_type == RegistryType.MODEL


class LoadedAuditRecord(LoadRecord):
    approved: bool
    audit: Dict[str, Dict[int, Dict[str, Optional[str]]]]
    comments: List[Comment]
    metadata: AuditCardMetadata

    @model_validator(mode="before")
    @classmethod
    def load_audit_attr(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        ...
        # audit_definition: Dict[str, Any] = load_artifact_from_storage(
        #    artifact_type=AllowedDataType.DICT,
        #    storage_request=StorageRequest(
        #        registry_type=RegistryType.AUDIT,
        #        card_uid=values["uid"],
        #        uri_name=UriNames.AUDIT_URI,
        #        uri_path=values["uris"][UriNames.AUDIT_URI.value],
        #    ),
        # )

    #
    # return audit_definition

    @staticmethod
    def validate_table(registry_type: RegistryType) -> bool:
        return registry_type == RegistryType.AUDIT


class LoadedRunRecord(LoadRecord):
    datacard_uids: Optional[List[str]] = None
    modelcard_uids: Optional[List[str]] = None
    pipelinecard_uid: Optional[str] = None
    artifact_uris: Dict[str, str]
    artifacts: Dict[str, Any] = {}
    metrics: METRICS
    project_id: Optional[str] = None
    parameters: PARAMS
    tags: Dict[str, str]
    runcard_uri: str

    @model_validator(mode="before")
    @classmethod
    def load_run_attr(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        ...
        # runcard_definition: Dict[str, Any] = load_artifact_from_storage(
        #    artifact_type=AllowedDataType.DICT,
        #    storage_request=StorageRequest(
        #        registry_type=RegistryType.RUN,
        #        card_uid=values["uid"],
        #        uri_name=UriNames.RUNCARD_URI,
        #        uri_path=values["uris"][UriNames.RUNCARD_URI.value],
        #    ),
        # )

    #
    # return runcard_definition

    @staticmethod
    def validate_table(registry_type: RegistryType) -> bool:
        return registry_type == RegistryType.RUN


# same as piplelineregistry (duplicating to stay with theme of separate records)
class LoadedPipelineRecord(LoadRecord):
    pipeline_code_uri: Optional[str] = None
    datacard_uids: Optional[List[str]] = None
    modelcard_uids: Optional[List[str]] = None
    runcard_uids: Optional[List[str]] = None

    @staticmethod
    def validate_table(registry_type: RegistryType) -> bool:
        return registry_type == RegistryType.PIPELINE


LoadedRecordType = Union[
    LoadedPipelineRecord,
    LoadedDataRecord,
    LoadedRunRecord,
    LoadedModelRecord,
    LoadedAuditRecord,
]


def load_record(registry_type: RegistryType, record_data: Dict[str, Any]) -> LoadedRecordType:
    record = next(
        record
        for record in LoadRecord.__subclasses__()
        if record.validate_table(
            registry_type=registry_type,
        )
    )

    loaded_record = record(**record_data)
    return cast(LoadedRecordType, loaded_record)
