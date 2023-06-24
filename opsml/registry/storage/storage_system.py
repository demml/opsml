# pylint: disable=import-outside-toplevel,disable=invalid-envvar-value


import os
import re
import shutil
import tempfile
import uuid
from contextlib import contextmanager
from enum import Enum
from functools import wraps
from pathlib import Path
from typing import (
    IO,
    Any,
    Dict,
    Generator,
    Iterator,
    List,
    Optional,
    Tuple,
    Union,
    cast,
)

import pandas as pd
from numpy.typing import NDArray
from pyarrow.fs import LocalFileSystem

from opsml.helpers.logging import ArtifactLogger
from opsml.helpers.request_helpers import ApiRoutes
from opsml.helpers.utils import all_subclasses
from opsml.model.types import (
    LIGHTGBM_SUPPORTED_MODEL_TYPES,
    SKLEARN_SUPPORTED_MODEL_TYPES,
    OnnxModelType,
)
from opsml.registry.storage.types import (
    ApiStorageClientSettings,
    ArtifactStorageSpecs,
    FilePath,
    GcsStorageClientSettings,
    MlFlowClientProto,
    MlflowInfo,
    StorageSettings,
)

logger = ArtifactLogger.get_logger(__name__)


class StorageSystem(str, Enum):
    GCS = "gcs"
    LOCAL = "local"
    MLFLOW = "mlflow"
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


