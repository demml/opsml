# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
import os
import uuid
from datetime import date
from enum import Enum
from typing import Type, Union, cast

from sqlalchemy import BigInteger, Column, String
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declarative_mixin, validates  # type: ignore

from opsml.helpers.logging import ArtifactLogger

logger = ArtifactLogger.get_logger()

Base = declarative_base()


class RegistryTableNames(str, Enum):
    DATA = os.getenv("ML_DATA_REGISTRY_NAME", "OPSML_DATA_REGISTRY")
    MODEL = os.getenv("ML_MODEL_REGISTRY_NAME", "OPSML_MODEL_REGISTRY")
    RUN = os.getenv("ML_RUN_REGISTRY_NAME", "OPSML_RUN_REGISTRY")
    PIPELINE = os.getenv("ML_PIPELINE_REGISTRY_NAME", "OPSML_PIPELINE_REGISTRY")
    PROJECT = os.getenv("ML_PROJECT_REGISTRY_NAME", "OPSML_PROJECT_REGISTRY")


@declarative_mixin
class BaseMixin:
    uid = Column("uid", String(64), primary_key=True, default=lambda: uuid.uuid4().hex)
    date = Column("date", String(32), default=lambda: str(date.today()))
    timestamp = Column("timestamp", BigInteger)
    app_env = Column("app_env", String(32), default=os.getenv("APP_ENV", "development"))
    name = Column("name", String(128))
    team = Column("team", String(128))
    version = Column("version", String(32), nullable=False)
    user_email = Column("user_email", String(128))
    tags = Column("tags", JSON)

    @validates("team")
    def lower_team(self, key, team):
        return team.lower().replace("_", "-")

    @validates("name")
    def lower_name(self, key, name):
        return name.lower().replace("_", "-")


@declarative_mixin
class DataMixin:
    data_uri = Column("data_uri", String(1024))
    data_type = Column("data_type", String(1024))
    runcard_uid = Column("runcard_uid", String(1024))
    pipelinecard_uid = Column("pipelinecard_uid", String(1024))
    datacard_uri = Column("datacard_uri", String(1024))


class DataSchema(Base, BaseMixin, DataMixin):  # type: ignore
    __tablename__ = RegistryTableNames.DATA.value

    def __repr__(self):
        return f"<SqlMetric({self.__tablename__}"


@declarative_mixin
class ModelMixin:
    modelcard_uri = Column("modelcard_uri", String(1024))
    datacard_uid = Column("datacard_uid", String(1024))
    trained_model_uri = Column("trained_model_uri", String(1024))
    model_metadata_uri = Column("model_metadata_uri", String(1024))
    sample_data_uri = Column("sample_data_uri", String(1024))
    sample_data_type = Column("sample_data_type", String(512))
    model_type = Column("model_type", String(512))
    runcard_uid = Column("runcard_uid", String(1024))
    pipelinecard_uid = Column("pipelinecard_uid", String(1024))


class ModelSchema(Base, BaseMixin, ModelMixin):  # type: ignore
    __tablename__ = RegistryTableNames.MODEL.value

    def __repr__(self):
        return f"<SqlMetric({self.__tablename__}"


@declarative_mixin
class RunMixin:
    datacard_uids = Column("datacard_uids", JSON)
    modelcard_uids = Column("modelcard_uids", JSON)
    pipelinecard_uid = Column("pipelinecard_uid", String(512))
    project_id = Column("project_id", String(512))
    artifact_uris = Column("artifact_uris", JSON)
    runcard_uri = Column("runcard_uri", String(512))


class RunSchema(Base, BaseMixin, RunMixin):  # type: ignore
    __tablename__ = RegistryTableNames.RUN.value

    def __repr__(self):
        return f"<SqlMetric({self.__tablename__}"


@declarative_mixin
class PipelineMixin:
    pipeline_code_uri = Column("pipeline_code_uri", String(512))
    datacard_uids = Column("datacard_uids", JSON)
    modelcard_uids = Column("modelcard_uids", JSON)
    runcard_uids = Column("runcard_uids", JSON)


class PipelineSchema(Base, BaseMixin, PipelineMixin):  # type: ignore
    __tablename__ = RegistryTableNames.PIPELINE.value

    def __repr__(self):
        return f"<SqlMetric({self.__tablename__}"


class ProjectSchema(Base):
    __tablename__ = RegistryTableNames.PROJECT.value

    uid = Column("uid", String(512), default=lambda: uuid.uuid4().hex)
    name = Column("name", String(512))
    team = Column("team", String(512))
    project_id = Column("project_id", String(512), primary_key=True)
    description = Column("description", String(512))
    version = Column("version", String(512))
    timestamp = Column("timestamp", BigInteger)


REGISTRY_TABLES = Union[  # pylint: disable=invalid-name
    DataSchema,
    ModelSchema,
    RunSchema,
    PipelineSchema,
    ProjectSchema,
]


class TableSchema:
    @staticmethod
    def get_table(table_name: str) -> Type[REGISTRY_TABLES]:  # type: ignore
        for table_schema in Base.__subclasses__():
            if table_name == table_schema.__tablename__:  # type: ignore
                return cast(Type[REGISTRY_TABLES], table_schema)

        raise ValueError(f"""Incorrect table name provided {table_name}""")
