# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
from enum import Enum
from functools import cached_property
from typing import Any, Type, cast

import sqlalchemy

from opsml.helpers.utils import all_subclasses
from opsml.registry.sql.connectors.base import BaseSQLConnection, CloudSQLConnection


class SqlType(str, Enum):
    CLOUDSQL_MYSQL = "cloudsql_mysql"
    CLOUDSQL_POSTGRES = "cloudsql_postgresql"
    LOCAL = "local"


class PythonCloudSqlType(str, Enum):
    MYSQL = "pymysql"
    POSTGRES = "pg8000"


class CloudSqlPrefix(str, Enum):
    MYSQL = "mysql+pymysql://"
    POSTGRES = "postgresql+pg8000://"


class CloudSqlPostgresql(CloudSQLConnection):
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
    def __init__(
        self,
        tracking_uri: str,
        credentials: Any = None,
    ):
        """
        Args:
            new database named "opsml.db" will be created in the home user directory.
            If the "opsml.db" already exists, a connection will be re-established (the
            database will not be overwritten)
            storage_backend (str): Which storage system to use. Defaults to local
        Returns:
            Instantiated class with required SQLite arguments
        """

        super().__init__(
            tracking_uri=tracking_uri,
            credentials=credentials,
        )

        self.storage_backend: str = SqlType.LOCAL.value

    @cached_property
    def _sqlalchemy_prefix(self):
        return self.tracking_uri

    def get_engine(self) -> sqlalchemy.engine.base.Engine:
        engine = sqlalchemy.create_engine(self._sqlalchemy_prefix)
        return engine

    @staticmethod
    def validate_type(connector_type: str) -> bool:
        return connector_type == SqlType.LOCAL


class SQLConnector:
    """Interface for finding correct subclass of BaseSQLConnection"""

    @staticmethod
    def get_connector(connector_type: str) -> Type[BaseSQLConnection]:
        """Gets the appropriate SQL connector given the type specified"""

        connector = next(
            (
                connector
                for connector in all_subclasses(BaseSQLConnection)
                if connector.validate_type(connector_type=connector_type)
            ),
            LocalSQLConnection,
        )
        return cast(Type[BaseSQLConnection], connector)
