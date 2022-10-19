from sqlalchemy import BigInteger, Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import JSON
from pydantic import BaseModel
from typing import Dict, Optional
import datetime
import time

base = declarative_base()


class DataModel(BaseModel):
    date: Optional[str] = datetime.date.today().strftime("%Y-%m-%d")
    timestamp: Optional[int] = int(round(time.time() * 1000))
    table_name: str
    storage_uri: str
    feature_mapping: Dict[str, str]
    version: int
    user_email: str


class SqlDataRegistrySchema(base):
    __tablename__ = "data_registry"

    date = Column("date", String(100))
    timestamp = Column(
        "timestamp",
        BigInteger,
        primary_key=True,
    )
    table_name = Column("table_name", String(100))
    storage_uri = Column("storage_uri", String(100))
    feature_mapping = Column("feature_mapping", JSON)
    version = Column("version", Integer, nullable=False)
    user_email = Column("user_email", String(100))

    __table_args__ = {"schema": "flight-plan-data-registry"}

    def __repr__(cls):
        return f"<SqlMetric({cls.__tablename__}"


# for testing purposes
class TestSqlDataRegistrySchema(base):
    __tablename__ = "test_data_registry"

    date = Column("date", String(100))
    timestamp = Column(
        "timestamp",
        BigInteger,
        primary_key=True,
    )
    table_name = Column("table_name", String(100))
    storage_uri = Column("storage_uri", String(100))
    feature_mapping = Column("feature_mapping", JSON)
    version = Column("version", Integer, nullable=False)
    user_email = Column("user_email", String(100))

    __table_args__ = {"schema": "flight-plan-data-registry"}

    def __repr__(cls):
        return f"<SqlMetric({cls.__tablename__}"
