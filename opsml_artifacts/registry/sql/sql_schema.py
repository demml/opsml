import datetime
import time
import uuid
from enum import Enum
from typing import Type, Union, cast

from sqlalchemy import BigInteger, Column, Integer, String
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declarative_mixin  # type: ignore
from sqlalchemy.orm import sessionmaker

from opsml_artifacts.helpers.settings import settings
from opsml_artifacts.registry.sql.connection import create_sql_engine

Base = declarative_base()


class ArtifactTableNames(str, Enum):
    DATA_REGISTRY = "data"
    MODEL_REGISTRY = "model"
    EXPERIMENT_REGISTRY = "experiment"
    PIPELINE_REGISTRY = "pipeline"
    TEST_DATA_REGISTRY = "data_test"
    TEST_MODEL_REGISTRY = "model_test"
    TEST_EXPERIMENT_REGISTRY = "experiment_test"
    TEST_PIPELINE_REGISTRY = "pipeline_test"


@declarative_mixin
class DataMixin:

    uid = Column("uid", String(512), primary_key=True, default=lambda: uuid.uuid4().hex)
    date = Column("date", String(512), default=datetime.date.today().strftime("%Y-%m-%d"))
    timestamp = Column("timestamp", BigInteger, default=int(round(time.time() * 1000)))
    app_env = Column("app_env", String(512), default=settings.app_env)
    name = Column("name", String(512))
    team = Column("team", String(512))
    data_uri = Column("data_uri", String(2048))
    drift_uri = Column("drift_uri", String(2048))
    feature_map = Column("feature_map", JSON)
    feature_descriptions = Column("feature_descriptions", JSON)
    data_splits = Column("data_splits", JSON)
    data_type = Column("data_type", String(512))
    version = Column("version", Integer, nullable=False)
    user_email = Column("user_email", String(512))
    dependent_vars = Column("dependent_vars", JSON)

    __table_args__ = {"schema": "ds-artifact-registry"}


class DataSchema(Base, DataMixin):  # type: ignore
    __tablename__ = ArtifactTableNames.DATA_REGISTRY.name

    def __repr__(self):
        return f"<SqlMetric({self.__tablename__}"


class TestDataSchema(Base, DataMixin):  # type: ignore
    __tablename__ = ArtifactTableNames.TEST_DATA_REGISTRY.name

    def __repr__(self):
        return f"<SqlMetric({self.__tablename__}"


@declarative_mixin
class ModelMixin:

    uid = Column("uid", String(512), primary_key=True, default=lambda: uuid.uuid4().hex)
    date = Column("date", String(512), default=datetime.date.today().strftime("%Y-%m-%d"))
    timestamp = Column("timestamp", BigInteger, default=int(round(time.time() * 1000)))
    app_env = Column("app_env", String(512), default=settings.app_env)
    name = Column("name", String(512))
    team = Column("team", String(512))
    model_uri = Column("model_uri", String(2048))
    model_type = Column("model_type", String(512))
    version = Column("version", Integer, nullable=False)
    user_email = Column("user_email", String(512))

    __table_args__ = {"schema": "ds-artifact-registry"}


class ModelSchema(Base, ModelMixin):  # type: ignore
    __tablename__ = ArtifactTableNames.MODEL_REGISTRY.name

    def __repr__(self):
        return f"<SqlMetric({self.__tablename__}"


class TestModelSchema(Base, ModelMixin):  # type: ignore
    __tablename__ = ArtifactTableNames.TEST_MODEL_REGISTRY.name

    def __repr__(self):
        return f"<SqlMetric({self.__tablename__}"


@declarative_mixin
class ExperimentMixin:

    uid = Column("uid", String(512), primary_key=True, default=lambda: uuid.uuid4().hex)
    date = Column("date", String(512), default=datetime.date.today().strftime("%Y-%m-%d"))
    timestamp = Column("timestamp", BigInteger, default=int(round(time.time() * 1000)))
    app_env = Column("app_env", String(512), default=settings.app_env)
    name = Column("name", String(512))
    team = Column("team", String(512))
    version = Column("version", Integer, nullable=False)
    user_email = Column("user_email", String(512))
    data_card_uid = Column("data_card_uid", String(512))
    model_card_uid = Column("model_card_uid", String(512))
    pipeline_card_uid = Column("pipeline_card_uid", String(512))
    artifact_uris = Column("artifact_uris", JSON)
    metrics = Column("metrics", JSON)

    __table_args__ = {"schema": "ds-artifact-registry"}


class ExperimentSchema(Base, ExperimentMixin):  # type: ignore
    __tablename__ = ArtifactTableNames.EXPERIMENT_REGISTRY.name

    def __repr__(self):
        return f"<SqlMetric({self.__tablename__}"


class TestExperimentSchema(Base, ExperimentMixin):  # type: ignore
    __tablename__ = ArtifactTableNames.TEST_EXPERIMENT_REGISTRY.name

    def __repr__(self):
        return f"<SqlMetric({self.__tablename__}"


@declarative_mixin
class PipelineMixin:

    uid = Column("uid", String(512), primary_key=True, default=lambda: uuid.uuid4().hex)
    date = Column("date", String(512), default=datetime.date.today().strftime("%Y-%m-%d"))
    timestamp = Column("timestamp", BigInteger, default=int(round(time.time() * 1000)))
    app_env = Column("app_env", String(512), default=settings.app_env)
    name = Column("name", String(512))
    team = Column("team", String(512))
    version = Column("version", Integer, nullable=False)
    user_email = Column("user_email", String(512))
    pipeline_code_uri = Column("pipeline_code_uri", String(512))
    data_card_uids = Column("data_card_uids", JSON)
    model_card_uids = Column("model_card_uids", JSON)
    experiment_card_uids = Column("experiment_card_uids", JSON)

    __table_args__ = {"schema": "ds-artifact-registry"}


class PipelineSchema(Base, PipelineMixin):  # type: ignore
    __tablename__ = ArtifactTableNames.PIPELINE_REGISTRY.name

    def __repr__(self):
        return f"<SqlMetric({self.__tablename__}"


class TestPipelineSchema(Base, PipelineMixin):  # type: ignore
    __tablename__ = ArtifactTableNames.TEST_PIPELINE_REGISTRY.name

    def __repr__(self):
        return f"<SqlMetric({self.__tablename__}"


REGISTRY_TABLES = Union[  # pylint: disable=invalid-name
    DataSchema,
    TestDataSchema,
    ModelSchema,
    TestModelSchema,
    ExperimentSchema,
    TestExperimentSchema,
    PipelineSchema,
    TestPipelineSchema,
]

ARTIFACT_DATA_TABLES = [
    ArtifactTableNames.DATA_REGISTRY,
    ArtifactTableNames.TEST_DATA_REGISTRY,
]

ARTIFACT_MODEL_TABLES = [
    ArtifactTableNames.MODEL_REGISTRY,
    ArtifactTableNames.TEST_MODEL_REGISTRY,
]


class TableSchema:
    @staticmethod
    def get_table(table_name: str) -> Type[REGISTRY_TABLES]:  # type: ignore
        for table_schema in Base.__subclasses__():
            if table_name == table_schema.__tablename__:  # type: ignore
                return cast(Type[REGISTRY_TABLES], table_schema)

        raise ValueError(f"""Incorrect table name provided {table_name}""")


engine = create_sql_engine()
Session = sessionmaker(bind=engine)
