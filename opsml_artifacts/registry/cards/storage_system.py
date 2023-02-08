# pylint: disable=import-outside-toplevel

import os
import uuid
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union, cast

from pyarrow.parquet import LocalFileSystem

from opsml_artifacts.registry.cards.types import SaveInfo


class StorageSystem(str, Enum):
    GCP = "gcp"
    LOCAL = "local"


class StorageClient:
    def __init__(
        self,
        connection_args: Dict[str, Any],
    ):
        self.connection_args = connection_args
        self.base_path_prefix = "overwrite"
        self.client = LocalFileSystem()
        self.backend = StorageSystem.LOCAL.name
        self.storage_folder = os.path.expanduser("~")
        self.base_path_prefix = self.storage_folder

    def create_save_path(self, save_info: SaveInfo, file_suffix: Optional[str] = None) -> Tuple[str, str]:
        filename = uuid.uuid4().hex
        if file_suffix is not None:
            filename = f"{filename}.{str(file_suffix)}"
        base_path = f"{self.base_path_prefix}/{save_info.blob_path}"
        data_path = f"/{save_info.team}/{save_info.name}/version-{save_info.version}"

        return base_path + data_path + f"/{filename}", filename

    def create_tmp_path(
        self,
        save_info: SaveInfo,
        tmp_dir: str,
        file_suffix: Optional[str] = None,
    ):
        gcs_path, filename = self.create_save_path(save_info=save_info, file_suffix=file_suffix)
        local_path = f"{tmp_dir}/{filename}"

        return gcs_path, local_path

    def list_files(self, storage_uri: str) -> List[str]:
        raise NotImplementedError

    def store(self, storage_uri: str):
        raise NotImplementedError

    @staticmethod
    def validate(storage_backend: str) -> bool:
        raise NotImplementedError


class GCSFSStorageClient(StorageClient):
    def __init__(self, connection_args: Dict[str, Any]):
        super().__init__(connection_args=connection_args)

        import gcsfs

        self.connection_args = connection_args
        self.gcs_bucket = connection_args.get("gcs_bucket")
        self.client = gcsfs.GCSFileSystem(
            project=connection_args.get("gcp_project"),
            token=connection_args.get("gcsfs_creds"),
        )
        self.backend = StorageSystem.GCP.name
        self.base_path_prefix = f"gs://{self.gcs_bucket}"

    def list_files(self, storage_uri: str) -> List[str]:
        bucket = storage_uri.split("/")[2]
        file_path = "/".join(storage_uri.split("/")[3:])
        files = ["gs://" + path for path in self.client.ls(path=bucket, prefix=file_path)]

        return files

    def store(self, storage_uri: str):
        """Create store for use with Zarr arrays"""
        import gcsfs  # pylint: disable=import-outside-toplevel

        return gcsfs.GCSMap(
            storage_uri,
            gcs=self.client,
            check=False,
        )

    @staticmethod
    def validate(storage_backend: str) -> bool:
        return storage_backend == "gcp"


class LocalStorageClient(StorageClient):
    def _make_path(self, folder_path: str):
        Path(folder_path).mkdir(parents=True, exist_ok=True)

    def create_save_path(
        self,
        save_info: SaveInfo,
        file_suffix: Optional[str] = None,
    ) -> Tuple[str, str]:

        save_path, filename = super().create_save_path(save_info=save_info, file_suffix=file_suffix)
        self._make_path("/".join(save_path.split("/")[:-1]))

        return save_path, filename

    def list_files(self, storage_uri: str) -> List[str]:
        return [storage_uri]

    def store(self, storage_uri: str):
        return storage_uri

    @staticmethod
    def validate(storage_backend: str) -> bool:
        return storage_backend == "local"


StorageClientObj = Union[GCSFSStorageClient, LocalStorageClient]


class StorageClientGetter:
    @staticmethod
    def get_storage_client(
        connection_args: Dict[str, Any],
    ) -> Union[GCSFSStorageClient, LocalStorageClient]:

        storage_backend = str(connection_args.get("storage_backend"))
        storage_client = next(
            (
                storage_client
                for storage_client in StorageClient.__subclasses__()
                if storage_client.validate(storage_backend=storage_backend)
            ),
            LocalStorageClient,
        )

        return cast(StorageClientObj, storage_client(connection_args=connection_args))
