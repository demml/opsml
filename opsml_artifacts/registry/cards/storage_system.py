from abc import ABC, abstractmethod
from typing import Dict, Tuple, List, Optional, Any
from opsml_artifacts.registry.cards.types import SaveInfo, StorageClientInfo
from pyarrow.parquet import LocalFileSystem
from enum import Enum
import uuid
import os
import glob


class StorageSystem(str, Enum):
    GCP = "cloudsqlconnection"
    LOCAL = "localsqlconnection"


class StorageClient(ABC):
    def __init__(self, storage_client, backend: str):
        self.client = storage_client
        self.backend = backend

    @abstractmethod
    def create_save_path(self, save_info: SaveInfo, file_suffix: str) -> Tuple[str, str]:
        raise NotImplementedError

    def create_tmp_path(self, save_info: SaveInfo, file_suffix: str, tmp_dir: str) -> Tuple[str, str]:
        raise NotImplementedError

    @abstractmethod
    def list_files(self, storage_uri: str) -> List[str]:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def validate(storage_backend: str) -> bool:
        raise NotImplementedError


class GCSFSStorageClient(StorageClient):
    def __init__(self, connection_args: Dict[str, Any]):
        import gcsfs

        self.gcs_bucket = connection_args.get("gcs_bucket")
        client = gcsfs.GCSFileSystem(
            project=connection_args.get("gcp_project"),
            token=connection_args.get("gcsfs_creds"),
        )
        super().__init__(
            storage_client=client,
            backend=StorageSystem.GCP.name,
        )

    def create_save_path(
        self,
        save_info: SaveInfo,
        file_suffix: str,
    ) -> Tuple[str, str]:
        filename = uuid.uuid4().hex
        if file_suffix is not None:
            filename = f"{filename}.{file_suffix}"
        gcs_base_path = f"gs://{self.gcs_bucket}/{save_info.blob_path}"
        data_path = f"/{save_info.team}/{save_info.name}/version-{save_info.version}"

        return gcs_base_path + data_path + f"/{filename}", filename

    def create_tmp_path(
        self,
        save_info: SaveInfo,
        file_suffix: str,
        tmp_dir: str,
    ):
        gcs_path, filename = self.create_save_path(
            save_info=save_info,
            file_suffix=file_suffix,
        )
        local_path = f"{tmp_dir}/{filename}"

        return gcs_path, local_path

    def list_files(self, storage_uri: str) -> List[str]:
        bucket = storage_uri.split("/")[2]
        file_path = "/".join(storage_uri.split("/")[3:])
        files = ["gs://" + path for path in self.client.ls(path=bucket, prefix=file_path)]

        return files

    @staticmethod
    def validate(storage_backend: str) -> bool:
        return storage_backend == "gcp"


class LocalStorageClient(StorageClient):
    def __init__(self, connection_args: Dict[str, Any]):

        self.storage_folder = os.path.expanduser("~")
        client = LocalFileSystem()
        super().__init__(
            storage_client=client,
            backend=StorageSystem.LOCAL.name,
        )

    def create_save_path(
        self,
        save_info: SaveInfo,
        file_suffix: str,
    ) -> Tuple[str, str]:
        filename = uuid.uuid4().hex
        if file_suffix is not None:
            filename = f"{filename}.{file_suffix}"
        gcs_base_path = f"{self.storage_folder}/{save_info.blob_path}"
        data_path = f"/{save_info.team}/{save_info.name}/version-{save_info.version}"

        return gcs_base_path + data_path + f"/{filename}", filename

    def list_files(self, storage_uri: str) -> List[str]:
        return [self.client.get_file_info(storage_uri)]

    @staticmethod
    def validate(storage_backend: str) -> bool:
        return storage_backend == "local"


class StorageClientGetter:
    @staticmethod
    def get_storage_client(
        connection_args: Dict[str, Any],
    ):
        storage_client = next(
            (
                storage_client
                for storage_client in StorageClient.__subclasses__()
                if storage_client.validate(storage_backend=connection_args.get("storage_backend"))
            ),
            LocalStorageClient,
        )

        return storage_client(connection_args=connection_args)
