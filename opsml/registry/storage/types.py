# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
from __future__ import annotations

import os
from enum import Enum, unique
from typing import Any, List, Optional, Union

from pydantic import BaseModel, ConfigDict

FilePath = Union[List[str], str]


@unique
class StorageSystem(Enum):
    GCS = "gcs"
    S3 = "s3"
    LOCAL = "local"
    API = "api"


@unique
class ArtifactStorageType(str, Enum):
    BOOSTER = "booster"
    HTML = "html"
    IMAGE = "ImageDataset"
    JSON = "json"
    NUMPY = "numpy.ndarray"
    ONNX = "onnx"
    PANDAS = "pandas.core.frame.DataFrame"
    POLARS = "polars.dataframe.frame.DataFrame"
    PYARROW = "pyarrow"
    PYTORCH = "pytorch"
    TF_MODEL = "keras"
    TRANSFORMER = "transformer"
    UNKNOWN = "unknown"

    @staticmethod
    def from_str(value: str) -> Optional[ArtifactStorageType]:
        for elt in ArtifactStorageType:
            if value in elt.value:
                return elt
        return None


class StorageClientSettings(BaseModel):
    storage_system: StorageSystem = StorageSystem.LOCAL
    storage_uri: str = os.getcwd()


class GcsStorageClientSettings(StorageClientSettings):
    storage_system: StorageSystem = StorageSystem.GCS
    credentials: Optional[Any] = None
    gcp_project: Optional[str] = None


class S3StorageClientSettings(StorageClientSettings):
    storage_system: StorageSystem = StorageSystem.S3


class ApiStorageClientSettings(StorageClientSettings):
    model_config = ConfigDict(arbitrary_types_allowed=True, frozen=False)

    storage_system: StorageSystem = StorageSystem.API
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
