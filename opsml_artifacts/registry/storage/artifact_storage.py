# pylint: disable=[import-outside-toplevel,import-error]

import json
import tempfile
from pathlib import Path
from typing import Any, Optional, Union

import joblib
import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import zarr

from opsml_artifacts.registry.cards.types import (
    DATA_ARTIFACTS,
    ArtifactStorageTypes,
    StoragePath,
)
from opsml_artifacts.registry.storage.storage_system import StorageClientType, StorageSystem, ArtifactClass
from opsml_artifacts.registry.storage.types import FilePath


class ArtifactStorage:
    """Artifact storage base class to inherit from"""

    def __init__(
        self,
        artifact_type: str,
        storage_client: StorageClientType,
        file_suffix: Optional[str] = None,
    ):

        self.file_suffix = None
        self.artifact_type = artifact_type
        self.storage_client = storage_client

        if file_suffix is not None:
            self.file_suffix = str(file_suffix)

    def _get_correct_storage_uri(self, storage_uri: str, tmp_uri: str, artifact_class: str) -> str:
        """Sets the correct storage uri based on the backend client"""

        if ArtifactClass(artifact_class) == ArtifactClass.DATA:
            if self.storage_client.backend in [StorageSystem.GCS, StorageSystem.LOCAL]:
                return storage_uri

            # this is mainly for writing data to proxies
            return tmp_uri

        else:
            if StorageSystem(self.storage_client.backend) == StorageSystem.LOCAL:
                return storage_uri

            return tmp_uri

    def _upload_artifact(
        self,
        file_path: str,
        storage_uri: str,
        artifact_class: str,
        recursive: bool = False,
    ) -> str:
        """Carries out post processing for proxy clients

        Args:
            file_path (str): File path used for writing
            storage_uri(str): Storage Uri. Can be the same as file_path
            artifact_class (str): Artifact class. Can be "data" or "other"
        """

        if ArtifactClass(artifact_class) == ArtifactClass.DATA:
            if self.storage_client.backend in [StorageSystem.GCS, StorageSystem.LOCAL]:
                return file_path

            # assume storage_uri is actually the tmp path
            return self.storage_client.upload(local_path=file_path)

        else:
            if StorageSystem(self.storage_client.backend) == StorageSystem.LOCAL:
                return storage_uri

            return self.storage_client.upload(
                local_path=file_path,
                write_path=storage_uri,
                recursive=recursive,
            )

    def _list_files(self, storage_uri: str) -> FilePath:
        """list files"""
        return self.storage_client.list_files(storage_uri=storage_uri)[0]

    def _load_artifact(self, file_path: FilePath) -> Any:
        raise NotImplementedError

    def load_artifact(self, storage_uri: str) -> Any:
        """Loads an artifact from file system"""

        files = self._list_files(storage_uri=storage_uri)
        return self._load_artifact(file_path=files)

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

    @staticmethod
    def validate(artifact_type: str) -> bool:
        """validate table type"""
        raise NotImplementedError


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
        )

    def _save_artifact(self, artifact: Any, storage_uri: str, tmp_uri: str) -> str:
        """Writes the artifact as a parquet table to the specified storage location

        Args:
            artifact (Parquet table): Parquet table to write
            storage_uri (str): Path to write to
            tmp_uri (str): Temporary uri to write to. This will be used
            for some storage client.

        Returns:
            Storage path
        """

        file_path = self._get_correct_storage_uri(
            storage_uri=storage_uri,
            tmp_uri=tmp_uri,
            artifact_class=ArtifactClass.DATA.value,
        )

        pq.write_table(
            table=artifact,
            where=file_path,
            filesystem=self.storage_client.client,
        )

        return self._upload_artifact(
            storage_uri=storage_uri,
            artifact_class=ArtifactClass.DATA.value,
        )

    def _load_artifact(self, file_path: FilePath) -> Union[pa.Table, pd.DataFrame, np.ndarray]:
        """Loads pyarrow data to original saved type

        Args:
            files (List[str]): List of filenames that make up the parquet dataset
        """
        pa_table: pa.Table = pq.ParquetDataset(
            path_or_paths=file_path,
            filesystem=self.storage_client.client,
        ).read()

        if self.artifact_type == ArtifactStorageTypes.DATAFRAME:
            return pa_table.to_pandas()

        return pa_table

    def _list_files(self, storage_uri) -> FilePath:
        return self.storage_client.list_files(storage_uri=storage_uri)

    def load_artifact(self, storage_uri: str) -> Any:
        files = self._list_files(storage_uri=storage_uri)
        return self._load_artifact(files)

    @staticmethod
    def validate(artifact_type: str) -> bool:
        return artifact_type in [
            ArtifactStorageTypes.ARROW_TABLE,
            ArtifactStorageTypes.DATAFRAME,
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
            file_suffix="zarr",
        )

    def _save_artifact(self, artifact: Any, storage_uri: str, tmp_uri: str) -> str:
        """Writes the artifact as a zarr array to the specified storage location

        Args:
            artifact (Numpy array): Numpy array to write
            storage_uri (str): Path to write to
            tmp_uri (str): Temporary uri to write to. This will be used
            for some storage client.

        Returns:
            Storage path
        """

        file_path = self._get_correct_storage_uri(
            storage_uri=storage_uri,
            tmp_uri=tmp_uri,
            artifact_class=ArtifactClass.DATA.value,
        )

        store = self.storage_client.store(storage_uri=storage_uri)
        zarr.save(store, artifact)

        return self._upload_artifact(
            file_path=file_path,
            storage_uri=storage_uri,
            artifact_class=ArtifactClass.DATA.value,
        )

    def _load_artifact(self, file_path: FilePath) -> np.ndarray:

        store = self.storage_client.store(storage_uri=str(file_path))

        return zarr.load(store)

    def load_artifact(self, storage_uri: str) -> Any:
        """Loads a numpy ndarray from a zarr directory

        Args:
            storage_uri (str): Storage uri of zarr array

        Returns:
            numpy ndarray
        """

        files = self._list_files(storage_uri=storage_uri)
        return self._load_artifact(file_path=files)

    @staticmethod
    def validate(artifact_type: str) -> bool:
        return artifact_type == ArtifactStorageTypes.NDARRAY


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
        )

    def _save_artifact(self, artifact: Any, storage_uri: str, tmp_uri: str) -> str:

        """Writes the artifact as a joblib file to a storage_uri

        Args:
            artifact (Any): Artifact to write to joblib
            storage_uri (str): Path to write to
            tmp_uri (str): Temporary uri to write to. This will be used
            for some storage client.

        Returns:
            Storage path
        """

        file_path = self._get_correct_storage_uri(
            storage_uri=storage_uri,
            tmp_uri=tmp_uri,
            artifact_class=ArtifactClass.OTHER.value,
        )
        joblib.dump(artifact, file_path)

        return self._upload_artifact(
            file_path=file_path,
            storage_uri=storage_uri,
            artifact_class=ArtifactClass.OTHER.value,
        )

    def _load_artifact(self, file_path: FilePath) -> Any:
        return joblib.load(file_path)

    def _list_files(self, storage_uri: str) -> FilePath:
        return self.storage_client.list_files(storage_uri=storage_uri)[0]

    @staticmethod
    def validate(artifact_type: str) -> bool:
        return artifact_type not in DATA_ARTIFACTS


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
        )

    def _save_artifact(self, artifact: Any, storage_uri: str, tmp_uri: str) -> str:

        """Writes the artifact as a json file to a storage_uri

        Args:
            artifact (Any): Artifact to write to json
            storage_uri (str): Path to write to
            tmp_uri (str): Temporary uri to write to. This will be used
            for some storage client.

        Returns:
            Storage path
        """

        file_path = self._get_correct_storage_uri(
            storage_uri=storage_uri,
            tmp_uri=tmp_uri,
            artifact_class=ArtifactClass.OTHER.value,
        )

        _path = Path(file_path)
        with _path.open("w", encoding="utf-8") as file_:
            file_.write(artifact)

        return self._upload_artifact(
            file_path=file_path,
            storage_uri=storage_uri,
            artifact_class=ArtifactClass.OTHER.value,
        )

    def _load_artifact(self, file_path: FilePath) -> Any:

        with open(str(file_path), encoding="utf-8") as json_file:
            return json.load(json_file)

    def _list_files(self, storage_uri: str) -> FilePath:
        return self.storage_client.list_files(storage_uri=storage_uri)[0]

    @staticmethod
    def validate(artifact_type: str) -> bool:
        return artifact_type == ArtifactStorageTypes.JSON


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
        )

    def _save_artifact(self, artifact: Any, storage_uri: str, tmp_uri: str) -> str:

        """Saves a tensorflow model

        Args:
            artifact (Any): Artifact to write to json
            storage_uri (str): Path to write to
            tmp_uri (str): Temporary uri to write to. This will be used
            for some storage client.

        Returns:
            Storage path
        """

        file_path = self._get_correct_storage_uri(
            storage_uri=storage_uri,
            tmp_uri=tmp_uri,
            artifact_class=ArtifactClass.OTHER.value,
        )

        artifact.save(storage_uri)

        self._upload_artifact(
            file_path=file_path,
            storage_uri=f"{storage_uri}/",
            artifact_class=ArtifactClass.OTHER.value,
            recursive=True,
        )

    def _list_files(self, storage_uri: str) -> FilePath:
        return self.storage_client.list_files(storage_uri=storage_uri)[0]

    def _load_artifact(self, file_path: FilePath):
        import tensorflow as tf

        return tf.keras.models.load_model(file_path)

    def load_artifact(self, storage_uri: str) -> Any:

        model_path = self._list_files(storage_uri=storage_uri)
        if self.storage_client.backend != StorageSystem.LOCAL:
            with tempfile.TemporaryDirectory() as tmpdirname:  # noqa
                self.storage_client.download(rpath=model_path, lpath=f"{tmpdirname}/", recursive=True)
                return self._load_artifact(tmpdirname)
        return self._load_artifact(model_path)

    @staticmethod
    def validate(artifact_type: str) -> bool:
        return artifact_type == ArtifactStorageTypes.TF_MODEL


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
        )

    def _save_artifact(self, artifact: Any, storage_uri: str, tmp_uri: str) -> str:

        """Saves a pytorch model

        Args:
            artifact (Any): Artifact to write to json
            storage_uri (str): Path to write to
            tmp_uri (str): Temporary uri to write to. This will be used
            for some storage client.

        Returns:
            Storage path
        """
        import torch

        file_path = self._get_correct_storage_uri(
            storage_uri=storage_uri,
            tmp_uri=tmp_uri,
            artifact_class=ArtifactClass.OTHER.value,
        )

        torch.save(artifact, file_path)

        self._upload_artifact(
            file_path=file_path,
            storage_uri=storage_uri,
            artifact_class=ArtifactClass.OTHER.value,
        )

    def _load_artifact(self, file_path: FilePath):
        import torch

        return torch.load(str(file_path))

    @staticmethod
    def validate(artifact_type: str) -> bool:
        return artifact_type == ArtifactStorageTypes.PYTORCH


def save_record_artifact_to_storage(
    artifact: Any,
    storage_client: StorageClientType,
    artifact_type: Optional[str] = None,
) -> StoragePath:

    _artifact_type: str = artifact_type or artifact.__class__.__name__

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
        for storage_type in ArtifactStorage.__subclasses__()
        if storage_type.validate(
            artifact_type=artifact_type,
        )
    )

    return storage_type(
        artifact_type=artifact_type,
        storage_client=storage_client,
    ).load_artifact(storage_uri=storage_client.storage_spec.save_path)
