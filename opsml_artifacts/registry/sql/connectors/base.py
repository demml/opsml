# pylint: disable=[import-outside-toplevel,import-outside-toplevel]
from typing import Dict, Any
from functools import cached_property
import os
import sqlalchemy
from sqlalchemy.engine.url import make_url

from opsml_artifacts.helpers.logging import ArtifactLogger

logger = ArtifactLogger.get_logger(__name__)


class BaseSQLConnection:
    def __init__(self, tracking_url: str):
        """Base Connection model that all connections inherit from"""

        self.tracking_url = tracking_url
        self.connection_parts = make_url(tracking_url)

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

    def __init__(self, tracking_url: str, gcp_credentials: Any):
        super().__init__(tracking_url=tracking_url)
        self.gcp_creds = gcp_credentials

    def _ip_type(self) -> str:
        """Sets IP type for CloudSql"""
        from google.cloud.sql.connector import IPTypes

        return IPTypes.PRIVATE if os.environ.get("PRIVATE_IP") else IPTypes.PUBLIC

    def _connection_name(self) -> str:
        """Gets connection name from connection parts"""

        connection_name = self.connection_parts.normalized_query.get("host")[0]
        if "cloudsql" in connection_name:
            return connection_name.split("cloudsql/")[-1]

    def _python_db_type(self) -> str:
        """Gets db type for sqlalchemy connection prefix"""

        raise NotImplementedError

    @cached_property
    def _conn(self):

        """Creates the mysql or postgres CloudSQL client"""
        from google.cloud.sql.connector import Connector

        connector = Connector(credentials=self.gcp_creds)

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
