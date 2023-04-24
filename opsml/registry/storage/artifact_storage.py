# pylint: disable=[import-outside-toplevel,import-error]

import json
import tempfile
from pathlib import Path
from typing import Any, Optional, Tuple, Union

import joblib
import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import zarr

from opsml.helpers.utils import all_subclasses
from opsml.registry.cards.types import StoragePath
from opsml.registry.storage.storage_system import (
    ArtifactClass,
    MlflowStorageClient,
    StorageClientType,
    StorageSystem,
    cleanup_files,
)
from opsml.registry.storage.types import ARTIFACT_TYPES, ArtifactStorageType, FilePath


class ArtifactStorage:
    """Artifact storage base class to inherit from"""

    def __init__(
        self,
        artifact_type: str,
        storage_client: StorageClientType,
        file_suffix: Optional[str] = None,
        artifact_class: Optional[str] = None,
    ):
        """Instantiates base ArtifactStorage class

        Args:
            artifact_type (str): Type of artifact. Examples include pyarrow Table, JSON, Pytorch
            artifact_class (str): Class that the artifact belongs to. This is either DATA or OTHER
            storage_client (StorageClientType): Backend storage client to use when saving and loading an artifact
            file_suffix (str): Optional suffix to use when saving and loading an artifact

        """

        self.file_suffix = None
        self.artifact_type = artifact_type
        self.storage_client = storage_client
        self.artifact_class = artifact_class

        if file_suffix is not None:
            self.file_suffix = str(file_suffix)

        if artifact_class is not None:
            self.artifact_class = str(artifact_class)

    @property
    def is_data(self):
        return self.artifact_class == ArtifactClass.DATA

    @property
    def is_storage_a_proxy(self):
        return self.storage_client.backend not in [StorageSystem.GCS, StorageSystem.LOCAL]

    @property
    def is_storage_local(self):
        return StorageSystem(self.storage_client.backend) == StorageSystem.LOCAL

    @property
    def storage_filesystem(self):
        return self.storage_client.client

    def _get_correct_storage_uri(self, storage_uri: str, tmp_uri: str) -> str:
        """Sets the correct storage uri based on the backend storage client"""

        if self.is_storage_local:
            return storage_uri

        # data artifacts need special handling since they use file systems directly
        if self.is_data and not self.is_storage_a_proxy:
            return storage_uri

        return tmp_uri

    def _upload_artifact(
        self,
        file_path: str,
        storage_uri: str,
        recursive: bool = False,
        **kwargs,
    ) -> str:
        """Carries out post processing for proxy clients

        Args:
            file_path (str): File path used for writing
            storage_uri(str): Storage Uri. Can be the same as file_path
            recursive (bool): Whether to recursively upload all files and folder in a given path
        """

        if self.is_storage_local:
            return storage_uri

        return self.storage_client.upload(
            local_path=file_path,
            write_path=storage_uri,
            recursive=recursive,
            **kwargs,
        )

    def _list_files(self, storage_uri: str) -> FilePath:
        """list files"""
        files = self.storage_client.list_files(storage_uri=storage_uri)

        if self.is_data:
            if not self.is_storage_a_proxy:
                return files
            return files[0]
        return files[0]

    def _load_artifact(self, file_path: FilePath) -> Any:
        raise NotImplementedError

    def _save_artifact(self, artifact: Any, storage_uri: str, tmp_uri: str):
        """Saves an artifact"""
        raise NotImplementedError

    def save_artifact(self, artifact: Any) -> StoragePath:

        with self.storage_client.create_temp_save_path(self.file_suffix) as temp_output:
            storage_uri, tmp_uri = temp_output
            storage_uri = self._save_artifact(
                artifact=artifact,
                storage_uri=storage_uri,
                tmp_uri=tmp_uri,
            )
            return StoragePath(uri=storage_uri)

    def _download_artifacts(
        self,
        files: FilePath,
        file_path: str,
        tmp_path: str,
    ) -> Any:
        if self.is_storage_local:
            return file_path

        loadable_path = self.storage_client.download(
            rpath=file_path,
            lpath=tmp_path,
            recursive=False,
            **{"files": files},
        )

        return loadable_path or tmp_path

    @cleanup_files
    def load_artifact(self, storage_uri: str) -> Tuple[Any, str]:
        files = self.storage_client.list_files(storage_uri=storage_uri)

        with tempfile.TemporaryDirectory() as tmpdirname:
            loadable_filepath = self._download_artifacts(
                files=files,
                file_path=storage_uri,
                tmp_path=tmpdirname,
            )

            artifact = self._load_artifact(file_path=loadable_filepath)

        return artifact, loadable_filepath

    @staticmethod
    def validate(artifact_type: str) -> bool:
        """validate table type"""
        raise NotImplementedError


