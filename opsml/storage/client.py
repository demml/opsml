# # pylint: disable=import-outside-toplevel,broad-exception-caught
# Copyright (c) 2023-2024 Shipt, Inc.
# Copyright (c) 2024-current Demml, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.


import datetime
import io
import warnings
from functools import cached_property
from pathlib import Path
from typing import Any, BinaryIO, Dict, Iterator, List, Optional, Protocol, Union, cast

from fsspec.implementations.local import LocalFileSystem

from opsml.helpers.logging import ArtifactLogger
from opsml.settings.config import OpsmlConfig, config
from opsml.storage.api import ApiClient, ApiRoutes, RequestType
from opsml.types import (
    ApiStorageClientSettings,
    AzureStorageClientSettings,
    BotoClient,
    GCSClient,
    GcsStorageClientSettings,
    S3StorageClientSettings,
    StorageClientProtocol,
    StorageClientSettings,
    StorageSettings,
    StorageSystem,
)

warnings.filterwarnings("ignore", message="Setuptools is replacing distutils.")
warnings.filterwarnings("ignore", message="Hint: Inferred schema contains integer*")

logger = ArtifactLogger.get_logger()


class _FileSystemProtocol(Protocol):
    """
    The *low level* file system interface which the storage client uses to write
    to its underlying file system.

    This interface is based on the fsspec AbstractFileSystem interface, however
    simplified to only the functions needed by opsml to reduce the API surface.

    While this API is *very* similar to StorageClientProtocol, they are
    different.

    1. StorageClientProtocol is a smaller API than what fsspec exposes. In
       particular, StorageClientProtocol does not expose "recursive" flags as
       each storage client will determine if recursive is required based on the
       path. Operations on directories are recursive, operations on files are
       not recursive.

    2. pathlib.Path is exposed on StorageClientProtocol, where fsspec APIs use
       str for paths.
    """

    def get(self, lpath: str, rpath: str, recursive: bool) -> None:
        """Copies file(s) from remote path (rpath) to local path (lpath)"""

    def ls(  # pylint: disable=invalid-name
        self, path: str, detail: bool = False
    ) -> Union[List[str], List[Dict[str, Any]]]:
        pass

    def find(self, path: str) -> List[str]:
        """Recursively list all files excluding directories"""

    def open(self, path: str, mode: str, encoding: Optional[str] = None) -> BinaryIO:
        """Open a file"""

    def iterfile(self, path: str, chunk_size: int) -> Iterator[bytes]:
        """Open an iterator"""

    def put(self, lpath: str, rpath: str, recursive: bool) -> None:
        """Copies file(s) from local path (lpath) to remote path (rpath)"""

    def copy(self, src: str, dest: str, recursive: bool) -> None:
        """Copies files from src to dest within the file system"""

    def rm(self, path: str, recursive: bool) -> None:  # pylint: disable=invalid-name
        """Deletes file(s)"""

    def exists(self, path: str) -> bool:
        """Determines if a file or directory exists"""


