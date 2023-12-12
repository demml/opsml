# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os
from enum import Enum
from typing import Any, List, Optional, Union

from pydantic import BaseModel, ConfigDict

from opsml.helpers.request_helpers import ApiClient
from opsml.registry.data.types import AllowedDataType

FilePath = Union[List[str], str]


class ArtifactStorageType(str, Enum):
    HTML = "html"
    TF_MODEL = "keras"
    PYTORCH = "pytorch"
    JSON = "json"
    BOOSTER = "booster"
    ONNX = "onnx"
    TRANSFORMER = "transformer"


ARTIFACT_TYPES = [
    *list(ArtifactStorageType),
    *[
        AllowedDataType.NUMPY,
        AllowedDataType.PANDAS,
        AllowedDataType.POLARS,
        AllowedDataType.IMAGE,
        AllowedDataType.PYARROW,
    ],
]


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

    client: Optional[ApiClient] = None

    @property
    def api_client(self) -> ApiClient:
        if self.client is not None:
            return self.client
        raise ValueError("ApiClient has not been set")


StorageSettings = Union[
    StorageClientSettings,
    GcsStorageClientSettings,
    ApiStorageClientSettings,
    S3StorageClientSettings,
]


class ArtifactStorageSpecs(BaseModel):
    model_config = ConfigDict(extra="allow", frozen=False)

    save_path: str
    filename: Optional[str] = None
