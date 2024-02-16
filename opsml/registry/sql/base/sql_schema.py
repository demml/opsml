# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
import datetime as dt
import os
import uuid
from datetime import date
from typing import List, cast

from sqlalchemy import BigInteger, Boolean, Column, Float, Integer, String
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import declarative_base, declarative_mixin, validates

from opsml.helpers.logging import ArtifactLogger
from opsml.types import RegistryTableNames

logger = ArtifactLogger.get_logger()

Base = declarative_base()


@declarative_mixin
class BaseMixin:
    uid = Column("uid", String(64), primary_key=True, default=lambda: uuid.uuid4().hex)
    date = Column("date", String(32), default=lambda: str(date.today()))
    timestamp = Column("timestamp", BigInteger)
    app_env = Column("app_env", String(32), default=os.getenv("APP_ENV", "development"))
    name = Column("name", String(128))
    repository = Column("repository", String(128))
    version = Column("version", String(64), nullable=False)
    contact = Column("contact", String(64))
    tags = Column("tags", JSON)

    @validates("repository")
    def lower_repository(self, key: str, repository: str) -> str:
        return repository.lower().replace("_", "-")

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
    data_type = Column("data_type", String(64))
    runcard_uid = Column("runcard_uid", String(64))
    pipelinecard_uid = Column("pipelinecard_uid", String(64))
    auditcard_uid = Column("auditcard_uid", String(64))


class DataSchema(Base, BaseMixin, DataMixin):
    __tablename__ = RegistryTableNames.DATA.value

    def __repr__(self) -> str:
        return f"<SqlTable: {self.__tablename__}>"


@declarative_mixin
class ModelMixin:
    datacard_uid = Column("datacard_uid", String(64))
    sample_data_type = Column("sample_data_type", String(64))
    model_type = Column("model_type", String(64))
    runcard_uid = Column("runcard_uid", String(64))
    pipelinecard_uid = Column("pipelinecard_uid", String(64))
    auditcard_uid = Column("auditcard_uid", String(64))


class ModelSchema(Base, BaseMixin, ModelMixin):
    __tablename__ = RegistryTableNames.MODEL.value

    def __repr__(self) -> str:
        return f"<SqlTable: {self.__tablename__}>"


@declarative_mixin
class RunMixin:
    datacard_uids = Column("datacard_uids", JSON)
    modelcard_uids = Column("modelcard_uids", JSON)
    pipelinecard_uid = Column("pipelinecard_uid", String(64))
    project = Column("project", String(64))
    artifact_uris = Column("artifact_uris", JSON)


class RunSchema(Base, BaseMixin, RunMixin):
    __tablename__ = RegistryTableNames.RUN.value

    def __repr__(self) -> str:
        return f"<SqlTable: {self.__tablename__}>"


@declarative_mixin
class AuditMixin:
    approved = Column("approved", Boolean)
    datacards = Column("datacard_uids", JSON)
    modelcards = Column("modelcard_uids", JSON)
    runcards = Column("runcard_uids", JSON)


class AuditSchema(Base, BaseMixin, AuditMixin):
    __tablename__ = RegistryTableNames.AUDIT.value

    def __repr__(self) -> str:
        return f"<SqlTable: {self.__tablename__}>"


@declarative_mixin
class PipelineMixin:
    pipeline_code_uri = Column("pipeline_code_uri", String(256))
    datacard_uids = Column("datacard_uids", JSON)
    modelcard_uids = Column("modelcard_uids", JSON)
    runcard_uids = Column("runcard_uids", JSON)


class PipelineSchema(Base, BaseMixin, PipelineMixin):
    __tablename__ = RegistryTableNames.PIPELINE.value

    def __repr__(self) -> str:
        return f"<SqlTable: {self.__tablename__}>"


class ProjectSchema(Base):
    __tablename__ = RegistryTableNames.PROJECT.value

    uid = Column("uid", String(64), default=lambda: uuid.uuid4().hex)
    name = Column("name", String(128))
    repository = Column("repository", String(128))
    project_id = Column("project_id", Integer, primary_key=True)
    version = Column("version", String(64), nullable=False)
    timestamp = Column("timestamp", BigInteger)

    def __repr__(self) -> str:
        return f"<SqlTable: {self.__tablename__}>"


class MetricSchema(Base):
    __tablename__ = RegistryTableNames.METRICS.value

    run_uid = Column("uid", String(64))
    name = Column("name", String(128))
    value = Column("value", Float)
    step = Column("step", Integer)
    timestamp = Column("timestamp", BigInteger)
    date_ts = Column("date_ts", String(64), default=lambda: str(dt.datetime.now()))
    idx = Column(Integer, primary_key=True)

    def __repr__(self) -> str:
        return f"<SqlTable: {self.__tablename__}>"


AVAILABLE_TABLES: List[CardSQLTable] = []
for schema in Base.__subclasses__():
    if schema.__tablename__ not in [
        RegistryTableNames.BASE.value,
        RegistryTableNames.METRICS.value,
    ]:
        AVAILABLE_TABLES.append(cast(CardSQLTable, schema))


class SQLTableGetter:
    @staticmethod
    def get_table(table_name: str) -> CardSQLTable:
        for table_schema in AVAILABLE_TABLES:
            if table_name == table_schema.__tablename__:
                return table_schema

        raise ValueError(f"""Incorrect table name provided {table_name}""")
