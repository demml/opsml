# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
from __future__ import annotations

import os
from enum import Enum, unique
from typing import Any, BinaryIO, Iterator, List, Optional, Protocol, Union

from fsspec import FSMap
from pydantic import BaseModel, ConfigDict

FilePath = Union[List[str], str]
StoreLike = Union[FSMap, str]


@unique
class StorageSystem(Enum):
    GCS = "gcs"
    S3 = "s3"
    LOCAL = "local"
    API = "api"


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


class StorageClientProtocol(Protocol):
    @property
    def base_path_prefix(self) -> str:
        """The root storage prefix. Used when absolute storage paths are required."""

    def get(self, rpath: str, lpath: str, recursive: bool = True) -> str:
        """Copies file(s) from remote path (rpath) to local path (lpath)"""

    def get_mapper(self, root: str) -> StoreLike:
        """Creates a key/value store based on the file system"""

    def ls(self, path: str) -> List[str]:  # pylint:  disable=invalid-name
        """Lists files"""

    def open(self, path: str, mode: str, encoding: Optional[str] = None) -> BinaryIO:
        """Open a file"""

    def iterfile(self, path: str, chunk_size: int) -> Iterator[bytes]:
        """Open an iterator"""

    def put(self, lpath: str, rpath: str) -> str:
        """Copies file(s) from local path (lpath) to remote path (rpath)"""

    def copy(self, src: str, dest: str, recursive: bool = True) -> None:
        """Copies files from src to dest within the file system"""

    def rm(self, path: str) -> None:  # pylint: disable=invalid-name
        """Deletes file(s)"""

    def exists(self, path: str) -> bool:
        "Determine if a file or directory exists"
