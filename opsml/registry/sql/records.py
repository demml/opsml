# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
import time
from typing import Any, Dict, List, Optional, Union, cast

from pydantic import BaseModel, model_validator, ConfigDict

from opsml.profile.profile_data import DataProfiler, ProfileReport
from opsml.registry.cards.types import METRICS, PARAMS, DataCardUris, ModelCardUris
from opsml.registry.sql.sql_schema import RegistryTableNames
from opsml.registry.storage.artifact_storage import load_record_artifact_from_storage
from opsml.registry.storage.storage_system import StorageClientType
from opsml.registry.storage.types import ArtifactStorageSpecs

ARBITRARY_ARTIFACT_TYPE = "dict"


def get_timestamp():
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
    datacard_uri: str

    @model_validator(mode="before")
    def set_uris(cls, values):
        uris = values.get("uris")
        values["data_uri"] = uris["data_uri"]
        values["datacard_uri"] = uris["datacard_uri"]

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

    model_config = ConfigDict(protected_namespaces=("protect_",))

    @model_validator(mode="before")
    def set_uris(cls, values):
        uris = values.get("uris")
        values["trained_model_uri"] = uris["trained_model_uri"]
        values["model_metadata_uri"] = uris["model_metadata_uri"]
        values["sample_data_uri"] = uris["sample_data_uri"]
        values["modelcard_uri"] = uris["modelcard_uri"]

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


RegistryRecord = Union[
    DataRegistryRecord,
    ModelRegistryRecord,
    RunRegistryRecord,
    PipelineRegistryRecord,
    ProjectRegistryRecord,
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
    def validate_table(table_name: str) -> bool:
        raise NotImplementedError


class LoadedDataRecord(LoadRecord):
    uris: DataCardUris
    data_type: Optional[str] = None
    feature_map: Optional[Dict[str, Any]] = None
    feature_descriptions: Optional[Dict[str, str]] = None
    dependent_vars: Optional[List[Union[int, str]]] = None
    additional_info: Optional[Dict[str, Union[float, int, str]]] = None
    runcard_uid: Optional[str] = None
    pipelinecard_uid: Optional[str] = None

    @model_validator(mode="before")
    def load_attributes(cls, values):
        storage_client = cast(StorageClientType, values["storage_client"])

        datacard_definition = cls.load_datacard_definition(
            save_path=values["datacard_uri"],
            storage_client=storage_client,
        )

        datacard_definition["storage_client"] = storage_client
        datacard_definition["uris"]["datacard_uri"] = values.get("datacard_uri")

        if datacard_definition["uris"]["profile_uri"] is not None:
            profile_uri = datacard_definition["uris"]["profile_uri"]

            datacard_definition["data_profile"] = LoadedDataRecord.load_data_profile(
                data_profile_uri=profile_uri,
                storage_client=storage_client,
            )

        return datacard_definition

    @staticmethod
    def load_data_profile(data_profile_uri: str, storage_client: StorageClientType) -> ProfileReport:
        storage_spec = ArtifactStorageSpecs(save_path=data_profile_uri)

        storage_client.storage_spec = storage_spec
        profile_bytes = load_record_artifact_from_storage(
            storage_client=storage_client,
            artifact_type=ARBITRARY_ARTIFACT_TYPE,
        )

        profile = DataProfiler.load_profile(data=profile_bytes)
        return profile

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

        storage_spec = ArtifactStorageSpecs(save_path=save_path)
        storage_client.storage_spec = storage_spec

        datacard_definition = load_record_artifact_from_storage(
            storage_client=storage_client,
            artifact_type=ARBITRARY_ARTIFACT_TYPE,
        )

        return datacard_definition

    @staticmethod
    def validate_table(table_name: str) -> bool:
        return table_name == RegistryTableNames.DATA.value


class LoadedModelRecord(LoadRecord):
    datacard_uid: str
    sample_data_type: str
    model_type: str
    runcard_uid: Optional[str] = None
    pipelinecard_uid: Optional[str] = None
    uris: ModelCardUris

    model_config = ConfigDict(protected_namespaces=("protect_",))

    @model_validator(mode="before")
    def load_model_attr(cls, values) -> Dict[str, Any]:
        storage_client = cast(StorageClientType, values["storage_client"])
        modelcard_definition = cls.load_modelcard_definition(
            values=values,
            storage_client=storage_client,
        )

        modelcard_definition["sample_data_type"] = values.get("sample_data_type")
        modelcard_definition["model_type"] = values.get("model_type")
        modelcard_definition["storage_client"] = values.get("storage_client")
        modelcard_definition["uris"] = ModelCardUris(
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

        storage_spec = ArtifactStorageSpecs(save_path=values["modelcard_uri"])

        storage_client.storage_spec = storage_spec
        model_card_definition = load_record_artifact_from_storage(
            storage_client=storage_client,
            artifact_type=ARBITRARY_ARTIFACT_TYPE,
        )

        return model_card_definition

    @staticmethod
    def validate_table(table_name: str) -> bool:
        return table_name == RegistryTableNames.MODEL.value


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
    def load_run_attr(cls, values) -> Dict[str, Any]:
        storage_client = cast(StorageClientType, values["storage_client"])

        runcard_definition = cls.load_runcard_definition(
            runcard_uri=values.get("runcard_uri"),
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

        storage_spec = ArtifactStorageSpecs(save_path=runcard_uri)

        storage_client.storage_spec = storage_spec
        runcard_definition = load_record_artifact_from_storage(
            storage_client=storage_client,
            artifact_type=ARBITRARY_ARTIFACT_TYPE,
        )

        return runcard_definition

    @staticmethod
    def validate_table(table_name: str) -> bool:
        return table_name == RegistryTableNames.RUN.value


# same as piplelineregistry (duplicating to stay with theme of separate records)
class LoadedPipelineRecord(LoadRecord):
    pipeline_code_uri: Optional[str] = None
    datacard_uids: Optional[List[str]] = None
    modelcard_uids: Optional[List[str]] = None
    runcard_uids: Optional[List[str]] = None

    @staticmethod
    def validate_table(table_name: str) -> bool:
        return table_name == RegistryTableNames.PIPELINE.value


LoadedRecordType = Union[
    LoadedPipelineRecord,
    LoadedDataRecord,
    LoadedRunRecord,
    LoadedModelRecord,
]


def load_record(
    table_name: str,
    record_data: Dict[str, Any],
    storage_client: StorageClientType,
) -> LoadedRecordType:
    record = next(
        record
        for record in LoadRecord.__subclasses__()
        if record.validate_table(
            table_name=table_name,
        )
    )

    loaded_record = record(
        **{
            **record_data,
            **{"storage_client": storage_client},
        }
    )

    return cast(LoadedRecordType, loaded_record)
