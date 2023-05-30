# pylint: disable=protected-access
from fastapi import APIRouter

from opsml.app.core.config import config
from opsml.app.routes.pydantic_models import StorageSettingsResponse
from opsml.helpers.logging import ArtifactLogger
from opsml.registry.storage.storage_system import StorageSystem

logger = ArtifactLogger.get_logger(__name__)

router = APIRouter()


@router.get("/settings", response_model=StorageSettingsResponse, name="settings")
def get_storage_settings() -> StorageSettingsResponse:
    """Returns backend storage path and type"""

    if bool(config.STORAGE_URI):
        if not config.is_proxy:
            if "gs://" in config.STORAGE_URI:
                return StorageSettingsResponse(
                    storage_type=StorageSystem.GCS.value,
                    storage_uri=config.STORAGE_URI,
                )

        # this should setup the api storage client
        if config.is_proxy:
            return StorageSettingsResponse(
                storage_type=StorageSystem.API.value,
                storage_uri=config.STORAGE_URI,
                proxy=config.is_proxy,
            )

    return StorageSettingsResponse(
        storage_type=StorageSystem.LOCAL.value,
        storage_uri=config.STORAGE_URI,
        proxy=config.is_proxy,
    )
