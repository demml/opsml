# pylint: disable=import-outside-toplevel
# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.


import warnings
from pathlib import Path
from typing import BinaryIO, Iterator, List, Optional, Protocol, cast

from fsspec.implementations.local import LocalFileSystem
from torch import NoneType

from opsml.helpers.logging import ArtifactLogger
from opsml.registry.storage.api import ApiClient, ApiRoutes
from opsml.registry.types import (
    ApiStorageClientSettings,
    GcsStorageClientSettings,
    S3StorageClientSettings,
    StorageClientProtocol,
    StorageClientSettings,
    StorageSettings,
    StoreLike,
)
from opsml.settings.config import OpsmlConfig, config

warnings.filterwarnings("ignore", message="Setuptools is replacing distutils.")
warnings.filterwarnings("ignore", message="Hint: Inferred schema contains integer*")

logger = ArtifactLogger.get_logger()


class FileSystemProtocol(Protocol):
    def get(self, lpath: str, rpath: str, recursive: bool = True) -> str:
        """Copies file(s) from remote path (rpath) to local path (lpath)"""

    def get_mapper(self, root: str) -> StoreLike:
        """Creates a key/value store based on the file system"""

    def ls(self, path: str) -> List[str]:  # pylint:  disable=invalid-name
        """Lists files"""

    def find(self, path: str) -> List[str]:
        """Recursively list all files excluding directories"""

    def open(self, path: str, mode: str, encoding: Optional[str] = None) -> BinaryIO:
        """Open a file"""

    def iterfile(self, path: str, chunk_size: int) -> Iterator[bytes]:
        """Open an iterator"""

    def put(self, lpath: str, rpath: str, recursive: bool) -> str:
        """Copies file(s) from local path (lpath) to remote path (rpath)"""

    def copy(self, src: str, dest: str, recursive: bool = True) -> None:
        """Copies files from src to dest within the file system"""

    def rm(self, path: str, recursive: bool) -> None:  # pylint: disable=invalid-name
        """Deletes file(s)"""

    def exists(self, rpath: str) -> bool:
        """Determines if a file or directory exists"""


class StorageClientBase(StorageClientProtocol):
    def __init__(
        self,
        settings: StorageSettings,
        client: Optional[FileSystemProtocol] = None,
    ):
        if client is None:
            self.client = cast(FileSystemProtocol, LocalFileSystem())
        else:
            self.client = client
        self.settings = settings

    def get(self, rpath: Path, lpath: Path, recursive: bool = True) -> NoneType:
        # handle rpath
        if rpath.suffix:
            recursive = False
            abs_rpath = str(rpath)
        else:
            abs_rpath = f"{str(rpath)}/"

        # handle lpath
        if lpath.suffix:
            abs_lpath = f"{str(lpath.parent)}/"
        else:
            abs_lpath = f"{str(lpath)}/"

        self.client.get(rpath=abs_rpath, lpath=abs_lpath, recursive=recursive)

    def get_mapper(self, root: str) -> StoreLike:
        return self.client.get_mapper(root)

    def ls(self, path: Path) -> List[str]:
        return self.client.ls(str(path))

    def find(self, path: Path) -> List[str]:
        return self.client.find(str(path))

    def open(self, path: Path, mode: str, encoding: Optional[str] = None) -> BinaryIO:
        return self.client.open(str(path), mode=mode, encoding=encoding)

    def iterfile(self, path: Path, chunk_size: int) -> Iterator[bytes]:
        with self.open(str(path), "rb") as file_:
            while chunk := file_.read(chunk_size):
                yield chunk

    def put(self, lpath: Path, rpath: Path) -> None:
        # mocking clients will *not* persist the path to the FS
        # assert os.path.exists(lpath)
        if lpath.is_dir():
            abs_lpath = f"{str(lpath)}/"  # pathlib strips trailing slashes
            abs_rpath = f"{str(rpath)}/"
            # logger.info("Putting directory: {} rpath: {}", abs_lpath, abs_rpath)
            self.client.put(abs_lpath, abs_rpath, True)
        else:
            # logger.info("Putting file: {} rpath: {}", lpath, rpath)
            self.client.put(str(lpath), str(rpath), False)

    def copy(self, src: Path, dest: Path, recursive: bool = True) -> None:
        self.client.copy(str(src), str(dest), recursive)

    def rm(self, path: Path) -> None:
        self.client.rm(str(path), True)

    def exists(self, path: Path) -> bool:
        return self.client.exists(path=str(path))


class GCSFSStorageClient(StorageClientBase):
    def __init__(
        self,
        settings: StorageSettings,
    ):
        import gcsfs

        assert isinstance(settings, GcsStorageClientSettings)
        if settings.credentials is None:
            client = gcsfs.GCSFileSystem()
        else:
            client = gcsfs.GCSFileSystem(
                project=settings.gcp_project,
                token=settings.credentials,
            )

        super().__init__(
            settings=settings,
            client=client,
        )


