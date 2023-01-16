import datetime
import os
import time
import uuid
from enum import Enum
from typing import Any, Dict, Type, Union, cast

from pyshipt_logging import ShiptLogging
from sqlalchemy import BigInteger, Column, Integer, String
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declarative_mixin  # type: ignore
from sqlalchemy.orm import sessionmaker

from opsml_artifacts.helpers.settings import settings
from opsml_artifacts.registry.sql.connection import create_sql_engine

logger = ShiptLogging.get_logger(__name__)
Base = declarative_base()
year_month_date = "%Y-%m-%d"


class RegistryTableNames(str, Enum):
    DATA = os.getenv("ML_DATA_REGISTRY_NAME", "DATA_REGISTRTY")
    MODEL = os.getenv("ML_MODEL_REGISTRY_NAME", "MODEL_REGISTRY")
    EXPERIMENT = os.getenv("ML_EXPERIMENT_REGISTRY_NAME", "EXPERIMENT_REGISTRY")
    PIPELINE = os.getenv("ML_PIPELINE_REGISTRY_NAME", "PIPELINE_REGISTRY")


@declarative_mixin
class BaseMixin:
    uid = Column("uid", String(512), primary_key=True, default=lambda: uuid.uuid4().hex)
    date = Column("date", String(512), default=datetime.date.today().strftime(year_month_date))
    timestamp = Column("timestamp", BigInteger, default=int(round(time.time() * 1000)))
    app_env = Column("app_env", String(512), default=settings.app_env)
    name = Column("name", String(512))
    team = Column("team", String(512))
    version = Column("version", Integer, nullable=False)
    user_email = Column("user_email", String(512))


@declarative_mixin
class DataMixin:
    data_uri = Column("data_uri", String(2048))
    drift_uri = Column("drift_uri", String(2048))
    feature_map = Column("feature_map", JSON)
    feature_descriptions = Column("feature_descriptions", JSON)
    data_splits = Column("data_splits", JSON)
    data_type = Column("data_type", String(512))
    dependent_vars = Column("dependent_vars", JSON)

    __table_args__ = {"schema": "ds-artifact-registry"}


class DataSchema(Base, BaseMixin, DataMixin):  # type: ignore
    __tablename__ = RegistryTableNames.DATA.value

    def __repr__(self):
        return f"<SqlMetric({self.__tablename__}"


@declarative_mixin
class ModelMixin:
    model_uri = Column("model_uri", String(2048))
    model_type = Column("model_type", String(512))

    __table_args__ = {"schema": "ds-artifact-registry"}


class ModelSchema(Base, BaseMixin, ModelMixin):  # type: ignore
    __tablename__ = RegistryTableNames.MODEL.value

    def __repr__(self):
        return f"<SqlMetric({self.__tablename__}"


@declarative_mixin
class ExperimentMixin:
    data_card_uid = Column("data_card_uid", String(512))
    model_card_uid = Column("model_card_uid", String(512))
    pipeline_card_uid = Column("pipeline_card_uid", String(512))
    artifact_uris = Column("artifact_uris", JSON)
    metrics = Column("metrics", JSON)

    __table_args__ = {"schema": "ds-artifact-registry"}


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

    __table_args__ = {"schema": "ds-artifact-registry"}


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


engine = create_sql_engine()
Session = sessionmaker(bind=engine)


class SqlManager:
    def __init__(self, table_name: str):
        self._session = Session
        self._table = TableSchema.get_table(table_name=table_name)
        self._create_table()
        self.table_name = self._table.__tablename__

    def _create_table(self):
        self._table.__table__.create(bind=engine, checkfirst=True)

    def _exceute_query(self, query: Any):
        with self._session() as sess:
            result = sess.scalars(query).first()
        return result

    def _add_commit_transaction(self, record=Type[REGISTRY_TABLES]):
        with self._session() as sess:
            sess.add(record)
            sess.commit()

    def _update_record_transaction(
        self,
        table: Type[REGISTRY_TABLES],
        record_uid: str,
        record: Dict[str, Any],
    ):
        with self._session() as sess:
            query = sess.query(table).filter(table.uid == record_uid)
            query.update(record)
            sess.commit()
