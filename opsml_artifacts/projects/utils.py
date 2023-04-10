# pylint: disable=invalid-envvar-value

from opsml_artifacts import CardRegistry
from opsml_artifacts.projects.types import CardRegistries
from opsml_artifacts.registry.storage.storage_system import (
    StorageClientType,
)


def get_card_registries(storage_client: StorageClientType):

    """Gets CardRegistries to associate with MlFlow experiment"""
    registries = CardRegistries(
        datacard=CardRegistry(registry_name="data"),
        modelcard=CardRegistry(registry_name="model"),
        RunCard=CardRegistry(registry_name="run"),
    )

    # double check
    registries.set_storage_client(storage_client=storage_client)

    return registries
