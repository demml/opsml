# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
import time
from typing import Any, Dict, List, Optional, Union, cast

from pydantic import BaseModel, ConfigDict, model_validator

from opsml.registry.cards.types import (
    METRICS,
    PARAMS,
    AuditCardMetadata,
    CardVersion,
    Comment,
    DataCardMetadata,
    ModelCardMetadata,
    ModelCardUris,
    RegistryType,
)
from opsml.registry.storage.artifact import load_record_artifact_from_storage
from opsml.registry.storage.client import StorageClientType

ARBITRARY_ARTIFACT_TYPE = "dict"


def get_timestamp() -> int:
    return int(round(time.time() * 1_000_000))


class SaveRecord(BaseModel):
    name: str
    team: str
    user_email: str
    uid: Optional[str] = None
    version: str
    tags: Dict[str, str]


class DataRegistryRecord(SaveRecord):
    data_uri: Optional[str] = None
    data_type: Optional[str] = None
    timestamp: int = get_timestamp()
    runcard_uid: Optional[str] = None
    pipelinecard_uid: Optional[str] = None
    auditcard_uid: Optional[str] = None
    datacard_uri: str

    @model_validator(mode="before")
    @classmethod
    def set_metadata(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        metadata: Dict[str, Any] = values["metadata"]
        uris: Dict[str, Any] = metadata["uris"]

        values["data_uri"] = uris["data_uri"]
        values["datacard_uri"] = uris["datacard_uri"]
        values["data_type"] = metadata["data_type"]
        values["runcard_uid"] = metadata["runcard_uid"]
        values["pipelinecard_uid"] = metadata["pipelinecard_uid"]
        values["auditcard_uid"] = metadata["auditcard_uid"]

        return values


class ModelRegistryRecord(SaveRecord):
    modelcard_uri: str
    datacard_uid: str
    trained_model_uri: str
    model_metadata_uri: Optional[str] = None
    sample_data_uri: str
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

        values["modelcard_uri"] = metadata["uris"]["modelcard_uri"]
        values["trained_model_uri"] = metadata["uris"]["trained_model_uri"]
        values["model_metadata_uri"] = metadata["uris"]["model_metadata_uri"]
        values["sample_data_uri"] = metadata["uris"]["sample_data_uri"]
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
    storage_client: Optional[StorageClientType] = None

    @staticmethod
    def validate_table(registry_type: RegistryType) -> bool:
        raise NotImplementedError


class LoadedDataRecord(LoadRecord):
    dependent_vars: Optional[List[Union[int, str]]] = None
    metadata: DataCardMetadata

    @model_validator(mode="before")
    @classmethod
    def load_attributes(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        storage_client = cast(StorageClientType, values["storage_client"])

        datacard_definition = cls.load_datacard_definition(
            save_path=values["datacard_uri"],
            storage_client=storage_client,
        )

        datacard_definition["storage_client"] = storage_client

        if datacard_definition.get("metadata") is None:  # this is None for previous v1 cards
            datacard_definition["metadata"] = cls.convert_data_metadata(datacard_definition)

        datacard_definition["metadata"]["uris"]["datacard_uri"] = values.get("datacard_uri")
        datacard_definition["metadata"]["auditcard_uid"] = values.get("auditcard_uid")

        return datacard_definition

    @classmethod
    def convert_data_metadata(cls, card_def: Dict[str, Any]) -> Dict[str, Any]:
        """This classmethod is used for backward compatibility"""
        return DataCardMetadata(**card_def).model_dump()

    @classmethod
    def load_datacard_definition(
        cls,
        save_path: str,
        storage_client: StorageClientType,
    ) -> Dict[str, Any]:
        """Loads a model card definition from current attributes

        Returns:
            Dictionary to be parsed by DataCard.model_validate()
        """
        datacard_definition = load_record_artifact_from_storage(
            artifact_type=ARBITRARY_ARTIFACT_TYPE,
            storage_client=storage_client,
            uri=save_path,
        )
        assert datacard_definition is not None
        return cast(Dict[str, Any], datacard_definition)

    @staticmethod
    def validate_table(registry_type: RegistryType) -> bool:
        return registry_type == RegistryType.DATA


class LoadedModelRecord(LoadRecord):
    datacard_uid: str
    metadata: ModelCardMetadata

    model_config = ConfigDict(protected_namespaces=("protect_",))

    @model_validator(mode="before")
    @classmethod
    def load_model_attr(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        storage_client = cast(StorageClientType, values["storage_client"])
        modelcard_definition = cls.load_modelcard_definition(
            values=values,
            storage_client=storage_client,
        )
        if modelcard_definition.get("metadata") is None:
            modelcard_definition["metadata"] = cls.convert_model_metadata(modelcard_definition)

        modelcard_definition["metadata"]["auditcard_uid"] = values.get("auditcard_uid")
        modelcard_definition["metadata"]["sample_data_type"] = values.get("sample_data_type")
        modelcard_definition["metadata"]["model_type"] = values.get("model_type", "undefined")
        modelcard_definition["storage_client"] = values.get("storage_client")
        modelcard_definition["metadata"]["uris"] = ModelCardUris(
            model_metadata_uri=values.get("model_metadata_uri"),
            trained_model_uri=values.get("trained_model_uri"),
            modelcard_uri=values.get("modelcard_uri"),
            sample_data_uri=values.get("sample_data_uri"),
        )

        return modelcard_definition

    @classmethod
    def load_modelcard_definition(
        cls,
        values: Dict[str, Any],
        storage_client: StorageClientType,
    ) -> Dict[str, Any]:
        """Loads a model card definition from current attributes

        Returns:
            Dictionary to be parsed by ModelCard.parse_obj()
        """
        model_card_definition = load_record_artifact_from_storage(
            artifact_type=ARBITRARY_ARTIFACT_TYPE,
            storage_client=storage_client,
            uri=values["modelcard_uri"],
        )
        assert model_card_definition is not None
        return cast(Dict[str, Any], model_card_definition)

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
        storage_client = cast(StorageClientType, values["storage_client"])

        audit = cls._load_audit(
            audit_uri=values["audit_uri"],
            storage_client=storage_client,
        )
        audit["metadata"]["audit_uri"] = values["audit_uri"]

        return audit

    @classmethod
    def _load_audit(
        cls,
        audit_uri: str,
        storage_client: StorageClientType,
    ) -> Dict[str, Any]:
        """Loads a audit artifact from an audit uri

        Args:
            audit_uri:
                URI to audit artifact
            storage_client:
                Storage client to use for loading

        Returns:
            Audit dictionary
        """

        audit_definition = load_record_artifact_from_storage(
            artifact_type=ARBITRARY_ARTIFACT_TYPE,
            storage_client=storage_client,
            uri=audit_uri,
        )
        assert audit_definition is not None
        return cast(Dict[str, Any], audit_definition)

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
        storage_client = cast(StorageClientType, values["storage_client"])

        runcard_definition = cls.load_runcard_definition(
            runcard_uri=values["runcard_uri"],
            storage_client=storage_client,
        )

        runcard_definition["runcard_uri"] = values.get("runcard_uri")
        runcard_definition["storage_client"] = values.get("storage_client")

        return runcard_definition

    @classmethod
    def load_runcard_definition(
        cls,
        runcard_uri: str,
        storage_client: StorageClientType,
    ) -> Dict[str, Any]:
        """Loads a model card definition from current attributes

        Returns:
            Dictionary to be parsed by RunCard.model_validate()
        """

        runcard_definition = load_record_artifact_from_storage(
            artifact_type=ARBITRARY_ARTIFACT_TYPE,
            storage_client=storage_client,
            uri=runcard_uri,
        )
        assert runcard_definition is not None
        return cast(Dict[str, Any], runcard_definition)

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


def load_record(
    registry_type: RegistryType,
    record_data: Dict[str, Any],
    storage_client: StorageClientType,
) -> LoadedRecordType:
    record = next(
        record
        for record in LoadRecord.__subclasses__()
        if record.validate_table(
            registry_type=registry_type,
        )
    )

    loaded_record = record(
        **{
            **record_data,
            **{"storage_client": storage_client},
        }
    )

    return cast(LoadedRecordType, loaded_record)
