from typing import Any, Dict, List, Optional, Union, cast

from pydantic import BaseModel, Extra, root_validator, validator

from opsml_artifacts.drift.models import DriftReport
from opsml_artifacts.registry.cards.artifact_storage import (
    load_record_artifact_from_storage,
)
from opsml_artifacts.registry.cards.storage_system import StorageClientProto
from opsml_artifacts.registry.sql.models import SaveInfo
from opsml_artifacts.registry.sql.sql_schema import RegistryTableNames


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
    data_card_uid: str
    trained_model_uri: str
    sample_data_uri: str
    sample_data_type: str
    model_type: str


class ExperimentRegistryRecord(BaseModel):
    name: str
    team: str
    user_email: str
    uid: Optional[str]
    version: Optional[str]
    data_card_uids: Optional[List[str]]
    model_card_uids: Optional[List[str]]
    pipeline_card_uid: Optional[str]
    artifact_uris: Optional[Dict[str, str]]
    metrics: Optional[Dict[str, Union[float, int]]]


class PipelineRegistryRecord(BaseModel):
    name: str
    team: str
    user_email: str
    uid: Optional[str]
    version: Optional[str]
    pipeline_code_uri: Optional[str]
    data_card_uids: Optional[Dict[str, str]]
    model_card_uids: Optional[Dict[str, str]]
    experiment_card_uids: Optional[Dict[str, str]]


class LoadRecord(BaseModel):
    version: str
    name: str
    team: str
    uid: str
    user_email: str

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
    storage_client: Optional[StorageClientProto]

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

        if bool(values.get("drift_uri")):
            save_info = SaveInfo(
                blob_path=values["drift_uri"],
                name=values["name"],
                team=values["team"],
                version=values["version"],
                storage_client=values["storage_client"],
            )

            return load_record_artifact_from_storage(
                save_info=save_info,
                artifact_type="dict",
            )
        return None

    @staticmethod
    def validate_table(table_name: str) -> bool:
        return table_name == RegistryTableNames.DATA


class LoadedModelRecord(LoadRecord):
    model_card_uri: str
    data_card_uid: str
    trained_model_uri: str
    sample_data_uri: str
    sample_data_type: str
    model_type: str
    storage_client: Optional[StorageClientProto]

    @root_validator(pre=True)
    def load_model_attr(cls, values) -> Dict[str, Any]:  # pylint: disable=no-self-argument

        storage_client = cast(StorageClientProto, values["storage_client"])
        modelcard_definition = cls.load_model_card_definition(
            values=values,
            storage_client=storage_client,
        )

        return {**values, **modelcard_definition}

    @classmethod
    def load_model_card_definition(
        cls,
        values: Dict[str, Any],
        storage_client: StorageClientProto,
    ) -> Dict[str, Any]:

        """Loads a model card definition from current attributes

        Returns:
            Dictionary to be parsed by ModelCard.parse_obj()
        """

        save_info = SaveInfo(
            blob_path=values["model_card_uri"],
            name=values["name"],
            version=values["version"],
            team=values["team"],
            storage_client=storage_client,
        )

        model_card_definition = load_record_artifact_from_storage(
            save_info=save_info,
            artifact_type="dict",
        )

        return model_card_definition

    @staticmethod
    def validate_table(table_name: str) -> bool:
        return table_name == RegistryTableNames.MODEL


class LoadedExperimentRecord(LoadRecord):
    data_card_uids: Optional[List[str]]
    model_card_uids: Optional[List[str]]
    pipeline_card_uid: Optional[str]
    artifact_uris: Dict[str, str]
    artifacts: Optional[Dict[str, Any]]
    metrics: Optional[Dict[str, Union[int, float]]]
    storage_client: Optional[StorageClientProto]

    @root_validator(pre=True)
    def load_exp_attr(cls, values) -> Dict[str, Any]:  # pylint: disable=no-self-argument

        storage_client = cast(StorageClientProto, values["storage_client"])
        cls.load_artifacts(values=values, storage_client=storage_client)

        return values

    @classmethod
    def load_artifacts(
        cls,
        values: Dict[str, Any],
        storage_client: StorageClientProto,
    ) -> None:
        """Loads experiment artifacts to pydantic model"""

        loaded_artifacts: Dict[str, Any] = {}
        artifact_uris = values.get("artifact_uris", loaded_artifacts)

        if not bool(artifact_uris):
            values["artifacts"] = loaded_artifacts

        for name, uri in artifact_uris.items():
            save_info = SaveInfo(
                blob_path=uri,
                name=values["name"],
                team=values["team"],
                version=values["version"],
                storage_client=storage_client,
            )
            loaded_artifacts[name] = load_record_artifact_from_storage(
                save_info=save_info,
                artifact_type="artifact",
            )

    @staticmethod
    def validate_table(table_name: str) -> bool:
        return table_name == RegistryTableNames.EXPERIMENT


# same as piplelineregistry (duplicating to stay with theme of separate records)
class LoadedPipelineRecord(LoadRecord):
    pipeline_code_uri: Optional[str]
    data_card_uids: Optional[Dict[str, str]]
    model_card_uids: Optional[Dict[str, str]]
    experiment_card_uids: Optional[Dict[str, str]]

    @staticmethod
    def validate_table(table_name: str) -> bool:
        return table_name == RegistryTableNames.PIPELINE


LoadedRecordType = Union[
    LoadedPipelineRecord,
    LoadedDataRecord,
    LoadedExperimentRecord,
    LoadedModelRecord,
]


def load_record(
    table_name: str,
    record_data: Dict[str, Any],
    storage_client: StorageClientProto,
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
