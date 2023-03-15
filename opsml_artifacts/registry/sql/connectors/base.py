# pylint: disable=[import-outside-toplevel,import-outside-toplevel]
import os
from functools import cached_property
from typing import Any

import sqlalchemy
from sqlalchemy.engine.url import make_url

from opsml_artifacts.helpers.logging import ArtifactLogger

logger = ArtifactLogger.get_logger(__name__)


class BaseSQLConnection:
    def __init__(self, tracking_uri: str, credentials: Any = None):
        """Base Connection model that all connections inherit from"""

        self.tracking_uri = tracking_uri
        self.connection_parts = self._make_url()
        self.credentials = credentials

    def _make_url(self) -> Any:
        if ":memory:" in self.tracking_uri:
            return None
        return make_url(self.tracking_uri)

    @cached_property
    def _sqlalchemy_prefix(self):
        raise NotImplementedError

    def get_engine(self) -> sqlalchemy.engine.base.Engine:
        raise NotImplementedError

    @staticmethod
    def validate_type(connector_type: str) -> bool:
        raise NotImplementedError


class CloudSQLConnection(BaseSQLConnection):
    """Cloud SQL connection string to pass to the registry for establishing
    a connection to a MySql or Postgres cloudsql DB

    """

    def _ip_type(self) -> str:
        """Sets IP type for CloudSql"""
        from google.cloud.sql.connector import IPTypes

        return IPTypes.PRIVATE if os.environ.get("PRIVATE_IP") else IPTypes.PUBLIC

    def _connection_name(self) -> str:
        """Gets connection name from connection parts"""

        connection_name = self.connection_parts.normalized_query.get("host")[0]  # type: ignore
        if "cloudsql" in connection_name:
            return connection_name.split("cloudsql/")[-1]
        return connection_name

    @property
    def _python_db_type(self) -> str:
        """Gets db type for sqlalchemy connection prefix"""

        raise NotImplementedError

    @cached_property
    def _conn(self):

        """Creates the mysql or postgres CloudSQL client"""
        from google.cloud.sql.connector import Connector

        connector = Connector(credentials=self.credentials)

        return connector.connect(
            instance_connection_string=self._connection_name,
            driver=self._python_db_type,
            user=self.connection_parts.username,
            password=self.connection_parts.password,
            db=self.connection_parts.database,
            ip_type=self._ip_type,
        )

    def get_engine(self) -> sqlalchemy.engine.base.Engine:
        """Creates SQLAlchemy engine"""

        return sqlalchemy.create_engine(
            self._sqlalchemy_prefix,
            creator=self._conn,
        )

    @staticmethod
    def validate_type(connector_type: str) -> bool:
        return False
