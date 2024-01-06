# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from functools import cached_property
from pathlib import Path
from typing import Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings

from opsml.types import StorageSystem


class OpsmlConfig(BaseSettings):
    app_name: str = "opsml"
    app_env: str = Field(default="development")

    opsml_storage_uri: str = "./mlruns"
    opsml_tracking_uri: str = "sqlite:///tmp.db"
    opsml_prod_token: str = "staging"
    opsml_proxy_root: str = "opsml-root:/"

    # API client username / password
    opsml_username: Optional[str] = None
    opsml_password: Optional[str] = None

    # The current RUN_ID to load when creating a new project
    opsml_run_id: Optional[str] = None

    @field_validator("opsml_storage_uri", mode="after")
    @classmethod
    def set_opsml_storage_uri(cls, opsml_storage_uri: str) -> str:
        """Opsml uses storage cients that follow fsspec guidelines. LocalFileSytem only deals
        in absolutes, so we need to convert relative paths to absolute paths.
        """
        if not opsml_storage_uri.startswith("gs://") or not opsml_storage_uri.startswith("s3://"):
            return Path(opsml_storage_uri).absolute().as_posix()

        return opsml_storage_uri

    @property
    def is_tracking_local(self) -> bool:
        """Used to determine if an API client will be used.

        If tracking is local, the [server] extra is required.
        """
        return not self.opsml_tracking_uri.lower().strip().startswith("http")

    @cached_property
    def storage_system(self) -> StorageSystem:
        """Returns the storage system used for the current tracking URI"""
        if self.is_tracking_local:
            if self.opsml_storage_uri.startswith("gs://"):
                return StorageSystem.GCS
            if self.opsml_storage_uri.startswith("s3://"):
                return StorageSystem.S3
            return StorageSystem.LOCAL
        return StorageSystem.API

    @cached_property
    def storage_root(self) -> str:
        """Returns the root of the storage URI"""
        if self.is_tracking_local:
            return self.opsml_storage_uri
        return self.opsml_proxy_root


config = OpsmlConfig()
