# pylint: disable=[import-outside-toplevel,import-outside-toplevel]

from enum import Enum
from functools import cached_property

import sqlalchemy
from pydantic import BaseSettings

from opsml_artifacts.helpers.logging import ArtifactLogger

logger = ArtifactLogger.get_logger(__name__)


class CloudSqlType(str, Enum):
    MYSQL = "mysql"
    POSTGRES = "postgres"


class PythonCloudSqlType(str, Enum):
    MYSQL = "pymysql"
    POSTGRES = "pg8000"


class CloudSqlPrefix(str, Enum):
    MYSQL = "mysql+pymysql://"
    POSTGRES = "postgresql+pg8000://"


class BaseSQLConnection(BaseSettings):
    """Base Connection model that all connections inherit from"""

    class Config:
        arbitrary_types_allowed = True
        extra = "allow"

    @cached_property
    def _sqlalchemy_prefix(self):
        raise NotImplementedError

    def get_engine(self) -> sqlalchemy.engine.base.Engine:
        raise NotImplementedError

    @staticmethod
    def validate_type(connector_type: str) -> bool:
        raise NotImplementedError


class SQLConnector:
    """Interface for finding correct subclass of BaseSQLConnection"""

    @staticmethod
    def get_connector(connector_type: Optional[str] = None) -> Type[BaseSQLConnection]:
        """Gets the appropriate SQL connector given the type specified"""

        if connector_type is None:
            conn_type = "local"
        conn_type = str(connector_type).lower()

        connector = next(
            (
                connector
                for connector in BaseSQLConnection.__subclasses__()
                if connector.validate_type(connector_type=conn_type)
            ),
            LocalSQLConnection,
        )
        return connector
