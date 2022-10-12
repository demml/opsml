from sqlalchemy import Column, String, Integer, Boolean, BigInteger, Float, FLOAT

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import JSON


base = declarative_base()


class SqlDataRegistrySchema(base):
    __tablename__ = "data_registry"

    date = Column("date", String(100))
    timestamp = Column(
        "timestamp",
        FLOAT,
        primary_key=True,
    )
    table_name = Column("table_name", String(100))
    storage_uri = Column("storage_uri", String(100))
    feature_mapping = Column("feature_mapping", JSON)
    version = Column("version", Integer, nullable=False)

    __table_args__ = {"schema": "flight-plan-data-registry"}

    def __repr__(cls):
        return f"<SqlMetric({cls.__tablename__}"
