# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from opsml.registry.utils.settings import settings


# no typing in order to prevent imports before they're needed
def get_registry():  # type: ignore
    """Get the registry object based on the settings"""

    # initialize tables
    if settings.request_client is None:
        from typing import cast

        from sqlalchemy.engine.base import Engine

        from opsml.registry.sql.base.server import ServerRegistry
        from opsml.registry.sql.db_initializer import DBInitializer
        from opsml.registry.sql.table_names import RegistryTableNames

        db_initializer = DBInitializer(
            engine=cast(Engine, settings.connection_client.sql_engine),
            registry_tables=list(RegistryTableNames),
        )
        db_initializer.initialize()

        return db_initializer, ServerRegistry

    from opsml.registry.sql.base.client import ClientRegistry

    return None, ClientRegistry


initializer, OpsmlRegistry = get_registry()  # type:ignore
