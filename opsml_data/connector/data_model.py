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
    mappings = Column("pipeline_metadata", JSON)
    version_id = Column("version_id", Integer, nullable=False)

    __table_args__ = {"schema": "flight-plan-data-registry"}
    __mapper_args__ = {"version_id_col": version_id}

    def __repr__(cls):
        return f"<SqlMetric({cls.__tablename__}"
