# pylint: disable=import-outside-toplevel

import tempfile
import uuid
from contextlib import contextmanager
from enum import Enum
from pathlib import Path
from typing import Any, Generator, List, Optional, Tuple, Union, cast
from pyarrow.parquet import LocalFileSystem

from opsml_artifacts.helpers.models import GcsStorageClientSettings, StorageSettings
from opsml_artifacts.helpers.utils import all_subclasses
from opsml_artifacts.registry.storage.types import ArtifactStorageMetadata, StorageClientProto


class StorageSystem(str, Enum):
    GCS = "gcs"
    LOCAL = "local"
    MLFLOW = "mlflow"


class DataTypes(str, Enum):
    PARQUET = "parquet"
    ZARR = "zarr"


class MlFlowDirs(str, Enum):
    DATA_DIR = "data"
    MODEL_DIR = "model"
    ONNX_MODEL_DIR = "model"
    ARTIFACT_DIR = "misc"


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
        self._storage_metadata = Optional[ArtifactStorageMetadata]

    @property
    def storage_meta(self) -> ArtifactStorageMetadata:
        return cast(ArtifactStorageMetadata, self._storage_metadata)

    @storage_meta.setter
    def storage_meta(self, artifact_storage_metadata):
        self._storage_metadata = artifact_storage_metadata

    def create_save_path(
        self,
        file_suffix: Optional[str] = None,
    ) -> Tuple[str, str]:

        filename = self.storage_meta.filename or uuid.uuid4().hex
        if file_suffix is not None:
            filename = f"{filename}.{str(file_suffix)}"
        base_path = f"{self.base_path_prefix}/{self.storage_meta.save_path}"

        return base_path + f"/{filename}", filename

    def create_tmp_path(
        self,
        tmp_dir: str,
        file_suffix: Optional[str] = None,
    ):
        base_path, filename = self.create_save_path(file_suffix=file_suffix)
        local_path = f"{tmp_dir}/{filename}"

        return base_path, local_path

    @contextmanager
    def create_temp_save_path(
        self,
        file_suffix: Optional[str],
    ) -> Generator[Tuple[Any, Any], None, None]:

        with tempfile.TemporaryDirectory() as tmpdirname:  # noqa
            storage_uri, local_path = self.create_tmp_path(
                file_suffix=file_suffix,
                tmp_dir=tmpdirname,
            )
            yield storage_uri, local_path

    def list_files(self, storage_uri: str) -> List[str]:
        raise NotImplementedError

    def store(self, storage_uri: str):
        raise NotImplementedError

    def upload(self, local_path: str, write_path: str, recursive: bool = False, **kwargs):
        self.client.upload(lpath=local_path, rpath=write_path, recursive=recursive)

    def _make_path(self, folder_path: str):
        Path(folder_path).mkdir(parents=True, exist_ok=True)

    def post_process(self, storage_uri: str) -> str:
        """Method that does post processing. Mainly used for mlflow work"""
        return storage_uri

    @staticmethod
    def validate(storage_backend: str) -> bool:
        raise NotImplementedError


class GCSFSStorageClient(StorageClient):
    def __init__(
        self,
        storage_settings: StorageSettings,
    ):
        import gcsfs

        storage_settings = cast(GcsStorageClientSettings, storage_settings)
        client = gcsfs.GCSFileSystem(
            project=storage_settings.gcp_project,
            token=storage_settings.credentials,
        )
        super().__init__(
            storage_settings=storage_settings,
            client=client,
            backend=StorageSystem.GCS.value,
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
    def create_save_path(
        self,
        file_suffix: Optional[str] = None,
    ) -> Tuple[str, str]:

        save_path, filename = super().create_save_path(
            file_suffix=file_suffix,
        )
        self._make_path("/".join(save_path.split("/")[:-1]))

        return save_path, filename

    def list_files(self, storage_uri: str) -> List[str]:
        return [storage_uri]

    def store(self, storage_uri: str):
        return storage_uri

    @staticmethod
    def validate(storage_backend: str) -> bool:
        return storage_backend == StorageSystem.LOCAL


class MlFlowStorageClient(LocalStorageClient):
    def __init__(
        self,
        storage_settings: StorageSettings,
    ):
        super().__init__(
            storage_settings=storage_settings,
            backend=StorageSystem.MLFLOW.value,
        )

        self._run_id: Optional[str] = None
        self._mlflow_client: Optional[Any] = None  # setting Any so no mlflow import needed

    def set_run_id(self, run_id: str):
        """Sets the run id to use with mlflow logging"""
        self._run_id = run_id

    def set_mlflow_client(self, mlflow_client: str):
        """Sets the mlflow client to use for logging"""
        self._mlflow_client = mlflow_client

    def post_process(self, storage_uri: str) -> str:

        """Uploads local artifact to mflow

        Args:
            local_path (str): Path to local file or folder
            write_path (str): MlFlow path to write to
        """
        mlflow_write_dir = self._get_mlflow_dir(filename=storage_uri)
        self._mlflow_client.log_artifact(
            run_id=self._run_id,
            local_path=storage_uri,
            artifact_path=mlflow_write_dir,
        )
        return storage_uri

    def upload(self, local_path: str, write_path: Optional[str] = None) -> str:
        """This is an explicit overwrite to keep consistency with ArtifactStorage
        subclasses and how LocalFileSystem and GcsfFileSystem upload objects

        """
        return self.post_process(storage_uri=local_path)

    def _get_mlflow_dir(self, filename: str) -> str:
        if any(data_type in filename for data_type in DataTypes):
            return MlFlowDirs.DATA_DIR.value
        return MlFlowDirs.ARTIFACT_DIR.value

    # def create_tmp_path(
    #    self,
    #    artifact_storage_info: ArtifactStorageMetaData,
    #    tmp_dir: str,
    #    file_suffix: Optional[str] = None,
    # ):
    #    _, filename = self.create_save_path(
    #        artifact_storage_info=artifact_storage_info,
    #        file_suffix=file_suffix,
    #    )
    #
    #    # hacky at the moment
    #    mlflow_path = self._get_mlflow_dir(filename=filename)
    #    local_path = f"{tmp_dir}/{filename}"
    #
    #    return mlflow_path, local_path

    @staticmethod
    def validate(storage_backend: str) -> bool:
        return storage_backend == StorageSystem.MLFLOW


class StorageClientGetter:
    @staticmethod
    def get_storage_client(
        storage_settings: StorageSettings,
    ) -> StorageClientProto:

        storage_client = next(
            (
                storage_client
                for storage_client in all_subclasses(StorageClient)
                if storage_client.validate(storage_backend=storage_settings.storage_type)
            ),
            LocalStorageClient,
        )

        return cast(StorageClientProto, storage_client(storage_settings=storage_settings))


StorageClientTypes = Union[LocalStorageClient, GCSFSStorageClient, MlFlowStorageClient]
