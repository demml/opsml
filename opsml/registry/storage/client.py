# pylint: disable=import-outside-toplevel
# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os
import shutil
import tempfile
import warnings
from contextlib import contextmanager
from pathlib import Path
from typing import (
    Any,
    BinaryIO,
    Generator,
    Iterator,
    List,
    Optional,
    Protocol,
    Union,
    cast,
)

from pyarrow.fs import LocalFileSystem

from opsml.helpers.logging import ArtifactLogger
from opsml.helpers.utils import all_subclasses
from opsml.registry.storage.api import ApiClient, ApiRoutes
from opsml.registry.storage.types import (
    ApiStorageClientSettings,
    GcsStorageClientSettings,
    S3StorageClientSettings,
    StorageClientSettings,
    StorageSettings,
    StorageSystem,
)
from opsml.settings.config import OpsmlConfig, config

warnings.filterwarnings("ignore", message="Setuptools is replacing distutils.")
warnings.filterwarnings("ignore", message="Hint: Inferred schema contains integer*")

logger = ArtifactLogger.get_logger()


class FileSystemClient(Protocol):
    def download(self, lpath: str, rpath: str, recursive: bool) -> Optional[str]:
        ...

    def upload(self, lpath: str, rpath: str, recursive: bool) -> str:
        ...

    def copy(self, read_path: str, write_path: str, recursive: bool) -> None:
        ...

    def rm(self, path: str, recursive: bool) -> None:  # pylint: disable=invalid-name
        ...

    def open(self, filename: str, mode: str) -> BinaryIO:
        ...

    def ls(self, path: str) -> List[str]:  # pylint:  disable=invalid-name
        ...

    def delete_dir(self, path: str) -> None:
        ...

    def delete_file(self, path: str) -> None:
        ...


class StorageClient:
    def __init__(
        self,
        settings: StorageSettings,
        client: Optional[FileSystemClient] = None,
    ):
        if client is None:
            self.client = cast(FileSystemClient, LocalFileSystem())
        else:
            self.client = client
        self.settings = settings
        self.base_path_prefix = settings.storage_uri

    @property
    def is_local(self) -> bool:
        return self.settings.storage_system == StorageSystem.LOCAL

    @contextmanager
    def create_tmp_path(
        self,
        path: str,
    ) -> Generator[str, None, None]:
        """Generates a temporary path for a given ArtifactStorageSpec."""
        with tempfile.TemporaryDirectory() as tmpdirname:
            yield os.path.join(tmpdirname, os.path.basename(path))

    def list_files(self, storage_uri: str) -> List[str]:
        raise NotImplementedError

    def store(self, storage_uri: str, **kwargs: Any) -> Any:
        raise NotImplementedError

    def open(self, filename: str, mode: str) -> BinaryIO:
        raise NotImplementedError

    def iterfile(self, file_path: str, chunk_size: int) -> Iterator[bytes]:
        with self.open(file_path, "rb") as file_:
            while chunk := file_.read(chunk_size):
                yield chunk

    def build_absolute_path(self, rpath: str) -> str:
        return os.path.join(self.base_path_prefix, rpath)

    def build_relative_path(self, rpath: str) -> str:
        """Returns the relative path in relation to the storage root."""
        base_path = Path(self.base_path_prefix)
        rpath_path = Path(rpath)

        assert rpath_path.is_relative_to(base_path)

        return str(rpath_path.relative_to(base_path))

    def download(self, rpath: str, lpath: str, recursive: bool = False, **kwargs: Any) -> Optional[str]:
        return self.client.download(rpath=self.build_absolute_path(rpath), lpath=lpath, recursive=recursive)

    def upload(
        self,
        local_path: str,
        write_path: str,
        recursive: bool = False,
        **kwargs: Any,
    ) -> str:
        return self.client.upload(lpath=local_path, rpath=self.build_absolute_path(write_path), recursive=recursive)

    def copy(self, read_path: str, write_path: str) -> None:
        raise ValueError("Storage class does not implement a copy method")

    def delete(self, read_path: str) -> None:
        raise ValueError("Storage class does not implement a delete method")

    @staticmethod
    def validate(storage_system: StorageSystem) -> bool:
        raise NotImplementedError


