from sqlalchemy import (
    Column,
    String,
    Integer,
    Boolean,
    BigInteger,
)

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import JSON


base = declarative_base()


class SqlDataRegistrySchema(base):
    __tablename__ = "data_registry"

    date = Column("date", String)
    timestamp = Column("timestamp", BigInteger, primary_key=True)
    table_name = Column("table_name", String)
    mappings = Column("pipeline_metadata", JSON)
    version_id = Column(Integer, nullable=False)

    __table_args__ = {"schema": "data"}
    __mapper_args__ = {"version_id_col": version_id}

    def __repr__(cls):
        return f"<SqlMetric({cls.__tablename__}"
