# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from opsml.registry.utils.settings import settings


def get_registry():
    """Get the registry object based on the settings"""

    # initialize tables
    if settings.request_client is None:
        from opsml.registry.sql.db_initializer import DBInitializer
        from opsml.registry.sql.base.server import ServerRegistry
        from opsml.registry.sql.sql_schema import RegistryTableNames

        db_initializer = DBInitializer(
            engine=settings.sql_engine,
            registry_tables=list(RegistryTableNames),
        )
        db_initializer.initialize()

        return db_initializer, ServerRegistry

    from opsml.registry.sql.base.client import ClientRegistry

    return None, ClientRegistry


initializer, OpsmlRegistry = get_registry()
