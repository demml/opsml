# pylint: disable=import-outside-toplevel,disable=invalid-envvar-value,disable=protected-access,disable=too-many-lines
# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os
import re
import shutil
import tempfile
import uuid
import warnings
from contextlib import contextmanager
from enum import Enum
from pathlib import Path
from typing import (
    Any,
    BinaryIO,
    Generator,
    Iterator,
    List,
    Optional,
    Tuple,
    Union,
    cast,
)

from pyarrow.fs import LocalFileSystem

from opsml.helpers.logging import ArtifactLogger
from opsml.helpers.request_helpers import ApiRoutes
from opsml.helpers.utils import all_subclasses
from opsml.registry.storage.types import (
    ApiStorageClientSettings,
    ArtifactStorageSpecs,
    FilePath,
    GcsStorageClientSettings,
    S3StorageClientSettings,
    StorageSettings,
)

warnings.filterwarnings("ignore", message="Setuptools is replacing distutils.")
warnings.filterwarnings("ignore", message="Hint: Inferred schema contains integer*")

logger = ArtifactLogger.get_logger()


class StorageSystem(str, Enum):
    GCS = "gcs"
    S3 = "s3"
    LOCAL = "local"
    API = "api"


class ArtifactClass(str, Enum):
    DATA = "data"
    OTHER = "other"


class DataArtifactNames(str, Enum):
    PARQUET = "parquet"
    ZARR = "zarr"
    DATACARD = "datacard"


class ModelArtifactNames(str, Enum):
    MODELCARD = "modelcard"
    TRAINED_MODEL = "trained-model"
    MODEL_METADATA = "model-metadata"
    ONNX = ".onnx"


OPSML_PATTERN = "OPSML_+(\\S+)+_REGISTRY"


def extract_registry_name(string: str) -> Optional[str]:
    """Extracts registry name from string

    Args:
        string:
            String
    Returns:
        Registry name
    """
    reg = re.compile(OPSML_PATTERN)
    match = reg.match(string)

    if match is not None:
        return match.group(1)
    return None


class StorageClient:
    def __init__(
        self,
        storage_settings: StorageSettings,
        client: Any = LocalFileSystem(),
        backend: str = StorageSystem.LOCAL.value,
    ):
        self.client = client
        self.backend = backend
        self.base_path_prefix = storage_settings.storage_uri

    def extend_storage_spec(
        self,
        spec: ArtifactStorageSpecs,
        extra_path: Optional[str] = None,
        file_suffix: Optional[str] = None,
    ) -> ArtifactStorageSpecs:
        """A utility function which extends the storage spec with an optional path and suffix."""
        ret = spec.model_copy()
        if extra_path is not None:
            ret.save_path = os.path.join(ret.save_path, extra_path)

        ret.filename = ret.filename or uuid.uuid4().hex
        if file_suffix is not None:
            ret.filename = f"{ret.filename}.{file_suffix}"
        return ret

    @contextmanager
    def create_temp_save_path_with_spec(
        self,
        spec: ArtifactStorageSpecs,
    ) -> Generator[Tuple[str, str], None, None]:
        spec.filename = spec.filename or uuid.uuid4().hex
        path = os.path.join(self.base_path_prefix, spec.save_path, spec.filename)
        with tempfile.TemporaryDirectory() as tmpdirname:  # noqa
            yield path, os.path.join(tmpdirname, spec.filename)

    def list_files(self, storage_uri: str) -> FilePath:
        raise NotImplementedError

    def store(self, storage_uri: str, **kwargs: Any) -> Any:
        raise NotImplementedError

    def open(self, filename: str, mode: str) -> BinaryIO:
        raise NotImplementedError

    def iterfile(self, file_path: str, chunk_size: int) -> Iterator[bytes]:
        with self.open(file_path, "rb") as file_:
            while chunk := file_.read(chunk_size):
                yield chunk

    def download(self, rpath: str, lpath: str, recursive: bool = False, **kwargs: Any) -> Optional[str]:
        return cast(Optional[str], self.client.download(rpath=rpath, lpath=lpath, recursive=recursive))

    def upload(
        self,
        local_path: str,
        write_path: str,
        recursive: bool = False,
        **kwargs: Any,
    ) -> str:
        self.client.upload(lpath=local_path, rpath=write_path, recursive=recursive)
        return write_path

    def copy(self, read_path: str, write_path: str) -> None:
        raise ValueError("Storage class does not implement a copy method")

    def delete(self, read_path: str) -> None:
        raise ValueError("Storage class does not implement a delete method")

    @staticmethod
    def validate(storage_backend: str) -> bool:
        raise NotImplementedError


