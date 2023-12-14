# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
from fastapi import APIRouter

from opsml import version
from opsml.app.routes.pydantic_models import StorageSettingsResponse
from opsml.helpers.logging import ArtifactLogger
from opsml.registry.storage.storage_system import StorageSystem
from opsml.settings.config import config

logger = ArtifactLogger.get_logger()

router = APIRouter()


# TODO(@damon): This should *not* be here. The API client should *not* know (or
# care) where the server is storing data.
@router.get("/settings", response_model=StorageSettingsResponse, name="settings")
def get_storage_settings() -> StorageSettingsResponse:
    """Returns backend storage path and type"""

    storage_type = StorageSystem.LOCAL.value
    if bool(config.opsml_storage_uri):
        if config.is_tracking_local and "gs://" in str(config.opsml_storage_uri):
            storage_type = StorageSystem.GCS.value

        if config.is_tracking_local and "s3://" in str(config.opsml_storage_uri):
            storage_type = StorageSystem.S3.value

        if not config.is_tracking_local:
            # this should setup the api storage client
            storage_type = StorageSystem.API.value

    return StorageSettingsResponse(
        storage_type=storage_type,
        storage_uri=config.opsml_storage_uri,
        version=version.__version__,
    )
