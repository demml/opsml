# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os
from enum import Enum, unique
from typing import Any, List, Optional, Union

from pydantic import BaseModel, ConfigDict

FilePath = Union[List[str], str]

_OPSML_STORAGE_ROOT = "opsml://"


class StorageClientSettings(BaseModel):
    storage_type: str = "local"
    storage_uri: str = os.getcwd()


class GcsStorageClientSettings(StorageClientSettings):
    storage_type: str = "gcs"
    credentials: Optional[Any] = None
    gcp_project: Optional[str] = None


class S3StorageClientSettings(StorageClientSettings):
    storage_type: str = "s3"


class ApiStorageClientSettings(StorageClientSettings):
    model_config = ConfigDict(arbitrary_types_allowed=True, frozen=False)
    opsml_tracking_uri: str
    opsml_username: Optional[str]
    opsml_password: Optional[str]
    opsml_prod_token: Optional[str]


StorageSettings = Union[
    StorageClientSettings,
    GcsStorageClientSettings,
    ApiStorageClientSettings,
    S3StorageClientSettings,
]


class StorageRequest(BaseModel):
    registry_type: str
    card_uid: str
    uri_name: str
    uri_path: Optional[str] = None
    filename: Optional[str] = None


@unique
class StorageSystem(str, Enum):
    GCS = "gcs"
    S3 = "s3"
    LOCAL = "local"
    API = "api"
