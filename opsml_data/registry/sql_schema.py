import datetime
import time
import uuid
from typing import Union

from sqlalchemy import BigInteger, Column, Integer, String
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declarative_mixin

from opsml_data.helpers.defaults import params

Base = declarative_base()


@declarative_mixin
class DataMixin:

    uid = Column("uuid", String(length=32), primary_key=True, default=lambda: uuid.uuid4().hex)
    date = Column("date", String(100), default=datetime.date.today().strftime("%Y-%m-%d"))
    timestamp = Column("timestamp", BigInteger, default=int(round(time.time() * 1000)))
    app_env = Column("app_env", String(100), default=params.app_env)
    data_name = Column("data_name", String(100))
    team = Column("team", String(100))
    data_uri = Column("data_uri", String(100))
    drift_uri = Column("drift_uri", String(100))
    feature_map = Column("feature_map", JSON)
    data_splits = Column("data_splits", JSON)
    data_type = Column("data_type", String(100))
    version = Column("version", Integer, nullable=False)
    user_email = Column("user_email", String(100))

    __table_args__ = {"schema": "ds-data-registry"}


class DataSchema(Base, DataMixin):
    __tablename__ = "data_registry"

    def __repr__(self):
        return f"<SqlMetric({self.__tablename__}"


class TestDataSchema(Base, DataMixin):
    __tablename__ = "test_data_registry"

    def __repr__(self):
        return f"<SqlMetric({self.__tablename__}"


class TableSchema:
    @staticmethod
    def get_table(table_name: str) -> Union[DataSchema, TestDataSchema]:
        for table_schema in Base.__subclasses__():
            if table_name == table_schema.__tablename__:
                return table_schema

        # return default
        return DataSchema