class JoblibStorage(ArtifactStorage):
    """Class that saves and loads a joblib object"""

    def __init__(
        self,
        artifact_type: str,
        storage_client: StorageClientType,
    ):
        super().__init__(
            artifact_type=artifact_type,
            storage_client=storage_client,
            file_suffix="joblib",
            artifact_class=ArtifactClass.OTHER.value,
        )

    def _write_joblib(self, artifact: Any, file_path: FilePath):
        joblib.dump(artifact, file_path)

    def _write_artifact(self, artifact: Any, file_path: str, storage_uri: str):
        # hack for mlflow
        if isinstance(self.storage_client, MlflowStorageClient) and "trained-model" in storage_uri:
            return self._upload_artifact(
                file_path=file_path,
                storage_uri=storage_uri,
                **{"model": artifact, "model_type": self.artifact_type},
            )

        self._write_joblib(artifact=artifact, file_path=file_path)
        return self._upload_artifact(file_path=file_path, storage_uri=storage_uri)

    def _save_artifact(self, artifact: Any, storage_uri: str, tmp_uri: str) -> str:
        """
        Writes the artifact as a joblib file to a storage_uri

        Args:
            artifact:
                Artifact to write to joblib
            storage_uri:
                Path to write to
            tmp_uri:
                Temporary uri to write to. This will be used
                for some storage client.

        Returns:
            Storage path
        """

        file_path = self._get_correct_storage_uri(storage_uri=storage_uri, tmp_uri=tmp_uri)
        return self._write_artifact(artifact=artifact, file_path=file_path, storage_uri=storage_uri)

    def _load_artifact(self, file_path: FilePath) -> Any:
        return joblib.load(file_path)

    @staticmethod
    def validate(artifact_type: str) -> bool:
        return artifact_type not in ARTIFACT_TYPES


class ParquetStorage(ArtifactStorage):
    """Class that saves and loads a parquet file"""

    def __init__(
        self,
        artifact_type: str,
        storage_client: StorageClientType,
    ):
        super().__init__(
            artifact_type=artifact_type,
            storage_client=storage_client,
            file_suffix="parquet",
            artifact_class=ArtifactClass.DATA.value,
        )

    def _save_artifact(self, artifact: Any, storage_uri: str, tmp_uri: str) -> str:
        """
        Writes the artifact as a parquet table to the specified storage location

        Args:
            artifact:
                Parquet table to write
            storage_uri:
                Path to write to
            tmp_uri:
                Temporary uri to write to. This will be used
                for some storage client.

        Returns:
            Storage path
        """

        file_path = self._get_correct_storage_uri(storage_uri=storage_uri, tmp_uri=tmp_uri)

        pq.write_table(
            table=artifact,
            where=file_path,
            filesystem=self.storage_filesystem,
        )

        if self.is_storage_a_proxy:
            return self.storage_client.upload(
                local_path=file_path,
                write_path=storage_uri,
                **{"is_dir": False},
            )

        return file_path

    def _load_artifact(self, file_path: FilePath) -> Union[pa.Table, pd.DataFrame]:
        """
        Loads pyarrow data to original saved type

        Args:
            file_path:
                List of filenames that make up the parquet dataset

        Returns
            Pandas DataFrame or Pyarrow table
        """

        pa_table: pa.Table = pq.ParquetDataset(
            path_or_paths=file_path,
            filesystem=self.storage_filesystem,
        ).read()

        if self.artifact_type == ArtifactStorageType.DATAFRAME:
            return pa_table.to_pandas()

        return pa_table

    @staticmethod
    def validate(artifact_type: str) -> bool:
        return artifact_type in [
            ArtifactStorageType.ARROW_TABLE,
            ArtifactStorageType.DATAFRAME,
        ]


