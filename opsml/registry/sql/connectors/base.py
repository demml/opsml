# pylint: disable=[import-outside-toplevel,import-outside-toplevel]
# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
import os
from enum import Enum
from functools import cached_property
from typing import Any, Dict

import sqlalchemy
from sqlalchemy.engine.url import make_url

from opsml.helpers.logging import ArtifactLogger

logger = ArtifactLogger.get_logger()
DEFAULT_POOL_SIZE = "10"
DEFAULT_OVERFLOW = "5"


class SqlType(str, Enum):
    CLOUDSQL_MYSQL = "cloudsql_mysql"
    CLOUDSQL_POSTGRES = "cloudsql_postgresql"
    LOCAL = "local"
    SQLITE = "sqlite"
    SQLITE_MEMORY = ":memory:"


class PythonCloudSqlType(str, Enum):
    MYSQL = "pymysql"
    POSTGRES = "pg8000"


class CloudSqlPrefix(str, Enum):
    MYSQL = "mysql+pymysql://"
    POSTGRES = "postgresql+pg8000://"


class BaseSQLConnection:
    def __init__(self, tracking_uri: str, credentials: Any = None):
        """Base Connection model that all connections inherit from"""

        self.tracking_uri = tracking_uri
        self.connection_parts = self._make_url()
        self.credentials = credentials

        self._engine = sqlalchemy.create_engine(
            self._sqlalchemy_prefix,
            **self.default_db_kwargs,
        )

    def _make_url(self) -> Any:
        if ":memory:" in self.tracking_uri:
            return None
        return make_url(self.tracking_uri)

    @cached_property
    def default_db_kwargs(self) -> Dict[str, int]:
        kwargs: Dict[str, Any] = {}
        if SqlType.SQLITE not in self.tracking_uri:
            kwargs = {
                "pool_size": int(os.getenv("OPSML_POOL_SIZE", DEFAULT_POOL_SIZE)),
                "max_overflow": int(os.getenv("OPSML_MAX_OVERFLOW", DEFAULT_OVERFLOW)),
            }

        # if using sqlite, use NullPool
        if SqlType.SQLITE in self.tracking_uri or SqlType.SQLITE_MEMORY in self.tracking_uri:
            kwargs["poolclass"] = sqlalchemy.pool.NullPool

        logger.info(
            "Default pool size: {}, overflow: {}",
            kwargs.get("pool_size", DEFAULT_POOL_SIZE),
            kwargs.get("max_overflow", DEFAULT_OVERFLOW),
        )
        return kwargs

    @cached_property
    def _sqlalchemy_prefix(self) -> str:
        raise NotImplementedError

    @property
    def sql_engine(self) -> sqlalchemy.engine.base.Engine:
        """Gets the sqlalchemy connection prefix"""
        return self._engine

    @staticmethod
    def validate_type(connector_type: str) -> bool:
        raise NotImplementedError


class CloudSQLConnection(BaseSQLConnection):
    """
    Cloud SQL connection string to pass to the registry for establishing
    a connection to a MySql or Postgres cloudsql DB

    """

    def __init__(self, tracking_uri: str, credentials: Any = None):
        super().__init__(tracking_uri, credentials)

        # overwrite engine

        self._engine = sqlalchemy.create_engine(
            self._sqlalchemy_prefix,
            creator=self._conn,
            **self.default_db_kwargs,
        )

    @property
    def _ip_type(self) -> Enum:
        """Sets IP type for CloudSql"""
        from google.cloud.sql.connector.instance import IPTypes

        return IPTypes.PRIVATE if os.environ.get("PRIVATE_IP") else IPTypes.PUBLIC

    @property
    def _connection_name(self) -> str:
        """Gets connection name from connection parts"""

        norm_query = self.connection_parts.normalized_query

        if "host" in norm_query.keys():
            connection_name = norm_query.get("host")[0]
        elif "unix_socket" in norm_query.keys():
            connection_name = norm_query.get("unix_socket")[0]
        else:
            raise ValueError("No unix_socket or host detected in uri")

        if "cloudsql" in connection_name:
            return str(connection_name.split("cloudsql/")[-1])
        return str(connection_name)

    @property
    def _python_db_type(self) -> str:
        """Gets db type for sqlalchemy connection prefix"""

        raise NotImplementedError

    def _conn(self) -> Any:
        """Creates the mysql or postgres CloudSQL client"""
        from google.cloud.sql.connector.connector import Connector

        connector = Connector(
            credentials=self.credentials,
            ip_type=self._ip_type,  # type: ignore
        )

        conn = connector.connect(
            instance_connection_string=self._connection_name,
            driver=self._python_db_type,
            user=self.connection_parts.username,
            password=self.connection_parts.password,
            db=self.connection_parts.database,
        )

        return conn

    @staticmethod
    def validate_type(connector_type: str) -> bool:
        return False
