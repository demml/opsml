import time
from typing import Any, Dict, List, Optional, Union, cast

from pydantic import BaseModel, Extra, root_validator, validator

from opsml_artifacts.drift.types import DriftReport
from opsml_artifacts.registry.sql.sql_schema import RegistryTableNames
from opsml_artifacts.registry.storage.artifact_storage import (
    load_record_artifact_from_storage,
)
from opsml_artifacts.registry.storage.storage_system import StorageClientType
from opsml_artifacts.registry.storage.types import ArtifactStorageSpecs


class DataRegistryRecord(BaseModel):
    data_uri: str
    drift_uri: Optional[str]
    data_splits: Optional[Dict[str, List[Dict[str, Any]]]]
    version: str
    data_type: str
    name: str
    team: str
    feature_map: Dict[str, str]
    feature_descriptions: Optional[Dict[str, str]]
    user_email: str
    uid: Optional[str]
    additional_info: Optional[Dict[str, Union[float, int, str]]]
    dependent_vars: Optional[List[Union[int, str]]]
    timestamp: int = int(round(time.time() * 1_000_000))

    class Config:
        smart_union = True

    @validator("data_splits", pre=True)
    def convert_to_dict(cls, splits):  # pylint: disable=no-self-argument
        if bool(splits):
            return {"splits": splits}
        return None


class ModelRegistryRecord(BaseModel):
    uid: str
    version: str
    team: str
    user_email: str
    name: str
    model_card_uri: str
    datacard_uid: str
    trained_model_uri: str
    sample_data_uri: str
    sample_data_type: str
    model_type: str
    timestamp: int = int(round(time.time() * 1_000_000))


class RunRegistryRecord(BaseModel):
    name: str
    team: str
    user_email: str
    uid: Optional[str]
    version: Optional[str]
    datacard_uids: Optional[List[str]]
    modelcard_uids: Optional[List[str]]
    pipelinecard_uid: Optional[str]
    project_id: Optional[str]
    artifact_uris: Optional[Dict[str, str]]
    metrics: Optional[Dict[str, Union[float, int]]]
    params: Dict[str, Union[float, int, str]]
    tags: Dict[str, str]
    timestamp: int = int(round(time.time() * 1_000_000))


class PipelineRegistryRecord(BaseModel):
    name: str
    team: str
    user_email: str
    uid: Optional[str]
    version: Optional[str]
    pipeline_code_uri: Optional[str]
    datacard_uids: Optional[Dict[str, str]]
    modelcard_uids: Optional[Dict[str, str]]
    runcard_uids: Optional[Dict[str, str]]
    timestamp: int = int(round(time.time() * 1_000_000))


RegistryRecord = Union[DataRegistryRecord, ModelRegistryRecord, RunRegistryRecord, PipelineRegistryRecord]


class LoadRecord(BaseModel):
    version: str
    name: str
    team: str
    uid: str
    user_email: str
    storage_client: Optional[StorageClientType]

    class Config:
        arbitrary_types_allowed = True
        smart_union = True
        extra = Extra.allow

    @staticmethod
    def validate_table(table_name: str) -> bool:
        raise NotImplementedError


class LoadedDataRecord(LoadRecord):
    data_uri: str
    drift_uri: Optional[str]
    data_splits: Optional[List[Dict[str, Any]]]
    data_type: str
    feature_map: Dict[str, str]
    feature_descriptions: Optional[Dict[str, str]]
    dependent_vars: Optional[List[Union[int, str]]]
    drift_report: Optional[Dict[str, DriftReport]]
    additional_info: Optional[Dict[str, Union[float, int, str]]]

    @root_validator(pre=True)
    def load_attributes(cls, values):  # pylint: disable=no-self-argument
        values["data_splits"] = LoadedDataRecord.get_splits(splits=values["data_splits"])
        values["drift_report"] = LoadedDataRecord.load_drift_report(values=values)

        return values

    @staticmethod
    def get_splits(splits):
        if bool(splits):
            return splits.get("splits")
        return None

    @staticmethod
    def load_drift_report(values):
        storage_client = cast(StorageClientType, values["storage_client"])

        if bool(values.get("drift_uri")):
            storage_spec = ArtifactStorageSpecs(
                save_path=values["drift_uri"],
                name=values["name"],
                team=values["team"],
                version=values["version"],
            )

            storage_client.storage_spec = storage_spec
            return load_record_artifact_from_storage(
                storage_client=storage_client,
                artifact_type="dict",
            )

        return None

    @staticmethod
    def validate_table(table_name: str) -> bool:
        return table_name == RegistryTableNames.DATA


