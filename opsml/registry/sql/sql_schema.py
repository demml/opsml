# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
import os
import uuid
from datetime import date
from typing import List, cast

from sqlalchemy import BigInteger, Boolean, Column, String
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declarative_mixin, validates

from opsml.helpers.logging import ArtifactLogger
from opsml.registry.sql.table_names import RegistryTableNames

logger = ArtifactLogger.get_logger()

Base = declarative_base()


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
    def lower_team(self, key: str, team: str) -> str:
        return team.lower().replace("_", "-")

    @validates("name")
    def lower_name(self, key: str, name: str) -> str:
        return name.lower().replace("_", "-")


# this is only used for type hinting. All tables follow the same base structure
# Ideally we should be able to use this as the parent to all other tables, but
# sqlalchemy's inheritance structure and how it relates to table creation is not straightforward.
class CardSQLTable(Base, BaseMixin):
    __tablename__ = RegistryTableNames.BASE.value

    def __repr__(self) -> str:
        return f"{self.__tablename__}"


@declarative_mixin
class DataMixin:
    data_uri = Column("data_uri", String(1024))
    data_type = Column("data_type", String(1024))
    runcard_uid = Column("runcard_uid", String(1024))
    pipelinecard_uid = Column("pipelinecard_uid", String(1024))
    datacard_uri = Column("datacard_uri", String(1024))
    auditcard_uid = Column("auditcard_uid", String(1024))
    uris = Column("uris", JSON)


class DataSchema(Base, BaseMixin, DataMixin):
    __tablename__ = RegistryTableNames.DATA.value

    def __repr__(self) -> str:
        return f"<SqlTable: {self.__tablename__}>"


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
    auditcard_uid = Column("auditcard_uid", String(1024))


class ModelSchema(Base, BaseMixin, ModelMixin):
    __tablename__ = RegistryTableNames.MODEL.value

    def __repr__(self) -> str:
        return f"<SqlTable: {self.__tablename__}>"


@declarative_mixin
class RunMixin:
    datacard_uids = Column("datacard_uids", JSON)
    modelcard_uids = Column("modelcard_uids", JSON)
    pipelinecard_uid = Column("pipelinecard_uid", String(512))
    project_id = Column("project_id", String(512))
    artifact_uris = Column("artifact_uris", JSON)
    runcard_uri = Column("runcard_uri", String(512))


class RunSchema(Base, BaseMixin, RunMixin):
    __tablename__ = RegistryTableNames.RUN.value

    def __repr__(self) -> str:
        return f"<SqlTable: {self.__tablename__}>"


@declarative_mixin
class AuditMixin:
    approved = Column("approved", Boolean)
    audit_uri = Column("audit_uri", String(2048))
    datacards = Column("datacard_uids", JSON)
    modelcards = Column("modelcard_uids", JSON)
    runcards = Column("runcard_uids", JSON)


class AuditSchema(Base, BaseMixin, AuditMixin):
    __tablename__ = RegistryTableNames.AUDIT.value

    def __repr__(self) -> str:
        return f"<SqlTable: {self.__tablename__}>"


@declarative_mixin
class PipelineMixin:
    pipeline_code_uri = Column("pipeline_code_uri", String(512))
    datacard_uids = Column("datacard_uids", JSON)
    modelcard_uids = Column("modelcard_uids", JSON)
    runcard_uids = Column("runcard_uids", JSON)


class PipelineSchema(Base, BaseMixin, PipelineMixin):
    __tablename__ = RegistryTableNames.PIPELINE.value

    def __repr__(self) -> str:
        return f"<SqlTable: {self.__tablename__}>"


class ProjectSchema(Base):
    __tablename__ = RegistryTableNames.PROJECT.value

    uid = Column("uid", String(512), default=lambda: uuid.uuid4().hex)
    name = Column("name", String(512))
    team = Column("team", String(512))
    project_id = Column("project_id", String(512), primary_key=True)
    description = Column("description", String(512))
    version = Column("version", String(512))
    timestamp = Column("timestamp", BigInteger)

    def __repr__(self) -> str:
        return f"<SqlTable: {self.__tablename__}>"


AVAILABLE_TABLES: List[CardSQLTable] = []
for schema in Base.__subclasses__():
    if schema.__tablename__ != RegistryTableNames.BASE.value:  # type: ignore[attr-defined]
        AVAILABLE_TABLES.append(cast(CardSQLTable, schema))


class SQLTableGetter:
    @staticmethod
    def get_table(table_name: str) -> CardSQLTable:
        for table_schema in AVAILABLE_TABLES:
            if table_name == table_schema.__tablename__:
                return table_schema

        raise ValueError(f"""Incorrect table name provided {table_name}""")
