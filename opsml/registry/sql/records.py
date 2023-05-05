import time
from typing import Any, Dict, List, Optional, Union, cast

from pydantic import BaseModel, Extra, root_validator

from opsml.registry.cards.types import METRICS, PARAMS
from opsml.registry.sql.sql_schema import RegistryTableNames
from opsml.registry.storage.artifact_storage import load_record_artifact_from_storage
from opsml.registry.storage.storage_system import StorageClientType
from opsml.registry.storage.types import ArtifactStorageSpecs

ARBITRARY_ARTIFACT_TYPE = "dict"


class DataRegistryRecord(BaseModel):
    data_uri: str
    version: str
    data_type: str
    name: str
    team: str
    user_email: str
    uid: Optional[str]
    timestamp: int = int(round(time.time() * 1_000_000))
    runcard_uid: Optional[str]
    pipelinecard_uid: Optional[str]
    datacard_uri: str

    class Config:
        smart_union = True


class ModelRegistryRecord(BaseModel):
    uid: str
    version: str
    team: str
    user_email: str
    name: str
    modelcard_uri: str
    datacard_uid: str
    trained_model_uri: str
    onnx_model_uri: Optional[str] = None
    sample_data_uri: str
    sample_data_type: str
    model_type: str
    timestamp: int = int(round(time.time() * 1_000_000))
    runcard_uid: Optional[str]
    pipelinecard_uid: Optional[str]


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
    tags: Dict[str, str]
    timestamp: int = int(round(time.time() * 1_000_000))
    runcard_uri: str


class PipelineRegistryRecord(BaseModel):
    name: str
    team: str
    user_email: str
    uid: Optional[str]
    version: Optional[str]
    pipeline_code_uri: Optional[str]
    datacard_uids: List[str]
    modelcard_uids: List[str]
    runcard_uids: List[str]
    timestamp: int = int(round(time.time() * 1_000_000))


class ProjectRegistryRecord(BaseModel):
    uid: str
    name: str
    team: str
    project_id: str
    version: Optional[str]
    description: Optional[str]
    timestamp: int = int(round(time.time() * 1_000_000))


RegistryRecord = Union[
    DataRegistryRecord,
    ModelRegistryRecord,
    RunRegistryRecord,
    PipelineRegistryRecord,
    ProjectRegistryRecord,
]


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
    data_splits: Optional[List[Dict[str, Any]]]
    data_type: str
    feature_map: Dict[str, str]
    feature_descriptions: Optional[Dict[str, str]]
    dependent_vars: Optional[List[Union[int, str]]]
    additional_info: Optional[Dict[str, Union[float, int, str]]]
    runcard_uid: Optional[str]
    pipelinecard_uid: Optional[str]
    datacard_uri: str

    @root_validator(pre=True)
    def load_attributes(cls, values):  # pylint: disable=no-self-argument
        storage_client = cast(StorageClientType, values["storage_client"])

        datacard_definition = cls.load_datacard_definition(
            save_path=values["datacard_uri"],
            storage_client=storage_client,
        )
        # values["data_splits"] = LoadedDataRecord.get_splits(splits=values["data_splits"])
        datacard_definition["datacard_uri"] = values.get("datacard_uri")
        datacard_definition["storage_client"] = values.get("storage_client")

        return datacard_definition

    @staticmethod
    def get_splits(splits):
        if bool(splits):
            return splits.get("splits")
        return None

    @staticmethod
    def load_drift_report(values):
        storage_client = cast(StorageClientType, values["storage_client"])

        if bool(values.get("drift_uri")):
            storage_spec = ArtifactStorageSpecs(save_path=values["drift_uri"])

            storage_client.storage_spec = storage_spec
            return load_record_artifact_from_storage(
                storage_client=storage_client,
                artifact_type=ARBITRARY_ARTIFACT_TYPE,
            )

        return None

    @classmethod
    def load_datacard_definition(
        cls,
        save_path: str,
        storage_client: StorageClientType,
    ) -> Dict[str, Any]:
        """Loads a model card definition from current attributes

        Returns:
            Dictionary to be parsed by DataCard.parse_obj()
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
        return table_name == RegistryTableNames.DATA


class LoadedModelRecord(LoadRecord):
    modelcard_uri: str
    datacard_uid: str
    trained_model_uri: str
    onnx_model_uri: Optional[str] = None
    sample_data_uri: str
    sample_data_type: str
    model_type: str
    runcard_uid: Optional[str]
    pipelinecard_uid: Optional[str]

    @root_validator(pre=True)
    def load_model_attr(cls, values) -> Dict[str, Any]:  # pylint: disable=no-self-argument
        storage_client = cast(StorageClientType, values["storage_client"])
        modelcard_definition = cls.load_modelcard_definition(
            values=values,
            storage_client=storage_client,
        )

        modelcard_definition["modelcard_uri"] = values.get("modelcard_uri")
        modelcard_definition["trained_model_uri"] = values.get("trained_model_uri")
        modelcard_definition["onnx_model_uri"] = values.get("onnx_model_uri")
        modelcard_definition["sample_data_uri"] = values.get("sample_data_uri")
        modelcard_definition["sample_data_type"] = values.get("sample_data_type")
        modelcard_definition["model_type"] = values.get("model_type")
        modelcard_definition["storage_client"] = values.get("storage_client")

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
        return table_name == RegistryTableNames.MODEL


class LoadedRunRecord(LoadRecord):
    datacard_uids: Optional[List[str]]
    modelcard_uids: Optional[List[str]]
    pipelinecard_uid: Optional[str]
    artifact_uris: Dict[str, str]
    artifacts: Dict[str, Any] = {}
    metrics: METRICS
    project_id: Optional[str]
    params: PARAMS
    tags: Dict[str, str]
    runcard_uri: str

    @root_validator(pre=True)
    def load_run_attr(cls, values) -> Dict[str, Any]:  # pylint: disable=no-self-argument
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
            Dictionary to be parsed by RunCard.parse_obj()
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
        return table_name == RegistryTableNames.RUN


# same as piplelineregistry (duplicating to stay with theme of separate records)
class LoadedPipelineRecord(LoadRecord):
    pipeline_code_uri: Optional[str]
    datacard_uids: Optional[List[str]]
    modelcard_uids: Optional[List[str]]
    runcard_uids: Optional[List[str]]

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