class StorageClientBase(StorageClientProtocol):
    def __init__(
        self,
        settings: StorageSettings,
        client: Optional[_FileSystemProtocol] = None,
    ):
        if client is None:
            self.client = cast(_FileSystemProtocol, LocalFileSystem(auto_mkdir=True))
        else:
            self.client = client
        self.settings = settings

    def get(self, rpath: Path, lpath: Path) -> None:
        # handle rpath
        if rpath.suffix:
            recursive = False
            abs_rpath = str(rpath)
        else:
            recursive = True
            abs_rpath = f"{str(rpath)}/"

        # handle lpath
        if lpath.suffix:
            abs_lpath = f"{str(lpath.parent)}/"
        else:
            abs_lpath = f"{str(lpath)}/"

        self.client.get(rpath=abs_rpath, lpath=abs_lpath, recursive=recursive)

    def ls(self, path: Path, detail: bool = False) -> Union[List[Path], List[Dict[str, Any]]]:
        files = self.client.ls(str(path), detail=detail)

        if detail:
            files = cast(List[Dict[str, Any]], files)
            return files

        files = cast(List[str], files)
        return [Path(f) for f in files]

    def find(self, path: Path) -> List[Path]:
        return [Path(p) for p in self.client.find(str(path))]

    def open(self, path: Path, mode: str, encoding: Optional[str] = None) -> BinaryIO:
        return self.client.open(str(path), mode=mode, encoding=encoding)

    def iterfile(self, path: Path, chunk_size: int) -> Iterator[bytes]:
        with self.open(path, "rb") as file_:
            while chunk := file_.read(chunk_size):
                yield chunk

    def iterbuffer(self, buffer: io.BytesIO, chunk_size: int) -> Iterator[bytes]:
        buffer.seek(0)
        while chunk := buffer.read(chunk_size):
            yield chunk

    def put(self, lpath: Path, rpath: Path) -> None:
        if lpath.is_dir():
            abs_lpath = f"{str(lpath)}/"  # pathlib strips trailing slashes
            abs_rpath = f"{str(rpath)}/"
            self.client.put(abs_lpath, abs_rpath, True)
        else:
            self.client.put(str(lpath), str(rpath), False)

    def copy(self, src: Path, dest: Path) -> None:
        self.client.copy(str(src), str(dest), recursive=True)

    def rm(self, path: Path) -> None:
        self.client.rm(str(path), True)

    def exists(self, path: Path) -> bool:
        try:
            return self.client.exists(path=str(path))
        except FileNotFoundError:
            return False

    def generate_presigned_url(self, path: Path, expiration: int) -> Optional[str]:
        """Generates pre signed url for object"""
        return path.as_posix()


class GCSFSStorageClient(StorageClientBase):
    def __init__(
        self,
        settings: StorageSettings,
    ):
        import gcsfs

        assert isinstance(settings, GcsStorageClientSettings)
        if settings.default_creds is None:
            logger.info("Using default GCP credentials")
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

    @cached_property
    def gcs_client(self) -> GCSClient:
        from google.cloud import storage

        assert isinstance(self.settings, GcsStorageClientSettings)

        return cast(
            GCSClient,
            storage.Client(
                credentials=self.settings.credentials,
            ),
        )

    @cached_property
    def get_id_credentials(self) -> Any:
        assert isinstance(self.settings, GcsStorageClientSettings)

        if self.settings.default_creds:
            logger.debug("Default Creds: {}", self.settings.default_creds)
            from google.auth import compute_engine
            from google.auth.transport import requests

            auth_request = requests.Request()  # type: ignore
            return compute_engine.IDTokenCredentials(auth_request, "")  # type: ignore

        return self.settings.credentials

    def generate_presigned_url(self, path: Path, expiration: int) -> Optional[str]:
        """Generates pre signed url for S3 object"""

        try:
            bucket = self.gcs_client.bucket(config.storage_root)
            blob = bucket.blob(str(path))
            return blob.generate_signed_url(
                expiration=datetime.timedelta(seconds=expiration),
                credentials=self.get_id_credentials,
                method="GET",
            )
        except Exception as error:
            logger.error("Failed to generate presigned URL: {}", error)
            return None


class S3StorageClient(StorageClientBase):
    def __init__(
        self,
        settings: StorageSettings,
    ):
        import s3fs

        from opsml.helpers.aws_utils import AwsCredsSetter

        assert isinstance(settings, S3StorageClientSettings)
        assert isinstance(settings.credentials, AwsCredsSetter)

        client = s3fs.S3FileSystem(
            key=settings.credentials.access_key,
            secret=settings.credentials.secret,
            token=settings.credentials.token,
        )

        super().__init__(
            settings=settings,
            client=client,
        )

    @cached_property
    def s3_client(self) -> BotoClient:
        import boto3

        return cast(BotoClient, boto3.client("s3"))

    def generate_presigned_url(self, path: Path, expiration: int) -> Optional[str]:
        """Generates pre signed url for S3 object"""
        try:
            return self.s3_client.generate_presigned_url(
                "get_object",
                Params={"Bucket": config.storage_root, "Key": str(path)},
                ExpiresIn=expiration,
            )
        except Exception as error:
            logger.error(f"Failed to generate presigned URL: {error}")
            return None


