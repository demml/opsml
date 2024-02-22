# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
from __future__ import annotations

import os
from enum import Enum, unique
from pathlib import Path
from typing import Any, BinaryIO, Iterator, List, Optional, Protocol, Union

from pydantic import BaseModel, ConfigDict

FilePath = Union[List[str], str]


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
    default_creds: bool = False


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


class BotoClient(Protocol):
    def generate_presigned_url(self, operation_name: str, Params: dict, ExpiresIn: int) -> str:
        ...


class Blob(Protocol):
    def generate_signed_url(self, version="v4", expiration: int = 600) -> str:
        ...


class Bucket(Protocol):
    def blob(self, name: str) -> Blob:
        ...


class GCSClient(Protocol):
    def bucket(self, name: str) -> Bucket:
        return Bucket()


class StorageClientProtocol(Protocol):
    def get(self, rpath: Path, lpath: Path) -> None:
        """Copies file(s) from remote path (rpath) to local path (lpath)"""

    def ls(self, path: Path) -> List[Path]:  # pylint:  disable=invalid-name
        """Lists files in directory (not recursive)"""

    def find(self, path: Path) -> List[Path]:
        """Lists all files in directory (recursive)"""

    def open(self, path: Path, mode: str, encoding: Optional[str] = None) -> BinaryIO:
        """Open a file"""

    def iterfile(self, path: Path, chunk_size: int) -> Iterator[bytes]:
        """Open an iterator"""

    def put(self, lpath: Path, rpath: Path) -> None:
        """Copies file(s) from local path (lpath) to remote path (rpath)"""

    def copy(self, src: Path, dest: Path) -> None:
        """Copies files from src to dest within the file system"""

    def rm(self, path: Path) -> None:  # pylint: disable=invalid-name
        """Deletes file(s)"""

    def exists(self, path: Path) -> bool:
        "Determine if a file or directory exists"
