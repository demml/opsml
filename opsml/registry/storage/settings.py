# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from opsml.helpers.logging import ArtifactLogger
from opsml.registry.storage.storage_system import (
    StorageClientType,
    StorageSystem,
    get_storage_client,
)
from opsml.registry.storage.types import (
    ApiStorageClientSettings,
    GcsStorageClientSettings,
    S3StorageClientSettings,
    StorageClientSettings,
    StorageSettings,
)
from opsml.settings.config import OpsmlConfig, config

logger = ArtifactLogger.get_logger()


class _DefaultAttrCreator:
    @staticmethod
    def get_storage_settings(cfg: OpsmlConfig) -> StorageSettings:
        if "gs://" in cfg.opsml_storage_uri:
            return _DefaultAttrCreator._get_gcs_settings(cfg.opsml_storage_uri)
        if "s3://" in cfg.opsml_storage_uri:
            return S3StorageClientSettings(
                storage_type=StorageSystem.S3.value,
                storage_uri=cfg.opsml_storage_uri,
            )
        return StorageClientSettings(
            storage_type=StorageSystem.LOCAL.value,
            storage_uri=cfg.opsml_storage_uri,
        )

    @staticmethod
    def _get_gcs_settings(storage_uri: str) -> GcsStorageClientSettings:
        from opsml.helpers.gcp_utils import (  # pylint: disable=import-outside-toplevel
            GcpCredsSetter,
        )

        gcp_creds = GcpCredsSetter().get_creds()

        return GcsStorageClientSettings(
            storage_type=StorageSystem.GCS.value,
            storage_uri=storage_uri,
            gcp_project=gcp_creds.project,
            credentials=gcp_creds.creds,
        )


class DefaultSettings:
    """Opsml settings"""

    def __init__(self, cfg: OpsmlConfig) -> None:
        self.cfg = cfg

        if not self.cfg.is_tracking_local:
            self._storage_settings: StorageSettings = ApiStorageClientSettings(
                storage_type=StorageSystem.API.value,
                storage_uri=cfg.opsml_storage_uri,
                opsml_tracking_uri=cfg.opsml_tracking_uri,
                opsml_username=cfg.opsml_username,
                opsml_password=cfg.opsml_password,
                opsml_prod_token=cfg.opsml_prod_token,
            )
        else:
            self._storage_settings = _DefaultAttrCreator.get_storage_settings(self.cfg)
        self._storage_client = get_storage_client(self.storage_settings)

    @property
    def storage_settings(self) -> StorageSettings:
        # TODO(@damon): Remove access to underlying storage settings. All
        # interaction to storage should be done thru the client only.
        return self._storage_settings

    @property
    def storage_client(self) -> StorageClientType:
        return self._storage_client


settings = DefaultSettings(cfg=config)
