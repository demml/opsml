# pylint: disable=protected-access
# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
from fastapi import APIRouter

from opsml import version
from opsml.app.core.config import config
from opsml.app.routes.pydantic_models import StorageSettingsResponse
from opsml.helpers.logging import ArtifactLogger
from opsml.registry.storage.storage_system import StorageSystem

logger = ArtifactLogger.get_logger()

router = APIRouter()


@router.get("/settings", response_model=StorageSettingsResponse, name="settings")
def get_storage_settings() -> StorageSettingsResponse:
    """Returns backend storage path and type"""

    storage_type = StorageSystem.LOCAL.value
    if bool(config.STORAGE_URI):
        if not config.is_proxy and "gs://" in config.STORAGE_URI:
            storage_type = StorageSystem.GCS.value
        if config.is_proxy:
            # this should setup the api storage client
            storage_type = StorageSystem.API.value

    return StorageSettingsResponse(
        storage_type=storage_type,
        storage_uri=config.STORAGE_URI,
        proxy=config.is_proxy,
        version=version.__version__,
    )