class AzureStorageClient(StorageClientBase):
    def __init__(
        self,
        settings: StorageSettings,
    ) -> None:
        import logging

        import adlfs

        from opsml.helpers.azure_utils import AzureCreds

        assert isinstance(settings, AzureStorageClientSettings)
        assert isinstance(settings.credentials, AzureCreds)

        # Set the logging level for all azure* libraries
        # Azure logs a lot of info messages by default (dumb)
        _logger = logging.getLogger("azure")
        _logger.setLevel(logging.ERROR)

        client = adlfs.AzureBlobFileSystem(
            account_name=settings.credentials.account_name,
            anon=False,
            tenant_id=settings.credentials.tenant_id,
            client_id=settings.credentials.client_id,
            client_secret=settings.credentials.client_secret,
        )

        super().__init__(
            settings=settings,
            client=client,
        )

    async def _generate_blob_sas(
        self,
        path: Path,
        start_time: datetime.datetime,
        expiry_time: datetime.datetime,
    ) -> Optional[str]:
        """Generates pre signed url for Azure object. This re-implements the
        fsspec _url Azure BlobFileSystem logic to generate a SAS token for a blob.
        The library does not current accept a user delegation key, so this is a workaround.
        """

        import adlfs
        from azure.storage.blob import generate_blob_sas

        assert isinstance(self.client, adlfs.AzureBlobFileSystem)

        user_delegation_key = await self.client.service_client.get_user_delegation_key(
            key_start_time=start_time,
            key_expiry_time=expiry_time,
        )

        sas_token = generate_blob_sas(
            account_name=self.client.account_name,
            container_name=config.storage_root,
            blob_name=str(path),
            user_delegation_key=user_delegation_key,
            permission="r",
            start=start_time,
            expiry=expiry_time,
        )

        async with self.client.service_client.get_blob_client(config.storage_root, str(path)) as blob_client:
            url = f"{blob_client.url}?{sas_token}"
        return url

    def generate_presigned_url(self, path: Path, expiration: int) -> Optional[str]:
        """Generates pre signed url for Azure object

        Args:
            path:
                Path to object
            expiration:
                Expiration time in seconds

        Returns:
            str: SAS URL
        """
        try:
            import adlfs
            from fsspec.asyn import sync

            assert isinstance(self.client, adlfs.AzureBlobFileSystem)
            # Get a user delegation key that's valid for 1 day
            delegation_key_start_time = datetime.datetime.now(datetime.timezone.utc)
            delegation_key_expiry_time = delegation_key_start_time + datetime.timedelta(minutes=30)

            presigned_url: str = sync(
                self.client.loop,
                self._generate_blob_sas,
                str(path),
                delegation_key_start_time,
                delegation_key_expiry_time,
            )

            return presigned_url

        except Exception as error:
            logger.error(f"Error generating SAS URL for container: {error}")
            return None


class LocalStorageClient(StorageClientBase):
    def put(self, lpath: Path, rpath: Path) -> None:
        if rpath.suffix:
            rpath.parent.mkdir(parents=True, exist_ok=True)
        else:
            rpath.mkdir(parents=True, exist_ok=True)

        super().put(lpath, rpath)

    def generate_presigned_url(self, path: Path, expiration: int) -> Optional[str]:
        """Generates pre signed url for object"""
        # use mounted path for local storage
        return (Path("/artifacts") / path).as_posix()


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
            use_auth=settings.opsml_auth,
            token=settings.opsml_prod_token,
            path_prefix=config.opsml_client_path_prefix,
        )

    def get(self, rpath: Path, lpath: Path, recursive: bool = True) -> None:
        """Copies file(s) from remote path (rpath) to local path (lpath)"""

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
                chunk_size=config.download_chunk_size,
            )

    def find(self, path: Path) -> List[Path]:
        response = self.api_client.request(
            route=ApiRoutes.LIST_FILES,
            request_type=RequestType.GET,
            params={"path": path.as_posix()},
        )

        # storage clients always return a list
        files: List[str] = response["files"]

        return [Path(p) for p in files]

    def put(self, lpath: Path, rpath: Path) -> None:
        if not lpath.is_file():
            for curr_lpath in lpath.rglob("*"):
                if curr_lpath.is_file():
                    curr_rpath = rpath / curr_lpath.relative_to(lpath)
                    self.put(curr_lpath, curr_rpath)
            return None

        response = self.api_client.stream_post_request(
            route=ApiRoutes.UPLOAD_FILE,
            files={"file": lpath.open("rb")},
            headers={"write_path": rpath.as_posix()},
            chunk_size=config.upload_chunk_size,
        )
        storage_uri: Optional[str] = response.get("storage_uri")

        if storage_uri is None:
            raise ValueError("Failed to write file to storage")
        return None

    def copy(self, src: Path, dest: Path, recursive: bool = True) -> None:
        raise NotImplementedError

    def open(self, path: Path, mode: str, encoding: Optional[str] = None) -> BinaryIO:
        raise NotImplementedError

    def rm(self, path: Path) -> None:
        response = self.api_client.request(
            route=ApiRoutes.DELETE_FILE,
            request_type=RequestType.GET,
            params={"path": path.as_posix()},
        )

        if response.get("deleted") is False:
            raise ValueError("Failed to delete file")

    def exists(self, path: Path) -> bool:
        """Checks if file exists on server

        Args:
            path:
                Path to file
        """
        response = self.api_client.request(
            route=ApiRoutes.FILE_EXISTS,
            request_type=RequestType.GET,
            params={"path": path.as_posix()},
        )

        return bool(response.get("exists", False))