class GCSFSStorageClient(StorageClient):
    def __init__(
        self,
        settings: StorageSettings,
    ):
        import gcsfs

        assert isinstance(settings, GcsStorageClientSettings)
        client = gcsfs.GCSFileSystem(
            project=settings.gcp_project,
            token=settings.credentials,
        )

        super().__init__(
            settings=settings,
            client=client,
        )

    def copy(self, read_path: str, write_path: str) -> None:
        """Copies object from read_path to write_path

        Args:
            read_path:
                Path to read from
            write_path:
                Path to write to
        """
        self.client.copy(read_path, self.build_absolute_path(write_path), recursive=True)

    def delete(self, read_path: str) -> None:
        """Deletes files from a read path

        Args:
            read_path:
                Path to delete
        """
        self.client.rm(path=self.build_absolute_path(read_path), recursive=True)

    def open(self, filename: str, mode: str) -> BinaryIO:
        return self.client.open(filename, mode)

    def list_files(self, storage_uri: str) -> List[str]:
        return [path.replace(self.base_path_prefix, "").lstrip("/") for path in self.client.ls(path=str(storage_uri))]

    def store(self, storage_uri: str, **kwargs: Any) -> Any:
        """Create store for use with Zarr arrays"""
        import gcsfs

        return gcsfs.GCSMap(storage_uri, gcs=self.client, check=False)

    def download(self, rpath: str, lpath: str, recursive: bool = False, **kwargs: Any) -> Optional[str]:
        loadable_path = self.client.download(rpath=self.build_absolute_path(rpath), lpath=lpath, recursive=recursive)
        if loadable_path is None:
            return None

        if all(path is None for path in loadable_path):
            return os.path.join(lpath, os.path.basename(rpath))
        return loadable_path

    @staticmethod
    def validate(storage_system: StorageSystem) -> bool:
        return storage_system == StorageSystem.GCS


# TODO(@damon): Remote path S3
class S3StorageClient(StorageClient):
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

    def copy(self, read_path: str, write_path: str) -> None:
        """Copies object from read_path to write_path

        Args:
            read_path:
                Path to read from
            write_path:
                Path to write to
        """
        self.client.copy(read_path, write_path, recursive=True)

    def delete(self, read_path: str) -> None:
        """Deletes files from a read path

        Args:
            read_path:
                Path to delete
        """
        self.client.rm(path=read_path, recursive=True)

    def open(self, filename: str, mode: str) -> BinaryIO:
        return self.client.open(filename, mode)

    def list_files(self, storage_uri: str) -> List[str]:
        # TODO(@damon): Strip the root prefix
        return [f"s3://{path}" for path in self.client.ls(path=str(storage_uri))]

    def store(self, storage_uri: str, **kwargs: Any) -> Any:
        """Create store for use with Zarr arrays"""
        import s3fs

        return s3fs.S3Map(storage_uri, s3=self.client, check=False)

    def download(self, rpath: str, lpath: str, recursive: bool = False, **kwargs: Any) -> Optional[str]:
        loadable_path = self.client.download(rpath=rpath, lpath=lpath, recursive=recursive)
        if loadable_path is None:
            return None

        if all(path is None for path in loadable_path):
            return os.path.join(lpath, os.path.basename(rpath))
        return loadable_path

    @staticmethod
    def validate(storage_system: StorageSystem) -> bool:
        return storage_system == StorageSystem.S3


