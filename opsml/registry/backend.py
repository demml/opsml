# pylint: disable=protected-access
# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import Type

from opsml.registry.sql.base.registry_base import SQLRegistryBase
from opsml.settings.config import config
from opsml.storage import client
from opsml.types import RegistryType


def _set_registry(registry_type: RegistryType) -> SQLRegistryBase:
    """Sets the underlying registry.

    IMPORTANT: We need to delay importing ServerRegistry until we know we
    need it. Since opsml can run in both "server" mode (where tracking is
    local) which requires sqlalchemy and "client" mode which does not, we
    only want to import ServerRegistry when we know we need it.
    """
    sql_registry_type: Type[SQLRegistryBase]
    if config.is_tracking_local:
        from opsml.registry.sql.base.server import ServerRegistry

        sql_registry_type = ServerRegistry
    else:
        from opsml.registry.sql.base.client import ClientRegistry

        sql_registry_type = ClientRegistry

    registry = next(
        registry
        for registry in sql_registry_type.__subclasses__()
        if registry.validate(
            registry_name=registry_type.value,
        )
    )
    return registry(
        registry_type=registry_type,
        storage_client=client.storage_client,
    )
