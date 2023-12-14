# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
from typing import Optional

import httpx

from opsml.helpers.logging import ArtifactLogger
from opsml.helpers.request_helpers import ApiClient
from opsml.registry.storage.storage_system import StorageSystem, get_storage_client
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
    def get_request_client(cfg: OpsmlConfig) -> Optional[ApiClient]:
        if cfg.is_tracking_local:
            return None

        username = cfg.opsml_username
        password = cfg.opsml_password

        request_client = ApiClient(cfg=cfg, base_url="")
        if all(bool(cred) for cred in [username, password]):
            request_client.client.auth = httpx.BasicAuth(
                username=str(username),
                password=str(password),
            )
        return request_client

    @staticmethod
    def get_storage_settings(cfg: OpsmlConfig, client: Optional[ApiClient]) -> StorageSettings:
        if client is not None:
            return ApiStorageClientSettings(
                storage_type=StorageSystem.API.value,
                storage_uri=cfg.opsml_storage_uri,
                api_client=client,
            )
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

        self.request_client = _DefaultAttrCreator.get_request_client(self.cfg)
        self.storage_settings = _DefaultAttrCreator.get_storage_settings(self.cfg, self.request_client)

    @property
    def storage_settings(self) -> StorageSettings:
        return self._storage_settings

    @storage_settings.setter
    def storage_settings(self, storage_settings: StorageSettings) -> None:
        self._storage_settings = storage_settings
        self.storage_client = get_storage_client(self._storage_settings)


settings = DefaultSettings(cfg=config)