class NumpyStorage(ArtifactStorage):
    """Class that saves and loads a numpy ndarray"""

    def __init__(
        self,
        artifact_type: str,
        storage_client: StorageClientType,
    ):
        super().__init__(
            artifact_type=artifact_type,
            storage_client=storage_client,
            artifact_class=ArtifactClass.DATA.value,
        )

    def _save_artifact(self, artifact: Any, storage_uri: str, tmp_uri: str) -> str:
        """
        Writes the artifact as a zarr array to the specified storage location

        Args:
            artifact:
                Numpy array to write
            storage_uri:
                Path to write to
            tmp_uri:
                Temporary uri to write to. This will be used
                for some storage client.

        Returns:
            Storage path
        """

        file_path = self._get_correct_storage_uri(storage_uri=storage_uri, tmp_uri=tmp_uri)
        store = self.storage_client.store(storage_uri=file_path)
        zarr.save(store, artifact)

        if self.is_storage_a_proxy:
            return self.storage_client.upload(
                local_path=file_path,
                write_path=storage_uri,
                **{"is_dir": True},
            )

        return file_path

    def _load_artifact(self, file_path: FilePath) -> np.ndarray:
        store = self.storage_client.store(
            storage_uri=str(file_path),
            **{"store_type": "download"},
        )
        return zarr.load(store)

    @staticmethod
    def validate(artifact_type: str) -> bool:
        return artifact_type == ArtifactStorageType.NDARRAY


class JSONStorage(ArtifactStorage):
    """Class that saves and loads a joblib object"""

    def __init__(
        self,
        artifact_type: str,
        storage_client: StorageClientType,
    ):
        super().__init__(
            artifact_type=artifact_type,
            storage_client=storage_client,
            file_suffix="json",
            artifact_class=ArtifactClass.OTHER.value,
        )

    def _write_json(self, artifact: Any, file_path: FilePath):
        path_to_create = str(file_path)
        _path = Path(path_to_create)
        with _path.open("w", encoding="utf-8") as file_:
            file_.write(artifact)

    def _save_artifact(self, artifact: Any, storage_uri: str, tmp_uri: str) -> str:
        """Writes the artifact as a json file to a storage_uri

        Args:
            artifact:
                Artifact to write to json
            storage_uri:
                Path to write to
            tmp_uri:
                Temporary uri to write to. This will be used or some storage client.

        Returns:
            Storage path
        """

        file_path = self._get_correct_storage_uri(storage_uri=storage_uri, tmp_uri=tmp_uri)
        self._write_json(artifact=artifact, file_path=file_path)
        return self._upload_artifact(file_path=file_path, storage_uri=storage_uri)

    def _load_artifact(self, file_path: FilePath) -> Any:
        with open(str(file_path), encoding="utf-8") as json_file:
            return json.load(json_file)

    def _list_files(self, storage_uri: str) -> FilePath:
        return self.storage_client.list_files(storage_uri=storage_uri)[0]

    @staticmethod
    def validate(artifact_type: str) -> bool:
        return artifact_type == ArtifactStorageType.JSON


