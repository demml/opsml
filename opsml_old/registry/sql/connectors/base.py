# pylint: disable=[import-outside-toplevel,import-outside-toplevel]
# Copyright (c) 2023-2024 Shipt, Inc.
# Copyright (c) 2024-current Demml, Inc.
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
    LOCAL = "local"
    SQLITE = "sqlite"
    SQLITE_MEMORY = ":memory:"


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
