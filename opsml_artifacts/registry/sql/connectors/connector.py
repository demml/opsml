from enum import Enum
from typing import Type, Union
import os
from functools import cached_property
import sqlalchemy
from opsml_artifacts.registry.sql.connectors.base import CloudSQLConnection, BaseSQLConnection


class SqlType(str, Enum):
    CLOUDSQL_MYSQL = "cloudsql_mysql"
    CLOUDSQL_POSTGRES = "cloudsql_postgres"
    LOCAL = "local"


class PythonCloudSqlType(str, Enum):
    MYSQL = "pymysql"
    POSTGRES = "pg8000"


class CloudSqlPrefix(str, Enum):
    MYSQL = "mysql+pymysql://"
    POSTGRES = "postgresql+pg8000://"


class CloudSqlPostgres(CloudSQLConnection):
    @property
    def _sqlalchemy_prefix(self) -> str:
        return CloudSqlPrefix.POSTGRES.value

    @property
    def _python_db_type(self) -> str:
        return PythonCloudSqlType.POSTGRES.value

    @staticmethod
    def validate_type(connector_type: str) -> bool:
        return connector_type == SqlType.CLOUDSQL_POSTGRES


class CloudSqlMySql(CloudSQLConnection):
    @property
    def _sqlalchemy_prefix(self) -> str:
        return CloudSqlPrefix.MYSQL.value

    @property
    def _python_db_type(self) -> str:
        return PythonCloudSqlType.MYSQL.value

    @staticmethod
    def validate_type(connector_type: str) -> bool:
        return connector_type == SqlType.CLOUDSQL_MYSQL


class LocalSQLConnection(BaseSQLConnection):
    def __init__(self):
        """
        Args:
            new database named "opsml_artifacts.db" will be created in the home user directory.
            If the "opsml_artifacts.db" already exists, a connection will be re-established (the
            database will not be overwritten)
            storage_backend (str): Which storage system to use. Defaults to local
        Returns:
            Instantiated class with required SQLite arguments
        """

        self.db_file_path: str = f"{os.path.expanduser('~')}/opsml_artifacts_database.db"
        self.storage_backend: str = SqlType.LOCAL.value

    @cached_property
    def _sqlalchemy_prefix(self):
        return "sqlite://"

    def get_engine(self) -> sqlalchemy.engine.base.Engine:
        engine = sqlalchemy.create_engine(f"{self._sqlalchemy_prefix}/{self.db_file_path}")
        return engine

    @staticmethod
    def validate_type(connector_type: str) -> bool:
        return connector_type == SqlType.LOCAL


SqlConnectorType = Union[CloudSqlMySql, CloudSqlPostgres, LocalSQLConnection]


class SQLConnector:
    """Interface for finding correct subclass of BaseSQLConnection"""

    @staticmethod
    def get_connector(connector_type: str) -> Type[BaseSQLConnection]:
        """Gets the appropriate SQL connector given the type specified"""

        connector = next(
            (
                connector
                for connector in BaseSQLConnection.__subclasses__()
                if connector.validate_type(connector_type=connector_type)
            ),
            LocalSQLConnection,
        )
        return connector