class TensorflowModelStorage(ArtifactStorage):
    """Class that saves and loads a tensorflow model"""

    def __init__(
        self,
        artifact_type: str,
        storage_client: StorageClientType,
    ):
        super().__init__(
            artifact_type=artifact_type,
            storage_client=storage_client,
            file_suffix=None,
            artifact_class=ArtifactClass.OTHER.value,
        )

    def _save_artifact(self, artifact: Any, storage_uri: str, tmp_uri: str) -> str:
        """Saves a tensorflow model

        Args:
            artifact:
                Artifact to write to json
            storage_uri:
                Path to write to
            tmp_uri:
                Temporary uri to write to. This will be used for some storage clients.

        Returns:
            Storage path
        """

        file_path = self._get_correct_storage_uri(storage_uri=storage_uri, tmp_uri=tmp_uri)
        if isinstance(self.storage_client, MlflowStorageClient) and "trained-model" in storage_uri:
            return self._upload_artifact(
                file_path=file_path,
                storage_uri=storage_uri,
                **{"model": artifact, "model_type": self.artifact_type},
            )

        artifact.save(file_path)

        return self._upload_artifact(
            file_path=file_path,
            storage_uri=storage_uri,
            recursive=True,
            **{"is_dir": True},
        )

    def _load_artifact(self, file_path: FilePath):
        import tensorflow as tf

        return tf.keras.models.load_model(file_path)

    @staticmethod
    def validate(artifact_type: str) -> bool:
        return artifact_type == ArtifactStorageType.TF_MODEL


class PyTorchModelStorage(ArtifactStorage):
    """Class that saves and loads a pytorch model"""

    def __init__(
        self,
        artifact_type: str,
        storage_client: StorageClientType,
    ):
        super().__init__(
            artifact_type=artifact_type,
            storage_client=storage_client,
            file_suffix="pt",
            artifact_class=ArtifactClass.OTHER.value,
        )

    def _save_artifact(self, artifact: Any, storage_uri: str, tmp_uri: str) -> str:
        """
        Saves a pytorch model

        Args:
            artifact:
                Artifact to write to json
            storage_uri:
                Path to write to
            tmp_uri:
                Temporary uri to write to. This will be used for some storage clients.

        Returns:
            Storage path
        """
        import torch

        file_path = self._get_correct_storage_uri(storage_uri=storage_uri, tmp_uri=tmp_uri)

        if isinstance(self.storage_client, MlflowStorageClient) and "trained-model" in storage_uri:
            return self._upload_artifact(
                file_path=file_path,
                storage_uri=storage_uri,
                **{"model": artifact, "model_type": self.artifact_type},
            )

        torch.save(artifact, file_path)

        return self._upload_artifact(file_path=file_path, storage_uri=storage_uri)

    def _load_artifact(self, file_path: FilePath):
        import torch

        return torch.load(str(file_path))

    @staticmethod
    def validate(artifact_type: str) -> bool:
        return artifact_type == ArtifactStorageType.PYTORCH


class LightGBMBooster(JoblibStorage):
    """Helper class only to be used with MLFLow"""

    def _load_artifact(self, file_path: FilePath) -> Any:
        if isinstance(self.storage_client, MlflowStorageClient):
            import lightgbm as lgb

            return lgb.Booster(model_file=file_path)

        return joblib.load(file_path)

    @staticmethod
    def validate(artifact_type: str) -> bool:
        return artifact_type == ArtifactStorageType.BOOSTER


def save_record_artifact_to_storage(
    artifact: Any,
    storage_client: StorageClientType,
    artifact_type: Optional[str] = None,
) -> StoragePath:
    _artifact_type: str = artifact_type or artifact.__class__.__name__

    print(artifact)

    storage_type = next(
        (
            storage_type
            for storage_type in ArtifactStorage.__subclasses__()
            if storage_type.validate(
                artifact_type=_artifact_type,
            )
        ),
        JoblibStorage,
    )

    return storage_type(
        storage_client=storage_client,
        artifact_type=_artifact_type,
    ).save_artifact(artifact=artifact)


def load_record_artifact_from_storage(artifact_type: str, storage_client: StorageClientType):
    if not bool(storage_client.storage_spec.save_path):
        return None

    storage_type = next(
        storage_type
        for storage_type in all_subclasses(ArtifactStorage)
        if storage_type.validate(
            artifact_type=artifact_type,
        )
    )

    return storage_type(
        artifact_type=artifact_type,
        storage_client=storage_client,
    ).load_artifact(storage_uri=storage_client.storage_spec.save_path)
