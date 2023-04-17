import datetime
import os
import uuid
from enum import Enum
from typing import Type, Union, cast

from alembic import command
from alembic.config import Config
from sqlalchemy import BigInteger, Column, String
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.engine.reflection import Inspector
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declarative_mixin, validates  # type: ignore

from opsml_artifacts.helpers.logging import ArtifactLogger

logger = ArtifactLogger.get_logger(__name__)

Base = declarative_base()
YEAR_MONTH_DATE = "%Y-%m-%d"

DIR_PATH = os.path.dirname(__file__)


class RegistryTableNames(str, Enum):
    DATA = os.getenv("ML_DATA_REGISTRY_NAME", "OPSML_DATA_REGISTRY")
    MODEL = os.getenv("ML_MODEL_REGISTRY_NAME", "OPSML_MODEL_REGISTRY")
    RUN = os.getenv("ML_RUN_REGISTRY_NAME", "OPSML_RUN_REGISTRY")
    PIPELINE = os.getenv("ML_PIPELINE_REGISTRY_NAME", "OPSML_PIPELINE_REGISTRY")
    PROJECT = os.getenv("ML_PROJECT_REGISTRY_NAME", "OPSML_PROJECT_REGISTRY")


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
    modelcard_uri = Column("modelcard_uri", String(2048))
    datacard_uid = Column("datacard_uid", String(2048))
    trained_model_uri = Column("trained_model_uri", String(2048))
    onnx_model_uri = Column("onnx_model_uri", String(2048))
    sample_data_uri = Column("sample_data_uri", String(2048))
    sample_data_type = Column("sample_data_type", String(512))
    model_type = Column("model_type", String(512))


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
    metrics = Column("metrics", JSON)
    params = Column("params", JSON)
    tags = Column("tags", JSON)


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


def registry_tables_exist(engine) -> bool:
    table_names = Inspector.from_engine(engine).get_table_names()
    return set(table_names) == set(list(RegistryTableNames))


class DBInitializer:
    def __init__(self, engine):
        self.engine = engine

    def registry_tables_exist(self) -> bool:
        """Checks if all tables have been created previously"""
        table_names = Inspector.from_engine(self.engine).get_table_names()
        return set(table_names) == set(list(RegistryTableNames))

    def create_tables(self):
        """Creates tables"""
        logger.info("Creating database tables")
        Base.metadata.create_all(self.engine)

    def update_tables(self):
        """Updates tables in db based on alembic revisions"""

        # credit to mlflow for this implementation
        logger.info("Updating dbs")

        db_url = str(self.engine.url)

        config = self.get_alembic_config(db_url=db_url)
        with self.engine.begin() as connection:
            config.attributes["connection"] = connection  # pylint: disable=unsupported-assignment-operation
            command.upgrade(config, "heads")

    def get_alembic_config(self, db_url: str) -> Config:

        alembic_dir = os.path.join(DIR_PATH, "migration")
        db_url = db_url.replace("%", "%%")
        config = Config(os.path.join(alembic_dir, "alembic.ini"))
        config.set_main_option("sqlalchemy.url", db_url)
        config.set_main_option("script_location", f"{alembic_dir}/alembic")
        config.attributes["configure_logger"] = False  # pylint: disable=unsupported-assignment-operation

        return config

    def initialize(self) -> None:
        """Create tables if they don't exist and update"""
        if not self.registry_tables_exist():
            self.create_tables()
        self.update_tables()
