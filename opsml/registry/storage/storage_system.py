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
    S3StorageClientSettings,
    MlFlowClientProto,
    MlflowInfo,
    MlflowModel,
    MlflowModelFlavor,
    MlflowModelInfo,
    StorageSettings,
)

warnings.filterwarnings("ignore", message="Setuptools is replacing distutils.")
warnings.filterwarnings("ignore", message="Hint: Inferred schema contains integer*")

logger = ArtifactLogger.get_logger()


class StorageSystem(str, Enum):
    GCS = "gcs"
    S3 = "s3"
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

    def copy(self, read_path: str, write_path: str) -> Optional[str]:
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

    def copy(self, read_path: str, write_path: str) -> Optional[str]:
        """Copies object from read_path to write_path

        Args:
            read_path:
                Path to read from
            write_path:
                Path to write to
        """
        return self.client.copy(read_path, write_path, recursive=True)

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


class S3StorageClient(StorageClient):
    def __init__(
        self,
        storage_settings: StorageSettings,
    ):
        import s3fs

        storage_settings = cast(S3StorageClientSettings, storage_settings)
        client = s3fs.S3FileSystem()

        super().__init__(
            storage_settings=storage_settings,
            client=client,
            backend=StorageSystem.S3.value,
        )

    def copy(self, read_path: str, write_path: str) -> Optional[str]:
        """Copies object from read_path to write_path

        Args:
            read_path:
                Path to read from
            write_path:
                Path to write to
        """
        return self.client.copy(read_path, write_path, recursive=True)

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
        files = ["s3://" + path for path in self.client.ls(path=storage_uri)]
        return files

    def store(self, storage_uri: str, **kwargs) -> Any:
        """Create store for use with Zarr arrays"""
        import s3fs  # pylint: disable=import-outside-toplevel

        return s3fs.S3Map(storage_uri, s3=self.client, check=False)

    def download(self, rpath: str, lpath: str, recursive: bool = False, **kwargs) -> Optional[str]:
        loadable_path = self.client.download(rpath=rpath, lpath=lpath, recursive=recursive)

        if all(path is None for path in loadable_path):
            file_ = os.path.basename(rpath)
            return os.path.join(lpath, file_)
        return loadable_path

    @staticmethod
    def validate(storage_backend: str) -> bool:
        return storage_backend == StorageSystem.S3


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
        """Uploads local_path to write_path

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

    def copy(self, read_path: str, write_path: str) -> str:
        """Copies object from read_path to write_path

        Args:
            read_path:
                Path to read from
            write_path:
                Path to write to
        """
        if Path(read_path).is_dir():
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
        if Path(read_path).is_dir():
            return self.client.delete_dir(read_path)

        return self.client.delete_file(read_path)

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


class MlflowModelSaver:
    def __init__(
        self,
        model: Any,
        model_type: str,
        sample_data: Union[pd.DataFrame, NDArray, Dict[str, NDArray]],
        artifact_path: str,
        run_id: str,
        root_path: str,
        base_path_prefix: str,
        opsml_storage_client: StorageClient,
        mlflow_client: MlFlowClientProto,
    ):
        self.model = model
        self.model_type = model_type
        self.sample_data = sample_data
        self.artifact_path = artifact_path
        self.run_id = run_id
        self.root_path = root_path
        self.base_path_prefix = base_path_prefix
        self.opsml_storage_client = opsml_storage_client
        self.mlflow_client = mlflow_client

    def _get_model_signature(self):
        from mlflow.models.signature import infer_signature

        signature = infer_signature(model_input=self.sample_data)

        return signature

    def _upload_model_dir(self, local_dir: str) -> None:
        """Uploads model directory to storage

        Args:
            local_dir:
                Local directory to upload
        """
        write_path = os.path.join(self.root_path, self.artifact_path)
        write_path = MlflowStorageClient.swap_mlflow_root(
            base_path_prefix=self.base_path_prefix,
            rpath=write_path,
        )
        self.opsml_storage_client.upload(
            local_path=local_dir,
            write_path=write_path,
            recursive=True,
        )

    def _save_model(self, flavor: MlflowModelFlavor, local_dir: str, **kwargs) -> MlflowModel:
        """Saves model to local directory

        Args:
            flavor:
                Mlflow flavor to save model with

        Returns:
            Mlflow model
        """
        from mlflow.models import Model

        mlflow_model = Model(artifact_path=self.artifact_path, run_id=self.run_id)
        flavor.save_model(
            mlflow_model=mlflow_model,
            path=local_dir,
            signature=self._get_model_signature(),
            **kwargs,
        )

        return mlflow_model

    def _log_model(self, flavor: MlflowModelFlavor, **kwargs) -> MlflowModelInfo:
        """
        This code reproduces the mlflow.log_model function for most flavors. Function will
        save an mlflow model to a temp directory and then stream the directory to the
        appropriate storage location using the opsml storage client.

        Returns:
            filename:
                Name of the model file
        """
        # import
        with tempfile.TemporaryDirectory() as local_dir:
            mlflow_model = self._save_model(flavor=flavor, local_dir=local_dir, **kwargs)
            self._upload_model_dir(local_dir=local_dir)

        # record logged model
        self.mlflow_client._record_logged_model(self.run_id, mlflow_model)

        return mlflow_model.get_model_info()

    def log_model(self) -> str:
        raise NotImplementedError

    @staticmethod
    def validate(model_type: str) -> bool:
        raise NotImplementedError


class MlFlowSklearn(MlflowModelSaver):
    def log_model(self) -> str:
        "Log a sklearn model to mlflow"
        import mlflow

        model_info = self._log_model(flavor=mlflow.sklearn, sk_model=self.model)
        filename = model_info.flavors["python_function"]["model_path"]
        return filename

    @staticmethod
    def validate(model_type: str) -> bool:
        return model_type in SKLEARN_SUPPORTED_MODEL_TYPES


class MlFlowLightGBM(MlflowModelSaver):
    def log_model(self) -> str:
        "Log a lightgbm model to mlflow"
        import mlflow

        model_info = self._log_model(flavor=mlflow.lightgbm, lgb_model=self.model)
        filename = model_info.flavors["lightgbm"]["data"]

        return filename

    @staticmethod
    def validate(model_type: str) -> bool:
        return model_type in LIGHTGBM_SUPPORTED_MODEL_TYPES


class MlFlowPytorch(MlflowModelSaver):
    def log_model(self) -> str:
        """Log a pytorch model to mlflow"""
        import mlflow

        model_info = self._log_model(flavor=mlflow.pytorch, pytorch_model=self.model)
        dir_name = model_info.flavors["pytorch"]["model_data"]
        return f"{dir_name}/model.pth"

    @staticmethod
    def validate(model_type: str) -> bool:
        return model_type in [OnnxModelType.TRANSFORMER, OnnxModelType.PYTORCH]


class MlFlowTensorflow(MlflowModelSaver):
    def log_model(self) -> str:
        "Log a tensorflow model to mlflow"
        import mlflow

        model_info = self._log_model(flavor=mlflow.tensorflow, model=self.model)
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
    def run_id(self) -> str:
        if self._run_id is None:
            raise ValueError("No run_id set")
        return self._run_id

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

    @staticmethod
    def swap_mlflow_root(base_path_prefix: str, rpath: str) -> str:
        """Swaps mlflow path with storage path (used for onnx proto path)"""

        if "mlflow-artifacts:/" in rpath:
            path_to_file = "/".join(rpath.split("mlflow-artifacts:/")[1:])
            rpath = os.path.join(base_path_prefix, path_to_file)

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
        write_path = MlflowStorageClient.swap_mlflow_root(
            base_path_prefix=self.base_path_prefix,
            rpath=write_path,
        )

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
            run_id=self.run_id,
            root_path=self.artifact_path,
            base_path_prefix=self.base_path_prefix,
            opsml_storage_client=self.opsml_storage_client,
            mlflow_client=self.mlflow_client,
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
        """
        Uploads local artifact to mlflow

        Args:
            local_path:
                local path to file
            write_path:
                path to write to in mlflow
            recursive:
                whether to recursively upload a directory
            kwargs:
                additional kwargs to pass to upload
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
            storage_uri = MlflowStorageClient.swap_mlflow_root(
                base_path_prefix=self.base_path_prefix,
                rpath=storage_uri,
            )

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
                logger.error("Failed to retrieve parent and child save paths. Defaulting to random. {}", error)
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
    S3StorageClient,
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
