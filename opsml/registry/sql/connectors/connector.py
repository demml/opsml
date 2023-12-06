# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
from functools import cached_property
from typing import Any, Type, cast

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
