# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
from functools import cached_property
from typing import Any, Dict, Optional

from opsml.helpers.logging import ArtifactLogger
from opsml.registry.sql.connectors.base import BaseSQLConnection, SqlType

logger = ArtifactLogger.get_logger()

_ENGINE_CACHE: Dict[str, BaseSQLConnection] = {}


class SQLConnection(BaseSQLConnection):
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

        return connector_type

    def get_connector(self) -> SQLConnection:
        """Gets the sql connector to use when running opsml locally (without api proxy)"""

        cached_conn = _ENGINE_CACHE.get(self.tracking_uri)
        if cached_conn is not None:
            return cached_conn

        connector = SQLConnection(self.tracking_uri, self.credentials)

        _ENGINE_CACHE[self.tracking_uri] = connector
        return connector
