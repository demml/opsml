# pylint: disable=import-outside-toplevel
# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os
import shutil
import warnings
from pathlib import Path
from typing import BinaryIO, Iterator, List, Optional, cast

from fsspec import FSMap
from pyarrow.fs import LocalFileSystem

from opsml.helpers.logging import ArtifactLogger
from opsml.registry.storage.api import ApiClient, ApiRoutes
from opsml.registry.storage.types import (
    ApiStorageClientSettings,
    GcsStorageClientSettings,
    S3StorageClientSettings,
    StorageClientProtocol,
    StorageClientSettings,
    StorageSettings,
    StorageSystem,
    StoreLike,
)
from opsml.settings.config import OpsmlConfig, config

warnings.filterwarnings("ignore", message="Setuptools is replacing distutils.")
warnings.filterwarnings("ignore", message="Hint: Inferred schema contains integer*")

logger = ArtifactLogger.get_logger()


class StorageClientBase(StorageClientProtocol):
    def __init__(
        self,
        settings: StorageSettings,
        client: Optional[StorageClientProtocol] = None,
    ):
        if client is None:
            self.client = cast(StorageClientProtocol, LocalFileSystem())
        else:
            self.client = client
        self.settings = settings

    @property
    def base_path_prefix(self) -> str:
        return self.settings.storage_uri

    def build_absolute_path(self, rpath: str) -> str:
        return os.path.join(self.base_path_prefix, rpath)

    def build_relative_path(self, rpath: str) -> str:
        """Returns the relative path in relation to the storage root."""
        base_path = Path(self.base_path_prefix)
        rpath_path = Path(rpath)
        assert rpath_path.is_relative_to(base_path)
        return str(rpath_path.relative_to(base_path))

    @property
    def is_local(self) -> bool:
        return self.settings.storage_system == StorageSystem.LOCAL

    def get(self, rpath: str, lpath: str, recursive: bool = True) -> str:
        raise NotImplementedError

    def get_mapper(self, root: str) -> FSMap:
        raise NotImplementedError

    def ls(self, path: str) -> List[str]:
        raise NotImplementedError

    def open(self, path: str, mode: str, encoding: Optional[str] = None) -> BinaryIO:
        raise NotImplementedError

    def iterfile(self, path: str, chunk_size: int) -> Iterator[bytes]:
        with self.open(path, "rb") as file_:
            while chunk := file_.read(chunk_size):
                yield chunk

    def put(self, lpath: str, rpath: str, recursive: bool = True) -> str:
        raise NotImplementedError

    def copy(self, src: str, dest: str, recursive: bool = True) -> None:
        raise NotImplementedError

    def rm(self, path: str, recursive: bool = True) -> None:
        raise NotImplementedError


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

    def get(self, rpath: str, lpath: str, recursive: bool = True) -> str:
        # TODO(@damon): Test this - does the GCS client return a path in the file *and* directory cases?
        loadable_path = self.client.get(rpath=self.build_absolute_path(rpath), lpath=lpath, recursive=recursive)
        if loadable_path is None:
            return None

        if all(path is None for path in loadable_path):
            return os.path.join(lpath, os.path.basename(rpath))
        return loadable_path

    def get_mapper(self, root: str) -> StoreLike:
        return self.client.get_mapper(root)

    def ls(self, path: str) -> List[str]:
        # TODO(@damon): Test this
        return [path.replace(self.base_path_prefix, "").lstrip("/") for path in self.client.ls(path=path)]

    def open(self, path: str, mode: str, encoding: Optional[str] = None) -> BinaryIO:
        return self.client.open(path, mode=mode, encoding=encoding)

    def put(self, lpath: str, rpath: str, recursive: bool = True) -> str:
        return self.client.put(lpath, rpath, recursive)

    def copy(self, src: str, dest: str, recursive: bool = True) -> None:
        self.client.copy(src, dest, recursive)

    def rm(self, path: str, recursive: bool = True) -> None:
        self.client.rm(path, recursive)


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

    def get(self, rpath: str, lpath: str, recursive: bool = True) -> str:
        # TODO(@damon): Test this - does the GCS client return a path in the file *and* directory cases?
        loadable_path = self.client.get(rpath=self.build_absolute_path(rpath), lpath=lpath, recursive=recursive)
        if loadable_path is None:
            return None

        if all(path is None for path in loadable_path):
            return os.path.join(lpath, os.path.basename(rpath))
        return loadable_path

    def get_mapper(self, root: str) -> StoreLike:
        return self.client.get_mapper(root)

    def ls(self, path: str) -> List[str]:
        # TODO(@damon): Test this
        return [path.replace(self.base_path_prefix, "").lstrip("/") for path in self.client.ls(path=path)]

    def open(self, path: str, mode: str, encoding: Optional[str] = None) -> BinaryIO:
        return self.client.open(path, mode=mode, encoding=encoding)

    def put(self, lpath: str, rpath: str, recursive: bool = True) -> str:
        return self.client.put(lpath, rpath, recursive)

    def copy(self, src: str, dest: str, recursive: bool = True) -> None:
        self.client.copy(src, dest, recursive)

    def rm(self, path: str, recursive: bool = True) -> None:
        self.client.rm(path, recursive)


