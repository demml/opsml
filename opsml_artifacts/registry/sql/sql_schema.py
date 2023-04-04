import datetime
import os
import uuid
from enum import Enum
from typing import Type, Union, cast

from sqlalchemy import BigInteger, Column, String
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declarative_mixin, validates  # type: ignore

from opsml_artifacts.helpers.logging import ArtifactLogger

logger = ArtifactLogger.get_logger(__name__)

Base = declarative_base()
YEAR_MONTH_DATE = "%Y-%m-%d"


class RegistryTableNames(str, Enum):
    DATA = os.getenv("ML_DATA_REGISTRY_NAME", "OPSML_DATA_REGISTRY")
    MODEL = os.getenv("ML_MODEL_REGISTRY_NAME", "OPSML_MODEL_REGISTRY")
    EXPERIMENT = os.getenv("ML_EXPERIMENT_REGISTRY_NAME", "OPSML_EXPERIMENT_REGISTRY")
    PIPELINE = os.getenv("ML_PIPELINE_REGISTRY_NAME", "OPSML_PIPELINE_REGISTRY")


@declarative_mixin
class BaseMixin:
    uid = Column("uid", String(512), primary_key=True, default=lambda: uuid.uuid4().hex)
    date = Column("date", String(512), default=datetime.date.today().strftime(YEAR_MONTH_DATE))
    timestamp = Column("timestamp", BigInteger)
    app_env = Column("app_env", String(512), default=os.getenv("APP_ENV", "development"))
    name = Column("name", String(512))
    team = Column("team", String(512))
    version = Column("version", String(512), nullable=False)
    user_email = Column("user_email", String(512))

    @validates("team")
    def lower_team(self, key, team):
        return team.lower().replace("_", "-")

    @validates("name")
    def lower_name(self, key, name):
        return name.lower().replace("_", "-")


@declarative_mixin
class DataMixin:
    data_uri = Column("data_uri", String(2048))
    drift_uri = Column("drift_uri", String(2048))
    feature_map = Column("feature_map", JSON)
    feature_descriptions = Column("feature_descriptions", JSON)
    data_splits = Column("data_splits", JSON)
    data_type = Column("data_type", String(512))
    additional_info = Column("additional_info", JSON)
    dependent_vars = Column("dependent_vars", JSON)


class DataSchema(Base, BaseMixin, DataMixin):  # type: ignore
    __tablename__ = RegistryTableNames.DATA.value

    def __repr__(self):
        return f"<SqlMetric({self.__tablename__}"


@declarative_mixin
class ModelMixin:
    model_card_uri = Column("model_card_uri", String(2048))
    data_card_uid = Column("data_card_uid", String(2048))
    trained_model_uri = Column("trained_model_uri", String(2048))
    sample_data_uri = Column("sample_data_uri", String(2048))
    sample_data_type = Column("sample_data_type", String(512))
    model_type = Column("model_type", String(512))


class ModelSchema(Base, BaseMixin, ModelMixin):  # type: ignore
    __tablename__ = RegistryTableNames.MODEL.value

    def __repr__(self):
        return f"<SqlMetric({self.__tablename__}"


@declarative_mixin
class ExperimentMixin:
    data_card_uids = Column("data_card_uids", JSON)
    model_card_uids = Column("model_card_uids", JSON)
    pipeline_card_uid = Column("pipeline_card_uid", String(512))
    artifact_uris = Column("artifact_uris", JSON)
    metrics = Column("metrics", JSON)


class ExperimentSchema(Base, BaseMixin, ExperimentMixin):  # type: ignore
    __tablename__ = RegistryTableNames.EXPERIMENT.value

    def __repr__(self):
        return f"<SqlMetric({self.__tablename__}"


@declarative_mixin
class PipelineMixin:
    pipeline_code_uri = Column("pipeline_code_uri", String(512))
    data_card_uids = Column("data_card_uids", JSON)
    model_card_uids = Column("model_card_uids", JSON)
    experiment_card_uids = Column("experiment_card_uids", JSON)


class PipelineSchema(Base, BaseMixin, PipelineMixin):  # type: ignore
    __tablename__ = RegistryTableNames.PIPELINE.value

    def __repr__(self):
        return f"<SqlMetric({self.__tablename__}"


REGISTRY_TABLES = Union[  # pylint: disable=invalid-name
    DataSchema,
    ModelSchema,
    ExperimentSchema,
    PipelineSchema,
]


class TableSchema:
    @staticmethod
    def get_table(table_name: str) -> Type[REGISTRY_TABLES]:  # type: ignore
        for table_schema in Base.__subclasses__():
            if table_name == table_schema.__tablename__:  # type: ignore
                return cast(Type[REGISTRY_TABLES], table_schema)

        raise ValueError(f"""Incorrect table name provided {table_name}""")