class LocalStorageClient(StorageClient):
    def upload(self, local_path: str, write_path: str, recursive: bool = False, **kwargs: Any) -> str:
        """Uploads (copies) local_path to write_path

        Args:
            local_path:
                local path to upload
            write_path:
                path to write to
            recursive:
                whether to recursively upload files
            kwargs:
                additional arguments to pass to upload function

        Returns:
            write_path
        """

        abs_write_path = self.build_absolute_path(write_path)
        if os.path.isdir(local_path):
            Path(local_path).mkdir(parents=True, exist_ok=True)
            shutil.rmtree(abs_write_path, ignore_errors=True)
            shutil.copytree(local_path, abs_write_path)
        else:
            abs_write_dir = Path(abs_write_path).parent
            if not abs_write_dir.exists():
                abs_write_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy(local_path, abs_write_path)

        return write_path

    def list_files(self, storage_uri: str) -> List[str]:
        abs_storage_uri = self.build_absolute_path(storage_uri)
        if not os.path.exists(abs_storage_uri):
            return []

        if not os.path.isdir(abs_storage_uri):
            return [storage_uri]

        files: List[str] = []
        for curr_path in Path(abs_storage_uri).rglob("*"):
            if not curr_path.is_dir():
                files.append(self.build_relative_path(str(curr_path)))
        return files

    def open(self, filename: str, mode: str, encoding: Optional[str] = None) -> BinaryIO:
        return cast(BinaryIO, open(file=filename, mode=mode, encoding=encoding))

    def store(self, storage_uri: str, **kwargs: Any) -> str:
        return storage_uri

    def copy(self, read_path: str, write_path: str) -> None:
        """Copies object from read_path to write_path

        Args:
            read_path:
                Path to read from
            write_path:
                Path to write to
        """
        abs_read_path = self.build_absolute_path(read_path)
        if os.path.isdir(abs_read_path):
            shutil.copytree(abs_read_path, write_path, dirs_exist_ok=True)
        else:
            shutil.copyfile(abs_read_path, write_path)

    def download(self, rpath: str, lpath: str, recursive: bool = False, **kwargs: Any) -> Optional[str]:
        # TODO(@damon): Remove the "files" kwarg
        # check if files have been passed (used with downloading artifacts)
        files = kwargs.get("files", [])
        if len(files) == 1:
            rpath = files[0]

        self.copy(read_path=rpath, write_path=lpath)
        return lpath

    def delete(self, read_path: str) -> None:
        """Deletes files from a read path

        Args:
            read_path:
                Path to delete
        """
        # TODO(@damon): Can we replace this with self.client.rm()?
        abs_read_path = self.build_absolute_path(read_path)
        if os.path.isdir(abs_read_path):
            self.client.delete_dir(abs_read_path)
        else:
            self.client.delete_file(abs_read_path)

    @staticmethod
    def validate(storage_system: StorageSystem) -> bool:
        return storage_system == StorageSystem.LOCAL


