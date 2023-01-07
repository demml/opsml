import datetime
import time
import uuid
from typing import Type

from sqlalchemy import BigInteger, Column, Integer, String
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declarative_mixin  # type: ignore

from opsml_data.helpers.settings import settings

Base = declarative_base()


@declarative_mixin
class DataMixin:

    uid = Column("uid", String(512), primary_key=True, default=lambda: uuid.uuid4().hex)
    date = Column("date", String(512), default=datetime.date.today().strftime("%Y-%m-%d"))
    timestamp = Column("timestamp", BigInteger, default=int(round(time.time() * 1000)))
    app_env = Column("app_env", String(512), default=settings.app_env)
    data_name = Column("data_name", String(512))
    team = Column("team", String(512))
    data_uri = Column("data_uri", String(2048))
    drift_uri = Column("drift_uri", String(2048))
    feature_map = Column("feature_map", JSON)
    data_splits = Column("data_splits", JSON)
    data_type = Column("data_type", String(512))
    version = Column("version", Integer, nullable=False)
    user_email = Column("user_email", String(512))
    dependent_vars = Column("dependent_vars", JSON)

    __table_args__ = {"schema": "ds-data-registry"}


class DataSchema(Base, DataMixin):  # type: ignore
    __tablename__ = "data_registry"

    def __repr__(self):
        return f"<SqlMetric({self.__tablename__}"


class TestDataSchema(Base, DataMixin):  # type: ignore
    __tablename__ = "test_data_registry"

    def __repr__(self):
        return f"<SqlMetric({self.__tablename__}"


class TableSchema:
    @staticmethod
    def get_table(table_name: str) -> Type[Base]:  # type: ignore
        for table_schema in Base.__subclasses__():
            if table_name == table_schema.__tablename__:  # type: ignore
                return table_schema

        # return default
        return DataSchema