class S3StorageClient(StorageClientBase):
    def __init__(
        self,
        settings: StorageSettings,
    ):
        import s3fs

        assert isinstance(settings, S3StorageClientSettings)
        client = s3fs.S3FileSystem()

        super().__init__(
            settings=settings,
            client=client,
        )


class LocalStorageClient(StorageClientBase):
    def put(self, lpath: Path, rpath: Path) -> None:
        if rpath.suffix:
            rpath.parent.mkdir(parents=True, exist_ok=True)
        else:
            rpath.mkdir(parents=True, exist_ok=True)

        super().put(lpath, rpath)


class ApiStorageClient(StorageClientBase):
    def __init__(self, settings: StorageSettings):
        assert isinstance(settings, ApiStorageClientSettings)
        super().__init__(
            settings=settings,
        )

        self.api_client = ApiClient(
            base_url=settings.opsml_tracking_uri,
            username=settings.opsml_username,
            password=settings.opsml_password,
            token=settings.opsml_prod_token,
        )

    def get(self, rpath: Path, lpath: Path, recursive: bool = True) -> None:
        """Copies file(s) from remote path (rpath) to local path (lpath)"""

        # print(self.find(rpath))
        for file in self.find(rpath):
            _rpath = Path(file)

            # for single files
            if _rpath.name == lpath.name:
                _lpath = lpath

            # for files in nested dirs
            else:
                index = _rpath.parts.index(lpath.name)
                _lpath = lpath.joinpath(*_rpath.parts[index + 1 :])

            self.api_client.stream_download_file_request(
                route=ApiRoutes.DOWNLOAD_FILE,
                local_dir=_lpath.parent,
                read_dir=_rpath.parent,
                filename=_rpath.name,
            )

    def find(self, path: Path) -> List[str]:
        response = self.api_client.get_request(
            route=ApiRoutes.LIST_FILES,
            params={"path": path},
        )

        # storage clients always return a list
        files: List[str] = response["files"]

        return files

    def put(self, lpath: Path, rpath: Path) -> None:
        # this will iterate through all dirs and files
        for curr_lpath in lpath.rglob("*"):
            if curr_lpath.is_file():
                curr_rpath = rpath / curr_lpath.relative_to(lpath)

                response = self.api_client.stream_post_request(
                    route=ApiRoutes.UPLOAD_FILE,
                    files={"file": open(curr_lpath.as_posix(), "rb")},
                    headers={"write_path": curr_rpath.as_posix()},
                )
                storage_uri: Optional[str] = response.get("storage_uri")

                if storage_uri is None:
                    raise ValueError("Failed to write file to storage")

    def copy(self, src: str, dest: str, recursive: bool = True) -> None:
        raise NotImplementedError

    def open(self, path: str, mode: str, encoding: Optional[str] = None) -> BinaryIO:
        raise NotImplementedError

    def rm(self, path: Path) -> None:
        route = Path(ApiRoutes.DELETE_FILE, path)
        response = self.api_client.get_request(route=route.as_posix())

        if response.get("deleted") is False:
            raise ValueError("Failed to delete file")

    def exists(self, path: Path) -> bool:
        """Checks if file exists on server

        Args:
            path:
                Path to file
        """

        response = self.api_client.get_request(
            route=ApiRoutes.FILE_EXISTS,
            params={"path": path.as_posix()},
        )

        return response.get("exists", False)


def _get_gcs_settings(storage_uri: str) -> GcsStorageClientSettings:
    from opsml.helpers.gcp_utils import GcpCredsSetter

    gcp_creds = GcpCredsSetter().get_creds()

    return GcsStorageClientSettings(
        storage_uri=storage_uri,
        gcp_project=gcp_creds.project,
        credentials=gcp_creds.creds,
    )


def get_storage_client(cfg: OpsmlConfig) -> StorageClientBase:
    if not cfg.is_tracking_local:
        return ApiStorageClient(
            ApiStorageClientSettings(
                storage_uri=cfg.opsml_storage_uri,
                opsml_tracking_uri=cfg.opsml_tracking_uri,
                opsml_username=cfg.opsml_username,
                opsml_password=cfg.opsml_password,
                opsml_prod_token=cfg.opsml_prod_token,
            )
        )
    if cfg.opsml_storage_uri.startswith("gs://"):
        return GCSFSStorageClient(_get_gcs_settings(storage_uri=cfg.opsml_storage_uri))
    if cfg.opsml_storage_uri.startswith("s3://"):
        return S3StorageClient(S3StorageClientSettings(storage_uri=cfg.opsml_storage_uri))

    return LocalStorageClient(StorageClientSettings(storage_uri=cfg.opsml_storage_uri))


# The global storage client. When importing from this module, be sure to import
# the *module* rather than storage_client itself to simplify mocking. Tests will
# mock the global storage client.
#
# i.e., use:
# from opsml.registry.storage import client
#
# do_something(client.storage_client)
#
# do *not* use:
# from opsml.registry.storage.client import storage_client
#
# do_something(storage_client)
storage_client = get_storage_client(config)


StorageClient = StorageClientBase
