# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
from functools import cached_property
from typing import Any, Dict, Optional, Type

from opsml.helpers.logging import ArtifactLogger
from opsml.helpers.utils import all_subclasses
from opsml.registry.sql.connectors.base import (
    BaseSQLConnection,
    CloudSQLConnection,
    CloudSqlPrefix,
    PythonCloudSqlType,
    SqlType,
)

logger = ArtifactLogger.get_logger()

_ENGINE_CACHE: Dict[str, BaseSQLConnection] = {}


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
            tracking_uri:
                The path to the sql URL. Should be in the form sqlite:///

            credentials:
                Optional credentials required by the local DB

        Returns:
            Instantiated class with required SQLite arguments
        """

        super().__init__(
            tracking_uri=tracking_uri,
            credentials=credentials,
        )

        self.storage_backend: str = SqlType.LOCAL.value

    @cached_property
    def _sqlalchemy_prefix(self) -> str:
        return self.tracking_uri

    @staticmethod
    def validate_type(connector_type: str) -> bool:
        return connector_type == SqlType.LOCAL


class DefaultConnector:
    def __init__(
        self,
        tracking_uri: str,
        credentials: Optional[Any] = None,
    ):
        self.tracking_uri = tracking_uri
        self.credentials = credentials

    def _get_connector_type_str(self) -> str:
        """Gets the sql connection type when running opsml locally (without api proxy)"""

        connector_type = "local"
        for db_type in ["postgresql", "mysql"]:
            if db_type in self.tracking_uri:
                connector_type = db_type

        if "cloudsql" in self.tracking_uri:
            connector_type = f"cloudsql_{connector_type}"

        return connector_type

    def _get_connector_type(self, connector_type: str) -> Type[BaseSQLConnection]:
        """Gets the sql connection given a connector type"""
        return next(
            (
                connector
                for connector in all_subclasses(BaseSQLConnection)
                if connector.validate_type(connector_type=connector_type)
            ),
            LocalSQLConnection,
        )

    def get_connector(self) -> BaseSQLConnection:
        """Gets the sql connector to use when running opsml locally (without api proxy)"""

        cached_conn = _ENGINE_CACHE.get(self.tracking_uri)
        if cached_conn is not None:
            return cached_conn

        connector_type = self._get_connector_type(connector_type=self._get_connector_type_str())
        connector = connector_type(self.tracking_uri, self.credentials)

        _ENGINE_CACHE[self.tracking_uri] = connector
        return connector