def _get_gcs_settings(storage_uri: str) -> GcsStorageClientSettings:
    from opsml.helpers.gcp_utils import GcpCredsSetter

    gcp_creds = GcpCredsSetter().get_creds()

    return GcsStorageClientSettings(
        storage_uri=storage_uri,
        gcp_project=gcp_creds.project,
        credentials=gcp_creds.creds,
        default_creds=gcp_creds.default_creds,
    )


def _get_s3_settings(storage_uri: str) -> S3StorageClientSettings:
    """Checks for S3 environment variables and returns the settings.
    If not found, returns the default settings and attempts to connect to the
    s3 file system using system defaults.
    """
    from opsml.helpers.aws_utils import AwsCredsSetter

    credentials = AwsCredsSetter()

    return S3StorageClientSettings(
        storage_uri=storage_uri,
        credentials=credentials,
    )


def _get_azure_settings(storage_uri: str) -> AzureStorageClientSettings:
    """Checks for Azure environment variables and returns the settings.
    If not found, returns the default settings and attempts to connect to the
    Azure file system using system defaults.
    """
    from opsml.helpers.azure_utils import AzureCreds

    azure_creds = AzureCreds()

    return AzureStorageClientSettings(
        storage_uri=storage_uri,
        credentials=azure_creds,
    )


def get_storage_client(cfg: OpsmlConfig) -> StorageClientBase:
    if not cfg.is_tracking_local:
        return ApiStorageClient(
            ApiStorageClientSettings(
                storage_uri=cfg.opsml_storage_uri,
                opsml_tracking_uri=cfg.opsml_tracking_uri,
                opsml_username=cfg.opsml_username,
                opsml_password=cfg.opsml_password,
                opsml_auth=cfg.opsml_auth,
                opsml_prod_token=cfg.opsml_prod_token,
            )
        )
    if cfg.storage_system == StorageSystem.GCS:
        return GCSFSStorageClient(_get_gcs_settings(storage_uri=cfg.opsml_storage_uri))
    if cfg.storage_system == StorageSystem.S3:
        return S3StorageClient(_get_s3_settings(storage_uri=cfg.opsml_storage_uri))
    if cfg.storage_system == StorageSystem.AZURE:
        return AzureStorageClient(_get_azure_settings(storage_uri=cfg.opsml_storage_uri))
    return LocalStorageClient(StorageClientSettings(storage_uri=cfg.opsml_storage_uri))


# The global storage client. When importing from this module, be sure to import
# the *module* rather than storage_client itself to simplify mocking. Tests will
# mock the global storage client.
#
# i.e., use:
# from opsml.storage import client
#
# do_something(client.storage_client)
#
# do *not* use:
# from opsml.storage.client import storage_client
#
# do_something(storage_client)
storage_client = get_storage_client(config)


StorageClient = StorageClientBase