def cleanup_files(func):
    """Decorator for deleting files if needed"""

    @wraps(func)
    def wrapper(self, *args, **kwargs) -> Any:
        artifact, loadable_filepath = func(self, *args, **kwargs)

        if isinstance(loadable_filepath, list):
            loadable_filepath = loadable_filepath[0]

        if isinstance(loadable_filepath, str):
            if "temp" in loadable_filepath:  # make this better later
                file_dir = "/".join(loadable_filepath.split("/")[:-1])
                shutil.rmtree(file_dir, ignore_errors=True)
        return artifact

    return wrapper


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
        self._storage_spec: Optional[ArtifactStorageSpecs] = None

    @property
    def storage_spec(self) -> ArtifactStorageSpecs:
        return cast(ArtifactStorageSpecs, self._storage_spec)

    @storage_spec.setter
    def storage_spec(self, artifact_storage_spec):
        self._storage_spec = artifact_storage_spec

    def create_save_path(
        self,
        file_suffix: Optional[str] = None,
        extra_path: Optional[str] = None,
    ) -> Tuple[str, str]:
        filename = self.storage_spec.filename or uuid.uuid4().hex

        if file_suffix is not None:
            filename = f"{filename}.{str(file_suffix)}"

        if extra_path is not None:
            base_path = f"{self.base_path_prefix}/{self.storage_spec.save_path}/{extra_path}"

        else:
            base_path = f"{self.base_path_prefix}/{self.storage_spec.save_path}"

        return base_path + f"/{filename}", filename

    def create_tmp_path(
        self,
        tmp_dir: str,
        extra_path: Optional[str] = None,
        file_suffix: Optional[str] = None,
    ):
        base_path, filename = self.create_save_path(
            file_suffix=file_suffix,
            extra_path=extra_path,
        )
        local_path = f"{tmp_dir}/{filename}"

        return base_path, local_path

    @contextmanager
    def create_temp_save_path(
        self,
        file_suffix: Optional[str],
        extra_path: Optional[str],
    ) -> Generator[Tuple[Any, Any], None, None]:
        with tempfile.TemporaryDirectory() as tmpdirname:  # noqa
            storage_uri, local_path = self.create_tmp_path(
                file_suffix=file_suffix,
                extra_path=extra_path,
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

    def store(self, storage_uri: str, **kwargs):
        raise NotImplementedError

    def open(self, filename: str, mode: str):
        raise NotImplementedError

    def iterfile(self, file_path: str, chunk_size: int) -> Iterator[bytes]:
        with self.open(file_path, "rb") as file_:
            while chunk := file_.read(chunk_size):
                yield chunk

    def download(self, rpath: str, lpath: str, recursive: bool = False, **kwargs) -> Optional[str]:
        return self.client.download(rpath=rpath, lpath=lpath, recursive=recursive)

    def upload(
        self,
        local_path: str,
        write_path: str,
        recursive: bool = False,
        **kwargs,
    ) -> str:
        self.client.upload(lpath=local_path, rpath=write_path, recursive=recursive)
        return write_path

    def copy(self, read_path: str, write_path: str) -> None:
        raise ValueError("Storage class does not implement a copy method")

    def delete(self, read_path: str):
        raise ValueError("Storage class does not implement a delete method")

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
        return self.client.rm(path=read_path, recursive=True)

    def open(self, filename: str, mode: str) -> IO:
        return self.client.open(filename, mode)

    def list_files(self, storage_uri: str) -> FilePath:
        files = ["gs://" + path for path in self.client.ls(path=storage_uri)]
        return files

    def store(self, storage_uri: str, **kwargs) -> Any:
        """Create store for use with Zarr arrays"""
        import gcsfs  # pylint: disable=import-outside-toplevel

        return gcsfs.GCSMap(storage_uri, gcs=self.client, check=False)

    def download(self, rpath: str, lpath: str, recursive: bool = False, **kwargs) -> Optional[str]:
        loadable_path = self.client.download(rpath=rpath, lpath=lpath, recursive=recursive)

        if all(path is None for path in loadable_path):
            file_ = os.path.basename(rpath)
            return os.path.join(lpath, file_)
        return loadable_path

    @staticmethod
    def validate(storage_backend: str) -> bool:
        return storage_backend == StorageSystem.GCS


class LocalStorageClient(StorageClient):
    def create_save_path(
        self,
        file_suffix: Optional[str] = None,
        extra_path: Optional[str] = None,
    ) -> Tuple[str, str]:
        save_path, filename = super().create_save_path(
            file_suffix=file_suffix,
            extra_path=extra_path,
        )

        self._make_path("/".join(save_path.split("/")[:-1]))

        return save_path, filename

    def upload(self, local_path: str, write_path: str, recursive: bool = False, **kwargs) -> str:
        shutil.copy(local_path, write_path)
        return write_path

    def list_files(self, storage_uri: str) -> FilePath:
        if os.path.isdir(storage_uri):
            paths = []
            for path, _, files in os.walk(storage_uri):
                for filename in files:
                    paths.append(os.path.join(path, filename))
            return paths

        return [storage_uri]

    def open(self, filename: str, mode: str, encoding: Optional[str] = None) -> IO:
        return open(file=filename, mode=mode, encoding=encoding)

    def store(self, storage_uri: str, **kwargs):
        return storage_uri

    def copy(self, read_path: str, write_path: str) -> None:
        """Copies object from read_path to write_path

        Args:
            read_path:
                Path to read from
            write_path:
                Path to write to
        """
        if os.path.isdir(read_path):
            return shutil.copytree(read_path, write_path, dirs_exist_ok=True)
        return shutil.copyfile(read_path, write_path)

    def download(self, rpath: str, lpath: str, recursive: bool = False, **kwargs) -> Optional[str]:
        files = kwargs.get("files", None)

        if len(files) == 1:
            filename = os.path.basename(files[0])

            if os.path.isdir(lpath):
                lpath = os.path.join(lpath, filename)

            return self.copy(read_path=files[0], write_path=lpath)
        return self.copy(read_path=rpath, write_path=lpath)

    def delete(self, read_path: str) -> None:
        """Deletes files from a read path

        Args:
            read_path:
                Path to delete
        """
        return self.client.delete_dir(read_path)

    @staticmethod
    def validate(storage_backend: str) -> bool:
        return storage_backend == StorageSystem.LOCAL


class ApiStorageClient(LocalStorageClient):
    def __init__(self, storage_settings: StorageSettings):
        super().__init__(
            storage_settings=storage_settings,
            backend=StorageSystem.API.value,
        )

        storage_settings = cast(ApiStorageClientSettings, storage_settings)
        self.api_client = storage_settings.api_client

    def create_save_path(
        self,
        file_suffix: Optional[str] = None,
        extra_path: Optional[str] = None,
    ) -> Tuple[str, str]:
        filename = self.storage_spec.filename or uuid.uuid4().hex

        if file_suffix is not None:
            filename = f"{filename}.{str(file_suffix)}"

        if extra_path is not None:
            base_path = f"{self.base_path_prefix}/{self.storage_spec.save_path}/{extra_path}"

        else:
            base_path = f"{self.base_path_prefix}/{self.storage_spec.save_path}"

        return base_path + f"/{filename}", filename

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
        **kwargs,
    ) -> str:
        files = {"file": open(os.path.join(local_dir, filename), "rb")}  # pylint: disable=consider-using-with
        headers = {"Filename": filename, "WritePath": write_dir}

        response = self.api_client.stream_post_request(
            route=ApiRoutes.UPLOAD,
            files=files,
            headers=headers,
        )
        storage_uri = response.get("storage_uri")

        if storage_uri is not None:
            return storage_uri
        raise ValueError("No storage_uri found")

    def upload_single_file(self, local_path, write_path):
        filename = os.path.basename(local_path)

        # paths should be directories for uploading
        local_dir = os.path.dirname(local_path)
        write_dir = os.path.dirname(write_path)

        return self._upload_file(
            local_dir=local_dir,
            write_dir=write_dir,
            filename=filename,
        )

    def upload_directory(self, local_path, write_path):
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
        **kwargs,
    ) -> str:
        """
        Uploads local artifact to server
        Args:
            local_path:
                Local path to artifact(s)
            write_path:
                Path where current artifact has been saved to
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
            read_dir = os.path.dirname(file_)
            local_dir = read_dir.replace(rpath, lpath)
            filename = os.path.basename(file_)

            self.api_client.stream_download_file_request(
                route=ApiRoutes.DOWNLOAD_FILE,
                local_dir=local_dir,
                read_dir=read_dir,
                filename=filename,
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

    def download(self, rpath: str, lpath: str, recursive: bool = False, **kwargs) -> Optional[str]:
        files = kwargs.get("files", None)
        if len(files) == 1:
            return self.download_file(lpath=lpath, filename=files[0])
        return self.download_directory(rpath=rpath, lpath=lpath, files=files)

    def store(self, storage_uri: str, **kwargs):
        """Wrapper method needed for working with data artifacts (zarr)"""
        return storage_uri

    @staticmethod
    def validate(storage_backend: str) -> bool:
        return storage_backend == StorageSystem.API


class MlflowModelSaver:
    def __init__(
        self,
        model: Any,
        model_type: str,
        sample_data: Optional[Union[pd.DataFrame, NDArray, Dict[str, NDArray]]],
        artifact_path: str,
    ):
        self.model = model
        self.model_type = model_type
        self.sample_data = sample_data
        self.artifact_path = artifact_path

    def _get_model_signature(self):
        from mlflow.models.signature import infer_signature

        signature = infer_signature(model_input=self.sample_data)

        return signature

    def log_model(self) -> str:
        raise NotImplementedError

    @staticmethod
    def validate(model_type: str) -> bool:
        raise NotImplementedError


class MlFlowSklearn(MlflowModelSaver):
    def log_model(self) -> str:
        import mlflow

        signature = self._get_model_signature()

        model_info = mlflow.sklearn.log_model(
            sk_model=self.model,
            artifact_path=self.artifact_path,
            signature=signature,
            input_example=self.sample_data,
        )

        filename = model_info.flavors["python_function"]["model_path"]

        return filename

    @staticmethod
    def validate(model_type: str) -> bool:
        return model_type in SKLEARN_SUPPORTED_MODEL_TYPES


class MlFlowLightGBM(MlflowModelSaver):
    def log_model(self) -> str:
        import mlflow

        signature = self._get_model_signature()

        model_info = mlflow.lightgbm.log_model(
            lgb_model=self.model,
            artifact_path=self.artifact_path,
            signature=signature,
            input_example=self.sample_data,
        )

        filename = model_info.flavors["lightgbm"]["data"]

        return filename

    @staticmethod
    def validate(model_type: str) -> bool:
        return model_type in LIGHTGBM_SUPPORTED_MODEL_TYPES


class MlFlowPytorch(MlflowModelSaver):
    def log_model(self) -> str:
        import mlflow

        signature = self._get_model_signature()

        model_info = mlflow.pytorch.log_model(
            pytorch_model=self.model,
            artifact_path=self.artifact_path,
            signature=signature,
            input_example=self.sample_data,
        )

        dir_name = model_info.flavors["pytorch"]["model_data"]
        return f"{dir_name}/model.pth"

    @staticmethod
    def validate(model_type: str) -> bool:
        return model_type == OnnxModelType.PYTORCH


class MlFlowTensorflow(MlflowModelSaver):
    def log_model(self) -> str:
        import mlflow

        signature = self._get_model_signature()

        model_info = mlflow.tensorflow.log_model(
            model=self.model,
            artifact_path=self.artifact_path,
            signature=signature,
            input_example=self.sample_data,
        )

        dir_name = model_info.flavors["tensorflow"]["data"]
        return f"{dir_name}/model"

    @staticmethod
    def validate(model_type: str) -> bool:
        return model_type == OnnxModelType.TF_KERAS


class MlflowStorageClient(StorageClient):
    def __init__(
        self,
        storage_settings: StorageSettings,
    ):
        super().__init__(
            storage_settings=storage_settings,
            backend=StorageSystem.MLFLOW.value,
        )

        self._run_id: Optional[str] = None
        self._artifact_path: str = "mlflow-artifacts:/"
        self._mlflow_client: Optional[MlFlowClientProto] = None
        self._storage_spec = ArtifactStorageSpecs(save_path=self.base_path_prefix)
        self._opsml_storage_client: Optional[StorageClient] = None

    @property
    def opsml_storage_client(self) -> StorageClient:
        if self._opsml_storage_client is not None:
            return self._opsml_storage_client
        raise ValueError("No storage client found")

    @opsml_storage_client.setter
    def opsml_storage_client(self, storage_client: StorageClient) -> None:
        self._opsml_storage_client = storage_client

    def open(self, filename: str, mode: str):
        """not used"""

    @property
    def run_id(self) -> Optional[str]:
        return self._run_id

    @run_id.setter
    def run_id(self, run_id: Optional[str]):
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
        extra_path: Optional[str] = None,
    ) -> Tuple[str, str]:
        save_path, filename = super().create_save_path(
            file_suffix=file_suffix,
            extra_path=extra_path,
        )

        return save_path, filename

    def swap_proxy_root(self, rpath: str) -> str:
        """Swaps the realpath with the expected mlflow proxy path"""

        if "http" in self.mlflow_client.tracking_uri:
            path_to_file = "/".join(rpath.split(self.base_path_prefix)[1:]).lstrip("/")

            mlflow_path = os.path.normpath(
                os.path.join(
                    self.artifact_path,
                    path_to_file,
                )
            )

            return mlflow_path

        return rpath

    def swap_mlflow_root(self, rpath: str) -> str:
        """Swaps mlflow path with storage path (used for onnx proto path)"""

        if "mlflow-artifacts:/" in rpath:
            path_to_file = "/".join(rpath.split("mlflow-artifacts:/")[1:])
            rpath = os.path.join(self.base_path_prefix, path_to_file)

        return rpath

    def download(self, rpath: str, lpath: str, recursive: bool = False, **kwargs) -> Optional[str]:
        temp_path = lpath
        if not recursive:
            filename = os.path.basename(rpath)
            temp_path = f"{temp_path}/{filename}"

        abs_temp_path = temp_path
        file_path = self.opsml_storage_client.download(rpath, abs_temp_path, recursive, **kwargs)

        return file_path

    def _log_artifact(self, mlflow_info: MlflowInfo) -> str:
        write_path = f"{self.artifact_path}/{mlflow_info.artifact_path}/{mlflow_info.filename}"
        write_path = self.swap_mlflow_root(rpath=write_path)

        self.opsml_storage_client.upload(
            local_path=mlflow_info.local_path,
            write_path=write_path,
        )
        return mlflow_info.filename

    def _log_model(self, mlflow_info: MlflowInfo) -> str:
        model_type = str(mlflow_info.model_type)
        model_logger = next(
            (
                model_logger
                for model_logger in MlflowModelSaver.__subclasses__()
                if model_logger.validate(
                    model_type=model_type,
                )
            ),
            None,
        )

        if model_logger is None:
            raise ValueError(
                f"Failed to find appropriate mlflow model type saver for {mlflow_info.model_type}",
            )

        _logger = model_logger(
            model=mlflow_info.model,
            model_type=model_type,
            sample_data=self.storage_spec.sample_data,  # type: ignore
            artifact_path=mlflow_info.artifact_path,
        )

        return _logger.log_model()

    def log_artifact(self, mlflow_info: MlflowInfo) -> str:
        if mlflow_info.model is not None:
            return self._log_model(mlflow_info=mlflow_info)
        return self._log_artifact(mlflow_info=mlflow_info)

    def upload(
        self,
        local_path: str,
        write_path: str,
        recursive: bool = False,
        **kwargs,
    ) -> str:
        """Uploads local artifact to mlflow
        Args:
            storage_uri: Path where current artifact has been saved to
        """

        mlflow_write_dir = self._get_mlflow_dir(filename=write_path)

        mlflow_info = MlflowInfo(
            local_path=local_path,
            artifact_path=mlflow_write_dir,
            model=kwargs.get("model"),
            model_type=kwargs.get("model_type"),
            filename=write_path.split("/")[-1],
        )

        filename = self.log_artifact(mlflow_info=mlflow_info)

        # need to re-write storage path for saving to ArtifactCard
        storage_uri = f"{self.artifact_path}/{mlflow_info.artifact_path}/{filename}"

        if ModelArtifactNames.ONNX or ModelArtifactNames.TRAINED_MODEL in storage_uri:
            storage_uri = self.swap_mlflow_root(rpath=storage_uri)

        return storage_uri

    def _get_mlflow_dir(self, filename: str) -> str:
        "Sets individual directories for all mlflow artifacts"

        if "OPSML" in filename and "REGISTRY" in filename:
            # OPSML save paths always follow table/team/name/version/file save format

            file_splits = filename.split("/")
            try:
                # attempt to get parent and child directories
                for idx, split in enumerate(file_splits):
                    registry_name = extract_registry_name(split)

                    if registry_name is not None:
                        parent_dir = registry_name.lower()
                        parent_idx = idx

                if len(file_splits[parent_idx:]) > 1:
                    # attempt to get the card name
                    write_dir = os.path.normpath(f"{parent_dir}/" + "/".join(file_splits[parent_idx + 1 : -1]))

                else:
                    # default to unique id
                    write_dir = f"{parent_dir}/{uuid.uuid4().hex}"

            except Exception as error:  # pylint: disable=broad-exception-caught
                logger.error("Failed to retrieve parent and child save paths. Defaulting to random. %s", error)
                write_dir = f"misc/{uuid.uuid4().hex}"

            return write_dir.lower()

        return "misc"

    def list_files(self, storage_uri: str) -> FilePath:
        return self.opsml_storage_client.list_files(storage_uri)
        # return [storage_uri]

    def store(self, storage_uri: str, **kwargs):
        """Wrapper method needed for working with data artifacts and mlflow"""
        return storage_uri

    @staticmethod
    def validate(storage_backend: str) -> bool:
        return storage_backend == StorageSystem.MLFLOW


StorageClientType = Union[
    LocalStorageClient,
    GCSFSStorageClient,
    MlflowStorageClient,
    ApiStorageClient,
]


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
