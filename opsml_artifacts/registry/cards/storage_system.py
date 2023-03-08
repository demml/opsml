# pylint: disable=import-outside-toplevel

import tempfile
import uuid
from contextlib import contextmanager
from enum import Enum
from pathlib import Path
from typing import Any, Generator, List, Optional, Tuple, Union, cast

from pyarrow.parquet import LocalFileSystem

from opsml_artifacts.helpers.models import GcsStorageClientInfo, StorageInfo
from opsml_artifacts.registry.cards.types import SaveInfo, StorageClientProto


class StorageSystem(str, Enum):
    GCS = "gcs"
    LOCAL = "local"


class StorageClient:
    def __init__(
        self,
        storage_info: StorageInfo,
        client: Any = LocalFileSystem(),
        backend: str = StorageSystem.LOCAL.name,
    ):

        self.client = client
        self.backend = backend
        self.base_path_prefix = storage_info.storage_url

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

    @contextmanager
    def create_temp_save_path(
        self, save_info: SaveInfo, file_suffix: Optional[str]
    ) -> Generator[Tuple[Any, Any], None, None]:
        with tempfile.TemporaryDirectory() as tmpdirname:  # noqa
            storage_uri, local_path = self.create_tmp_path(
                save_info=save_info,
                file_suffix=file_suffix,
                tmp_dir=tmpdirname,
            )
            yield storage_uri, local_path

    def list_files(self, storage_uri: str) -> List[str]:
        raise NotImplementedError

    def store(self, storage_uri: str):
        raise NotImplementedError

    @staticmethod
    def validate(storage_backend: str) -> bool:
        raise NotImplementedError


class GCSFSStorageClient(StorageClient):
    def __init__(
        self,
        storage_info: StorageInfo,
    ):
        import gcsfs

        storage_info = cast(GcsStorageClientInfo, storage_info)
        client = gcsfs.GCSFileSystem(
            project=storage_info.gcp_project,
            token=storage_info.credentials,
        )
        super().__init__(
            storage_info=storage_info,
            client=client,
            backend=StorageSystem.GCS.name,
        )

    def list_files(self, storage_uri: str) -> List[str]:
        bucket = storage_uri.split("/")[2]
        file_path = "/".join(storage_uri.split("/")[3:])
        files = ["gs://" + path for path in self.client.ls(path=bucket, prefix=file_path)]

        return files

    def store(self, storage_uri: str) -> Any:
        """Create store for use with Zarr arrays"""
        import gcsfs  # pylint: disable=import-outside-toplevel

        return gcsfs.GCSMap(
            storage_uri,
            gcs=self.client,
            check=False,
        )

    @staticmethod
    def validate(storage_backend: str) -> bool:
        return storage_backend == StorageSystem.GCS


class LocalStorageClient(StorageClient):
    def _make_path(self, folder_path: str):
        Path(folder_path).mkdir(parents=True, exist_ok=True)

    def create_save_path(
        self,
        save_info: SaveInfo,
        file_suffix: Optional[str] = None,
        **kwargs,
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
        return storage_backend == StorageSystem.LOCAL


class StorageClientGetter:
    @staticmethod
    def get_storage_client(
        storage_info: StorageInfo,
    ) -> StorageClientProto:

        storage_client = next(
            (
                storage_client
                for storage_client in StorageClient.__subclasses__()
                if storage_client.validate(storage_backend=storage_info.storage_type)
            ),
            LocalStorageClient,
        )

        return cast(StorageClientProto, storage_client(storage_info=storage_info))


StorageClientTypes = Union[LocalStorageClient, GCSFSStorageClient]