class LocalStorageClient(StorageClientBase):
    def get(self, rpath: str, lpath: str, recursive: bool = True) -> str:
        abs_remote_path = self.build_absolute_path(rpath)
        assert os.path.exists(abs_remote_path)

        if os.path.isdir(abs_remote_path):
            shutil.rmtree(lpath, ignore_errors=True)
            shutil.copytree(abs_remote_path, lpath)
        else:
            assert os.path.isfile(abs_remote_path)
            local_dir = Path(lpath).parent
            if not local_dir.exists():
                local_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy(abs_remote_path, lpath)
        return lpath

    def get_mapper(self, root: str) -> StoreLike:
        return root

    def ls(self, path: str) -> List[str]:
        abs_storage_uri = self.build_absolute_path(path)
        if not os.path.exists(abs_storage_uri):
            return []

        if not os.path.isdir(abs_storage_uri):
            return [path]

        files: List[str] = []
        for curr_path in Path(abs_storage_uri).rglob("*"):
            if not curr_path.is_dir():
                files.append(self.build_relative_path(str(curr_path)))
        return files

    def open(self, path: str, mode: str, encoding: Optional[str] = None) -> BinaryIO:
        return cast(BinaryIO, open(file=path, mode=mode, encoding=encoding))

    def put(self, lpath: str, rpath: str, recursive: bool = True) -> str:
        assert os.path.exists(lpath)

        abs_remote_path = self.build_absolute_path(rpath)

        if os.path.isdir(lpath):
            shutil.rmtree(abs_remote_path, ignore_errors=True)
            shutil.copytree(lpath, abs_remote_path)
        else:
            assert os.path.isfile(lpath)
            abs_remote_dir = Path(abs_remote_path).parent
            if not abs_remote_dir.exists():
                abs_remote_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy(lpath, abs_remote_path)

        return rpath

    def copy(self, src: str, dest: str, recursive: bool = True) -> None:
        """Both src and dest are remote paths."""
        self.put(self.build_absolute_path(src), dest, recursive)

    def rm(self, path: str, recursive: bool = True) -> None:
        # TODO(@damon) Remove the "recursive" parameter on rm for all clients.
        abs_path = self.build_absolute_path(path)
        if os.path.isdir(abs_path):
            shutil.rmtree(abs_path)
        elif os.path.isfile(abs_path):
            os.remove(abs_path)


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

    def get(self, rpath: str, lpath: str, recursive: bool = True) -> str:
        if recursive:
            for file in self.ls(rpath):
                rel_path = Path(file).relative_to(rpath)
                self.get(file, str(Path(lpath).joinpath(rel_path)), False)
            return lpath

        self.api_client.stream_download_file_request(
            route=ApiRoutes.DOWNLOAD_FILE,
            local_dir=str(Path(lpath).parent),
            read_dir=str(Path(rpath).parent),
            filename=Path(rpath).name,
        )
        return lpath

    def get_mapper(self, root: str) -> str:
        # TODO(@damon): Verify this
        return root

    def ls(self, path: str) -> List[str]:
        response = self.api_client.post_request(
            route=ApiRoutes.LIST_FILES,
            json={"read_path": path},
        )
        files = response.get("files")

        if files is not None:
            return cast(List[str], files)

        return []

    def put(self, lpath: str, rpath: str, recursive: bool = True) -> str:
        if recursive:
            write_path_path = Path(rpath)
            for path, _, localfiles in os.walk(lpath):
                for filename in localfiles:
                    curr_local_path = Path(path).joinpath(filename)
                    curr_write_path = write_path_path.joinpath(curr_local_path.relative_to(lpath))
                    self.put(str(curr_local_path), str(curr_write_path), False)
            return rpath

        files = {"file": open(lpath, "rb")}  # pylint: disable=consider-using-with
        headers = {"Filename": os.path.basename(rpath), "WritePath": os.path.dirname(rpath)}

        response = self.api_client.stream_post_request(
            route=ApiRoutes.UPLOAD,
            files=files,
            headers=headers,
        )
        storage_uri: Optional[str] = response.get("storage_uri")

        if storage_uri is not None:
            return storage_uri

        raise ValueError("No storage_uri found")

    def copy(self, src: str, dest: str, recursive: bool = True) -> None:
        raise NotImplementedError

    def open(self, path: str, mode: str, encoding: Optional[str] = None) -> BinaryIO:
        raise NotImplementedError

    def rm(self, path: str, recursive: bool = False) -> None:
        # TODO:(@damon): Implement recursive delete on the API client
        assert not recursive
        response = self.api_client.post_request(
            route=ApiRoutes.DELETE_FILE,
            json={"read_path": path},
        )

        if response.get("deleted") is False:
            raise ValueError("Failed to delete file")


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
    if "gs://" in cfg.opsml_storage_uri:
        return GCSFSStorageClient(_get_gcs_settings(storage_uri=cfg.opsml_storage_uri))
    if "s3://" in cfg.opsml_storage_uri:
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