class LoadedModelRecord(LoadRecord):
    model_card_uri: str
    datacard_uid: str
    trained_model_uri: str
    sample_data_uri: str
    sample_data_type: str
    model_type: str

    @root_validator(pre=True)
    def load_model_attr(cls, values) -> Dict[str, Any]:  # pylint: disable=no-self-argument

        storage_client = cast(StorageClientType, values["storage_client"])
        modelcard_definition = cls.load_model_card_definition(
            values=values,
            storage_client=storage_client,
        )

        modelcard_definition["model_card_uri"] = values.get("model_card_uri")
        modelcard_definition["trained_model_uri"] = values.get("trained_model_uri")
        modelcard_definition["sample_data_uri"] = values.get("sample_data_uri")
        modelcard_definition["sample_data_type"] = values.get("sample_data_type")
        modelcard_definition["storage_client"] = values.get("storage_client")

        return modelcard_definition

    @classmethod
    def load_model_card_definition(
        cls,
        values: Dict[str, Any],
        storage_client: StorageClientType,
    ) -> Dict[str, Any]:

        """Loads a model card definition from current attributes

        Returns:
            Dictionary to be parsed by ModelCard.parse_obj()
        """

        storage_spec = ArtifactStorageSpecs(
            save_path=values["model_card_uri"],
            name=values["name"],
            version=values["version"],
            team=values["team"],
        )

        storage_client.storage_spec = storage_spec
        model_card_definition = load_record_artifact_from_storage(
            storage_client=storage_client,
            artifact_type="dict",
        )

        return model_card_definition

    @staticmethod
    def validate_table(table_name: str) -> bool:
        return table_name == RegistryTableNames.MODEL


class LoadedRunRecord(LoadRecord):
    datacard_uids: Optional[List[str]]
    modelcard_uids: Optional[List[str]]
    pipelinecard_uid: Optional[str]
    artifact_uris: Dict[str, str]
    artifacts: Optional[Dict[str, Any]]
    metrics: Optional[Dict[str, Union[int, float]]]
    project_id: Optional[str]
    params: Dict[str, Union[float, int, str]]
    tags: Dict[str, str]

    @root_validator(pre=True)
    def load_exp_attr(cls, values) -> Dict[str, Any]:  # pylint: disable=no-self-argument

        storage_client = cast(StorageClientType, values["storage_client"])
        cls.load_artifacts(values=values, storage_client=storage_client)
        return values

    @classmethod
    def load_artifacts(
        cls,
        values: Dict[str, Any],
        storage_client: StorageClientType,
    ) -> None:
        """Loads run artifacts to pydantic model"""

        loaded_artifacts: Dict[str, Any] = {}
        artifact_uris = values.get("artifact_uris", loaded_artifacts)

        if not bool(artifact_uris):
            values["artifacts"] = loaded_artifacts

        for name, uri in artifact_uris.items():
            storage_spec = ArtifactStorageSpecs(
                save_path=uri,
                name=values["name"],
                team=values["team"],
                version=values["version"],
                storage_client=storage_client,
            )

            storage_client.storage_spec = storage_spec
            loaded_artifacts[name] = load_record_artifact_from_storage(
                storage_client=storage_client,
                artifact_type="artifact",
            )

    @staticmethod
    def validate_table(table_name: str) -> bool:
        return table_name == RegistryTableNames.RUN


# same as piplelineregistry (duplicating to stay with theme of separate records)
class LoadedPipelineRecord(LoadRecord):
    pipeline_code_uri: Optional[str]
    datacard_uids: Optional[Dict[str, str]]
    modelcard_uids: Optional[Dict[str, str]]
    runcard_uids: Optional[Dict[str, str]]

    @staticmethod
    def validate_table(table_name: str) -> bool:
        return table_name == RegistryTableNames.PIPELINE


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
