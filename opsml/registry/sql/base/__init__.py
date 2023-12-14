# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import cast

from opsml.helpers.logging import ArtifactLogger
from opsml.helpers.utils import OpsmlImportExceptions
from opsml.settings.config import config

logger = ArtifactLogger.get_logger()


# no typing in order to prevent imports before they're needed
def get_registry():  # type: ignore
    """Get the registry object based on the settings"""

    if config.is_tracking_local:
        logger.info("Initializing SQL: verifying the [server] extra is installed.")
        OpsmlImportExceptions.try_sql_import()

        from sqlalchemy.engine.base import Engine

        from opsml.registry.sql.base.server import ServerRegistry
        from opsml.registry.sql.connectors.connector import DefaultConnector
        from opsml.registry.sql.db_initializer import DBInitializer
        from opsml.registry.sql.table_names import RegistryTableNames

        connector = DefaultConnector(tracking_uri=config.opsml_tracking_uri).get_connector()
        db_initializer = DBInitializer(
            engine=cast(Engine, connector.sql_engine),
            registry_tables=list(RegistryTableNames),
        )
        db_initializer.initialize()

        return db_initializer, ServerRegistry

    from opsml.registry.sql.base.client import ClientRegistry

    return None, ClientRegistry


initializer, OpsmlRegistry = get_registry()  # type:ignore