class ApiStorageClient(StorageClient):
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

    def list_files(self, storage_uri: str) -> List[str]:
        response = self.api_client.post_request(
            route=ApiRoutes.LIST_FILES,
            json={"read_path": str(storage_uri)},
        )
        files = response.get("files")

        if files is not None:
            return cast(List[str], files)

        raise ValueError("No files found")

    def _upload_file(
        self,
        local_dir: str,
        write_dir: str,
        filename: str,
        recursive: bool = False,
        **kwargs: Any,
    ) -> str:
        files = {"file": open(os.path.join(local_dir, filename), "rb")}  # pylint: disable=consider-using-with
        headers = {"Filename": filename, "WritePath": write_dir}

        response = self.api_client.stream_post_request(
            route=ApiRoutes.UPLOAD,
            files=files,
            headers=headers,
        )
        storage_uri: Optional[str] = response.get("storage_uri")

        if storage_uri is not None:
            return storage_uri
        raise ValueError("No storage_uri found")

    def upload_single_file(self, local_path: str, write_path: str) -> str:
        return self._upload_file(
            local_dir=os.path.dirname(local_path),
            write_dir=os.path.dirname(write_path),
            filename=os.path.basename(local_path),
        )

    def upload_directory(self, local_path: str, write_path: str) -> str:
        write_path_path = Path(write_path)
        for path, _, files in os.walk(local_path):
            for filename in files:
                curr_local_path = Path(path).joinpath(filename)
                curr_write_path = write_path_path.joinpath(curr_local_path.relative_to(local_path))
                self._upload_file(
                    local_dir=str(curr_local_path.parent),
                    write_dir=str(curr_write_path.parent),
                    filename=curr_local_path.name,
                )
        return write_path

    def upload(
        self,
        local_path: str,
        write_path: str,
        recursive: bool = False,
        **kwargs: Any,
    ) -> str:
        """
        Uploads local artifact to server
        Args:
            local_path:
                Local path to artifact(s)
            write_path:
                Path where current artifact has been saved to
            recursive:
                Whether to recursively upload files
            kwargs:
                Additional arguments to pass to upload function
        Returns:
            Write path
        """
        if os.path.isdir(local_path):
            return self.upload_directory(local_path=local_path, write_path=write_path)
        return self.upload_single_file(local_path=local_path, write_path=write_path)

    def _download_directory(
        self,
        rpath: str,
        lpath: str,
        files: List[str],
    ) -> str:
        for file_ in files:
            path = Path(file_)
            read_dir = str(path.parent)

            if path.is_dir():
                continue  # folder name path gets added to files list when we use local storage client

            self.api_client.stream_download_file_request(
                route=ApiRoutes.DOWNLOAD_FILE,
                local_dir=read_dir.replace(rpath, lpath),
                read_dir=read_dir,
                filename=path.name,
            )

        return lpath

    def download_file(self, lpath: str, filename: str) -> str:
        read_dir = os.path.dirname(filename)
        file_ = os.path.basename(filename)

        self.api_client.stream_download_file_request(
            route=ApiRoutes.DOWNLOAD_FILE,
            local_dir=lpath,
            read_dir=read_dir,
            filename=file_,
        )

        return os.path.join(lpath, file_)

    def download(self, rpath: str, lpath: str, recursive: bool = False, **kwargs: Any) -> Optional[str]:
        files = kwargs.get("files", None)
        if len(files) == 1:
            return self.download_file(lpath=lpath, filename=files[0])
        return self._download_directory(rpath=rpath, lpath=lpath, files=files)

    def store(self, storage_uri: str, **kwargs: Any) -> str:
        """Wrapper method needed for working with data artifacts (zarr)"""
        return storage_uri

    def open(self, filename: str, mode: str) -> BinaryIO:
        raise NotImplementedError

    def delete(self, read_path: str) -> None:
        """Deletes files from a read path

        Args:
            read_path:
                Path to delete
        """
        response = self.api_client.post_request(
            route=ApiRoutes.DELETE_FILE,
            json={"read_path": read_path},
        )

        if response.get("deleted") is False:
            raise ValueError("Failed to delete file")

    @staticmethod
    def validate(storage_system: StorageSystem) -> bool:
        return storage_system == StorageSystem.API


StorageClientType = Union[
    LocalStorageClient,
    GCSFSStorageClient,
    S3StorageClient,
    ApiStorageClient,
]


class _DefaultAttrCreator:
    @staticmethod
    def get_storage_settings(cfg: OpsmlConfig) -> StorageSettings:
        if "gs://" in cfg.opsml_storage_uri:
            return _DefaultAttrCreator._get_gcs_settings(cfg.opsml_storage_uri)
        if "s3://" in cfg.opsml_storage_uri:
            return S3StorageClientSettings(
                storage_uri=cfg.opsml_storage_uri,
            )
        return StorageClientSettings(
            storage_uri=cfg.opsml_storage_uri,
        )

    @staticmethod
    def _get_gcs_settings(storage_uri: str) -> GcsStorageClientSettings:
        from opsml.helpers.gcp_utils import GcpCredsSetter

        gcp_creds = GcpCredsSetter().get_creds()

        return GcsStorageClientSettings(
            storage_uri=storage_uri,
            gcp_project=gcp_creds.project,
            credentials=gcp_creds.creds,
        )


def get_storage_client(cfg: OpsmlConfig) -> StorageClientType:
    if not cfg.is_tracking_local:
        settings: StorageSettings = ApiStorageClientSettings(
            storage_uri=cfg.opsml_storage_uri,
            opsml_tracking_uri=cfg.opsml_tracking_uri,
            opsml_username=cfg.opsml_username,
            opsml_password=cfg.opsml_password,
            opsml_prod_token=cfg.opsml_prod_token,
        )
    else:
        settings = _DefaultAttrCreator.get_storage_settings(cfg)

    client_type = next(
        (c for c in all_subclasses(StorageClient) if c.validate(settings.storage_system)),
        LocalStorageClient,
    )

    return client_type(settings=settings)


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
