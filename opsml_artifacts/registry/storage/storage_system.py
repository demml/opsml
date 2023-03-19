# pylint: disable=import-outside-toplevel

import shutil
import tempfile
import uuid
from contextlib import contextmanager
from enum import Enum
from functools import wraps
from pathlib import Path
from typing import Any, Generator, Optional, Tuple, Union, cast

from pyarrow.parquet import LocalFileSystem

from opsml_artifacts.helpers.utils import all_subclasses
from opsml_artifacts.registry.storage.types import (
    ArtifactStorageSpecs,
    FilePath,
    GcsStorageClientSettings,
    MlFlowClientProto,
    StorageSettings,
)


class StorageSystem(str, Enum):
    GCS = "gcs"
    LOCAL = "local"
    MLFLOW = "mlflow"


class ArtifactClass(str, Enum):
    DATA = "data"
    OTHER = "other"


class DataArtifactNames(str, Enum):
    PARQUET = "parquet"
    ZARR = "zarr"


class ModelArtifactNames(str, Enum):
    MODELCARD = "modelcard"
    TRAINED_MODEL = "trained-model"
    API_DEF = "api-def"


class MlFlowDirs(str, Enum):
    DATA_DIR = "data"
    MODEL_DIR = "model"
    ONNX_MODEL_DIR = "model"
    ARTIFACT_DIR = "misc"


def cleanup_files(func):

    """Decorator for deleting files if needed"""

    @wraps(func)
    def wrapper(self, *args, **kwargs) -> Any:

        artifact, loadable_filepath = func(self, *args, **kwargs)

        if isinstance(loadable_filepath, list):
            loadable_filepath = loadable_filepath[0]

        if isinstance(loadable_filepath, str):

            if "temp" in loadable_filepath:  # make this better later
                try:
                    file_dir = "/".join(loadable_filepath.split("/")[:-1])
                    shutil.rmtree(file_dir)
                except Exception:  # pylint: disable=broad-exception-caught
                    pass  # soft failure

        return artifact

    return wrapper


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
        self._storage_spec = Optional[ArtifactStorageSpecs]

    @property
    def storage_spec(self) -> ArtifactStorageSpecs:
        return cast(ArtifactStorageSpecs, self._storage_spec)

    @storage_spec.setter
    def storage_spec(self, artifact_storage_spec):
        self._storage_spec = artifact_storage_spec

    def create_save_path(
        self,
        file_suffix: Optional[str] = None,
    ) -> Tuple[str, str]:

        filename = self.storage_spec.filename or uuid.uuid4().hex
        if file_suffix is not None:
            filename = f"{filename}.{str(file_suffix)}"
        base_path = f"{self.base_path_prefix}/{self.storage_spec.save_path}"

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

    @contextmanager
    def create_named_tempfile(self, file_suffix: Optional[str]):

        if file_suffix is not None:
            if "." not in file_suffix:
                file_suffix = f".{file_suffix}"

        with tempfile.NamedTemporaryFile(suffix=file_suffix) as tmpfile:  # noqa
            yield tmpfile

    def list_files(self, storage_uri: str) -> FilePath:
        raise NotImplementedError

    def store(self, storage_uri: str):
        raise NotImplementedError

    def download(self, rpath: FilePath, lpath: str, recursive: bool = False) -> Optional[str]:
        return self.client.download(rpath=rpath, lpath=lpath, recursive=recursive)

    def upload(
        self,
        local_path: str,
        write_path: str,
        recursive: bool = False,
    ) -> str:
        self.client.upload(lpath=local_path, rpath=write_path, recursive=recursive)
        return write_path

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

    def list_files(self, storage_uri: str) -> FilePath:
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

    def list_files(self, storage_uri: str) -> FilePath:
        return [storage_uri]

    def store(self, storage_uri: str):
        return storage_uri

    @staticmethod
    def validate(storage_backend: str) -> bool:
        return storage_backend == StorageSystem.LOCAL


class MlFlowStorageClient(StorageClient):
    def __init__(
        self,
        storage_settings: StorageSettings,
    ):
        super().__init__(
            storage_settings=storage_settings,
            backend=StorageSystem.MLFLOW.value,
        )

        self._run_id: Optional[str] = None
        self._artifact_path: Optional[str] = None
        self._mlflow_client: Optional[MlFlowClientProto] = None  # setting Any so no mlflow import needed

    @property
    def run_id(self) -> str:
        return str(self._run_id)

    @run_id.setter
    def run_id(self, run_id: str):
        self._run_id = run_id

    @property
    def artifact_path(self):
        return str(self._artifact_path)

    @artifact_path.setter
    def artifact_path(self, artifact_path: str):
        self._artifact_path = artifact_path

    @property
    def mlflow_client(self):
        return cast(MlFlowClientProto, self._mlflow_client)

    @mlflow_client.setter
    def mlflow_client(self, mlflow_client: MlFlowClientProto):
        self._mlflow_client = mlflow_client

    def create_save_path(
        self,
        file_suffix: Optional[str] = None,
    ) -> Tuple[str, str]:

        save_path, filename = super().create_save_path(
            file_suffix=file_suffix,
        )

        return save_path, filename

    def download(self, rpath: FilePath, lpath: str, recursive: bool = False) -> Optional[str]:
        import mlflow

        temp_path = Path("temp")
        temp_path.mkdir(parents=True, exist_ok=True)
        abs_temp_path = str(temp_path.resolve())

        file_path = mlflow.artifacts.download_artifacts(
            artifact_uri=rpath,
            dst_path=abs_temp_path,
            tracking_uri=self.mlflow_client.tracking_uri,
        )
        return file_path

    def upload(
        self,
        local_path: str,
        write_path: str,
        recursive: bool = False,
    ) -> str:

        """Uploads local artifact to mflow

        Args:
            storage_uri: Path where current artifact has been saved to
        """

        mlflow_write_dir = self._get_mlflow_dir(filename=write_path)

        self.mlflow_client.log_artifact(
            run_id=self.run_id,
            local_path=local_path,
            artifact_path=mlflow_write_dir,
        )

        # need to re-write storage path for saving to ArtifactCard
        filename = write_path.split("/")[-1]
        storage_uri = f"{self.artifact_path}/{mlflow_write_dir}/{filename}"

        return storage_uri

    def _get_mlflow_dir(self, filename: str) -> str:

        "Sets individual directories for all mlflow artifacts"
        if any(name in filename for name in DataArtifactNames):
            return MlFlowDirs.DATA_DIR.value

        if any(name in filename for name in ModelArtifactNames):
            return MlFlowDirs.MODEL_DIR.value

        return MlFlowDirs.ARTIFACT_DIR.value

    def list_files(self, storage_uri: str) -> FilePath:
        return [storage_uri]

    def store(self, storage_uri: str):
        return storage_uri

    @staticmethod
    def validate(storage_backend: str) -> bool:
        return storage_backend == StorageSystem.MLFLOW


StorageClientType = Union[LocalStorageClient, GCSFSStorageClient, MlFlowStorageClient]


class StorageClientGetter:
    @staticmethod
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
