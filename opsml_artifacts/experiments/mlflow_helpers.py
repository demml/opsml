from typing import cast

from pydantic import BaseModel

from opsml_artifacts import CardRegistry
from opsml_artifacts.helpers.logging import ArtifactLogger
from opsml_artifacts.helpers.settings import settings
from opsml_artifacts.registry.storage.storage_system import (
    MlFlowStorageClient,
    StorageClientGetter,
    StorageClientType,
    StorageSystem,
)
from opsml_artifacts.registry.storage.types import StorageClientSettings

logger = ArtifactLogger.get_logger(__name__)


class CardRegistries(BaseModel):
    datacard: CardRegistry
    modelcard: CardRegistry
    experimentcard: CardRegistry

    class Config:
        arbitrary_types_allowed = True
        allow_mutation = True

    def set_storage_client(self, storage_client: StorageClientType):
        self.datacard.registry.storage_client = storage_client
        self.modelcard.registry.storage_client = storage_client
        self.experimentcard.registry.storage_client = storage_client


def get_mlflow_storage_client() -> MlFlowStorageClient:
    """Sets MlFlowStorageClient is it is not currently set in settings"""

    if not isinstance(settings.storage_client, MlFlowStorageClient):
        return cast(
            MlFlowStorageClient,
            StorageClientGetter.get_storage_client(
                storage_settings=StorageClientSettings(storage_type=StorageSystem.MLFLOW.value),
            ),
        )
    return cast(MlFlowStorageClient, settings.storage_client)


mlflow_storage_client = get_mlflow_storage_client()