class GCSFSStorageClient(StorageClient):
    def __init__(
        self,
        storage_settings: StorageSettings,
    ):
        import gcsfs

        assert isinstance(storage_settings, GcsStorageClientSettings)
        client = gcsfs.GCSFileSystem(
            project=storage_settings.gcp_project,
            token=storage_settings.credentials,
        )

        super().__init__(
            storage_settings=storage_settings,
            client=client,
            backend=StorageSystem.GCS.value,
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
        return cast(BinaryIO, self.client.open(filename, mode))

    def list_files(self, storage_uri: str) -> FilePath:
        return [f"gs://{path}" for path in self.client.ls(path=storage_uri)]

    def store(self, storage_uri: str, **kwargs: Any) -> Any:
        """Create store for use with Zarr arrays"""
        import gcsfs

        return gcsfs.GCSMap(storage_uri, gcs=self.client, check=False)

    def download(self, rpath: str, lpath: str, recursive: bool = False, **kwargs: Any) -> Optional[str]:
        loadable_path: str = self.client.download(rpath=rpath, lpath=lpath, recursive=recursive)

        if all(path is None for path in loadable_path):
            file_ = os.path.basename(rpath)
            return os.path.join(lpath, file_)
        return loadable_path

    @staticmethod
    def validate(storage_backend: str) -> bool:
        return storage_backend == StorageSystem.GCS


class S3StorageClient(StorageClient):
    def __init__(
        self,
        storage_settings: StorageSettings,
    ):
        import s3fs

        assert isinstance(storage_settings, S3StorageClientSettings)
        client = s3fs.S3FileSystem()

        super().__init__(
            storage_settings=storage_settings,
            client=client,
            backend=StorageSystem.S3.value,
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
        return cast(BinaryIO, self.client.open(filename, mode))

    def list_files(self, storage_uri: str) -> FilePath:
        return [f"s3://{path}" for path in self.client.ls(path=storage_uri)]

    def store(self, storage_uri: str, **kwargs: Any) -> Any:
        """Create store for use with Zarr arrays"""
        import s3fs

        return s3fs.S3Map(storage_uri, s3=self.client, check=False)

    def download(self, rpath: str, lpath: str, recursive: bool = False, **kwargs: Any) -> Optional[str]:
        loadable_path: str = self.client.download(rpath=rpath, lpath=lpath, recursive=recursive)

        if all(path is None for path in loadable_path):
            file_ = os.path.basename(rpath)
            return os.path.join(lpath, file_)
        return loadable_path

    @staticmethod
    def validate(storage_backend: str) -> bool:
        return storage_backend == StorageSystem.S3


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

        if os.path.isdir(local_path):
            write_dir = Path(write_path)
            write_dir.mkdir(parents=True, exist_ok=True)
            shutil.copytree(local_path, write_path, dirs_exist_ok=True)

        else:
            write_dir = Path(write_path).parents[0]
            write_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy(local_path, write_path)

        return write_path

    def list_files(self, storage_uri: str) -> FilePath:
        path = Path(storage_uri)

        if path.is_dir():
            paths = [str(p) for p in path.rglob("*")]
            return paths

        return [storage_uri]

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
        if Path(read_path).is_dir():
            shutil.copytree(read_path, write_path, dirs_exist_ok=True)
        else:
            shutil.copyfile(read_path, write_path)

    def download(self, rpath: str, lpath: str, recursive: bool = False, **kwargs: Any) -> Optional[str]:
        local_path = Path(lpath)
        read_path = Path(rpath)

        # check if files have been passed (used with downloading artifacts)
        files = kwargs.get("files", [])
        if len(files) == 1:
            filepath = Path(files[0])

            if local_path.is_dir():
                lpath = str(local_path / filepath.name)

            return cast(Optional[str], self.copy(read_path=str(filepath), write_path=lpath))

        # check if trying to copy single file to directory
        if read_path.is_file():
            lpath = str(local_path / read_path.name)
            return cast(Optional[str], self.copy(read_path=rpath, write_path=lpath))

        return cast(Optional[str], self.copy(read_path=rpath, write_path=lpath))

    def delete(self, read_path: str) -> None:
        """Deletes files from a read path

        Args:
            read_path:
                Path to delete
        """
        if Path(read_path).is_dir():
            self.client.delete_dir(read_path)

        else:
            self.client.delete_file(read_path)

    @staticmethod
    def validate(storage_backend: str) -> bool:
        return storage_backend == StorageSystem.LOCAL


class ApiStorageClient(LocalStorageClient):
    def __init__(self, storage_settings: StorageSettings):
        assert isinstance(storage_settings, ApiStorageClientSettings)
        super().__init__(
            storage_settings=storage_settings,
            backend=StorageSystem.API.value,
        )

        self.api_client = storage_settings.api_client

    def list_files(self, storage_uri: str) -> FilePath:
        response = self.api_client.post_request(
            route=ApiRoutes.LIST_FILES,
            json={"read_path": storage_uri},
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
        filename = os.path.basename(local_path)

        # paths should be directories for uploading
        local_dir = os.path.dirname(local_path)
        write_dir = os.path.dirname(write_path)

        return self._upload_file(
            local_dir=local_dir,
            write_dir=write_dir,
            filename=filename,
        )

    def upload_directory(self, local_path: str, write_path: str) -> str:
        for path, _, files in os.walk(local_path):
            for filename in files:
                write_dir = path.replace(local_path, write_path)

                self._upload_file(
                    local_dir=path,
                    write_dir=write_dir,
                    filename=filename,
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

        if not os.path.isdir(local_path):
            return self.upload_single_file(local_path=local_path, write_path=write_path)

        return self.upload_directory(local_path=local_path, write_path=write_path)

    def download_directory(
        self,
        rpath: str,
        lpath: str,
        files: List[str],
        recursive: bool = False,
    ) -> str:
        for file_ in files:
            path = Path(file_)
            read_dir = str(path.parents[0])

            if path.is_dir():
                continue  # folder name path gets added to files list when use local storage client

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
        return self.download_directory(rpath=rpath, lpath=lpath, files=files)

    def store(self, storage_uri: str, **kwargs: Any) -> str:
        """Wrapper method needed for working with data artifacts (zarr)"""
        return storage_uri

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
    def validate(storage_backend: str) -> bool:
        return storage_backend == StorageSystem.API


StorageClientType = Union[
    LocalStorageClient,
    GCSFSStorageClient,
    S3StorageClient,
    ApiStorageClient,
]


def get_storage_client(
    storage_settings: StorageSettings,
) -> StorageClientType:
    storage_client = next(
        (
            storage_client
            for storage_client in all_subclasses(StorageClient)
            if storage_client.validate(storage_backend=storage_settings.storage_type)
        ),
        LocalStorageClient,
    )

    return storage_client(storage_settings=storage_settings)
