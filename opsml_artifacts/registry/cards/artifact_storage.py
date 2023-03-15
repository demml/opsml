# pylint: disable=[import-outside-toplevel,import-error]

import tempfile
from typing import Any, Dict, List, Optional, Union
import json
import joblib
import yaml
import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import zarr

from opsml_artifacts.registry.cards.storage_system import StorageSystem
from opsml_artifacts.registry.cards.types import (
    DATA_ARTIFACTS,
    ArtifactStorageTypes,
    ArtifactStorageInfo,
    StorageClientProto,
    StoragePath,
)


class ArtifactStorage:
    """Artifact storage base class to inherit from"""

    def __init__(
        self,
        artifact_type: str,
        artifact_storage_info: ArtifactStorageInfo,
        file_suffix: Optional[str] = None,
    ):

        self.file_suffix = None
        self.artifact_type = artifact_type
        self.storage_client: StorageClientProto = artifact_storage_info.storage_client
        self.artifact_storage_info = artifact_storage_info

        if file_suffix is not None:
            self.file_suffix = str(file_suffix)

    def save_artifact_to_external(self, artifact: Any) -> str:
        """save artifact to external storage"""
        return "default"

    def save_artifact_to_local(self, artifact: Any) -> str:
        """save artifact to local storage"""
        return "default"

    def load_artifact(self, storage_uri: str) -> Any:
        """Loads data"""
        raise NotImplementedError

    def save_artifact(self, artifact: Any) -> StoragePath:

        if self.storage_client.backend == StorageSystem.LOCAL:
            storage_uri = self.save_artifact_to_local(artifact=artifact)
            return StoragePath(uri=storage_uri)

        storage_uri = self.save_artifact_to_external(artifact=artifact)
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
        artifact_storage_info: ArtifactStorageInfo,
    ):
        super().__init__(
            artifact_type=artifact_type,
            artifact_storage_info=artifact_storage_info,
            file_suffix="parquet",
        )

    def _write_pq_table(self, table: pa.Table, storage_uri: str):
        pq.write_table(
            table=table,
            where=storage_uri,
            filesystem=self.storage_client.client,
        )

    def save_artifact_to_local(self, artifact: pa.Table) -> StoragePath:

        storage_uri, _ = self.storage_client.create_save_path(
            artifact_storage_info=self.artifact_storage_info,
            file_suffix=self.file_suffix,
        )
        self._write_pq_table(table=artifact, storage_uri=storage_uri)

        return storage_uri

    def save_artifact_to_external(self, artifact: pa.Table) -> StoragePath:

        with self.storage_client.create_temp_save_path(self.artifact_storage_info, self.file_suffix) as temp_output:
            storage_uri, local_path = temp_output

            if self.storage_client.backend == StorageSystem.GCS:
                local_path = storage_uri

            self._write_pq_table(table=artifact, storage_uri=local_path)
            self.storage_client.post_process(storage_uri=local_path)

        return storage_uri

    def _load_arrow_from_files(self, files: List[str]) -> Union[pa.Table, pd.DataFrame, np.ndarray]:
        """Loads pyarrow data to original saved type

        Args:
            files (List[str]): List of filenames that make up the parquet dataset
        """
        pa_table: pa.Table = pq.ParquetDataset(
            path_or_paths=files,
            filesystem=self.storage_client.client,
        ).read()

        if self.artifact_type == ArtifactStorageTypes.DATAFRAME:
            return pa_table.to_pandas()

        return pa_table

    def load_artifact(self, storage_uri: str) -> Union[pd.DataFrame, np.ndarray]:
        files = self.storage_client.list_files(storage_uri=storage_uri)
        return self._load_arrow_from_files(files)

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
        artifact_storage_info: ArtifactStorageInfo,
    ):
        super().__init__(
            artifact_type=artifact_type,
            artifact_storage_info=artifact_storage_info,
            file_suffix="zarr",
        )

    def _write_with_storage_client(self, artifact: pa.Table) -> StoragePath:
        storage_uri, _ = self.storage_client.create_save_path(
            artifact_storage_info=self.artifact_storage_info,
            file_suffix=self.file_suffix,
        )
        store = self.storage_client.store(storage_uri=storage_uri)
        zarr.save(store, artifact)

        return StoragePath(uri=storage_uri)

    def _write_temp_and_upload(self, artifact: pa.Table) -> StoragePath:
        with self.storage_client.create_temp_save_path(self.artifact_storage_info, self.file_suffix) as temp_output:
            storage_uri, local_path = temp_output
            store = self.storage_client.store(storage_uri=storage_uri)
            zarr.save(store, artifact)

            self.storage_client.upload(local_path=local_path, write_path=storage_uri)

            return StoragePath(
                uri=storage_uri,
            )

    def save_artifact(self, artifact: np.ndarray) -> StoragePath:
        """Saves a numpy n-dimensional array as a Zarr array

        Args:
            artifact (np.ndarray): Numpy nd array

        Returns:
            StoragePath
        """

        if self.storage_client.backend in [StorageSystem.LOCAL, StorageSystem.GCS]:
            return self._write_with_storage_client(artifact=artifact)
        return self._write_temp_and_upload(artifact=artifact)

    def load_artifact(self, storage_uri: str) -> np.ndarray:
        """Loads a numpy ndarray from a zarr directory

        Args:
            storage_uri (str): Storage uri of zarr array

        Returns:
            numpy ndarray
        """

        files = self.storage_client.list_files(storage_uri=storage_uri)[0]
        store = self.storage_client.store(storage_uri=files)

        return zarr.load(store)

    @staticmethod
    def validate(artifact_type: str) -> bool:
        return artifact_type == ArtifactStorageTypes.NDARRAY


class JoblibStorage(ArtifactStorage):
    """Class that saves and loads a joblib object"""

    def __init__(
        self,
        artifact_type: str,
        artifact_storage_info: ArtifactStorageInfo,
    ):
        super().__init__(
            artifact_type=artifact_type,
            artifact_storage_info=artifact_storage_info,
            file_suffix="joblib",
        )

        # overwrite suffix
        self.file_suffix = self._get_file_suffix()
        print(self.artifact_storage_info.name, self.file_suffix)

    def _get_file_suffix(self) -> str:
        """Get file suffix based on specific card attributes"""

        if "api-def" in self.artifact_storage_info.name:
            return "json"

        return "joblib"

    def _save_json(self, artifact: Any, file_path: str):
        with open(file_path, "w", encoding="utf-8") as file_:
            return json.dump(artifact, file_)

    # def _save_yaml(self, artifact: Any, file_path: str):
    #    with open(file_path, "w") as out:
    #        yaml.safe_dump(data=artifact, stream=out)

    def _save_joblib(self, artifact: Any, file_path: str):
        joblib.dump(artifact, file_path)

    def _save_artifact(self, artifact: Any, file_path: str):
        if self.file_suffix == "json":
            self._save_json(artifact=artifact, file_path=file_path)

        self._save_joblib(artifact=artifact, file_path=file_path)

    def save_artifact_to_external(self, artifact: Any) -> str:
        with self.storage_client.create_temp_save_path(self.artifact_storage_info, self.file_suffix) as temp_output:
            storage_uri, local_path = temp_output
            self._save_artifact(artifact=artifact, file_path=local_path)
            self.storage_client.upload(local_path=local_path, write_path=storage_uri)

        return storage_uri

    def save_artifact_to_local(self, artifact: Any) -> str:
        storage_uri, _ = self.storage_client.create_save_path(
            artifact_storage_info=self.artifact_storage_info,
            file_suffix=self.file_suffix,
        )

        self._save_artifact(artifact=artifact, file_path=storage_uri)

        return storage_uri

    def _load_json(self, file_path: str) -> Any:
        with open(file_path) as json_file:
            return json.load(json_file)

    def _load_yaml(self, file_path: str) -> Any:
        with open(file_path, "r") as file_:
            return yaml.safe_load(file_)

    def _load_joblib(self, file_path: str) -> Any:
        joblib.load(file_path)

    def _load(self, file_path: str) -> Any:
        if "json" in file_path:
            self._load_json(file_path=file_path)
        if "yaml" in file_path:
            self._load_yaml(file_path=file_path)

        return self._load_joblib(file_path=file_path)

    def load_artifact(self, storage_uri: str) -> Dict[str, Any]:
        file_path = self.storage_client.list_files(storage_uri=storage_uri)[0]
        if self.storage_client.backend != StorageSystem.LOCAL:
            with tempfile.NamedTemporaryFile(suffix=self.file_suffix) as tmpfile:  # noqa
                self.storage_client.client.download(rpath=file_path, lpath=tmpfile.name)
                return self._load(file_path=file_path)

        return self._load(file_path=file_path)

    @staticmethod
    def validate(artifact_type: str) -> bool:
        return artifact_type not in DATA_ARTIFACTS


class TensorflowModelStorage(ArtifactStorage):
    """Class that saves and loads a tensorflow model"""

    def __init__(
        self,
        artifact_type: str,
        artifact_storage_info: ArtifactStorageInfo,
    ):
        super().__init__(
            artifact_type=artifact_type,
            artifact_storage_info=artifact_storage_info,
            file_suffix=None,
        )

    def save_artifact_to_external(self, artifact: Any) -> str:

        with self.storage_client.create_temp_save_path(self.artifact_storage_info, self.file_suffix) as temp_output:
            storage_uri, local_path = temp_output
            artifact.save(local_path)
            self.storage_client.upload(local_path=local_path, write_path=f"{storage_uri}/", recursive=True)

        return storage_uri

    def save_artifact_to_local(self, artifact: Any) -> str:
        storage_uri, _ = self.storage_client.create_save_path(
            artifact_storage_info=self.artifact_storage_info,
            file_suffix=self.file_suffix,
        )
        artifact.save(storage_uri)

        return storage_uri

    def load_artifact(self, storage_uri: str) -> Any:

        import tensorflow as tf

        model_path = self.storage_client.list_files(storage_uri=storage_uri)[0]

        if self.storage_client.backend != StorageSystem.LOCAL:
            with tempfile.TemporaryDirectory() as tmpdirname:  # noqa
                self.storage_client.client.download(rpath=model_path, lpath=f"{tmpdirname}/", recursive=True)
                return tf.keras.models.load_model(tmpdirname)
        return tf.keras.models.load_model(model_path)

    @staticmethod
    def validate(artifact_type: str) -> bool:
        return artifact_type == ArtifactStorageTypes.TF_MODEL


class PyTorchModelStorage(ArtifactStorage):
    """Class that saves and loads a pytorch model"""

    def __init__(
        self,
        artifact_type: str,
        artifact_storage_info: ArtifactStorageInfo,
    ):
        super().__init__(
            artifact_type=artifact_type,
            artifact_storage_info=artifact_storage_info,
            file_suffix="pt",
        )

    def save_artifact_to_external(self, artifact: Any) -> str:
        """Save artifact to external storage"""
        import torch

        with self.storage_client.create_temp_save_path(self.artifact_storage_info, self.file_suffix) as temp_output:
            storage_uri, local_path = temp_output
            torch.save(artifact, local_path)
            self.storage_client.upload(local_path=local_path, write_path=storage_uri)

        return storage_uri

    def save_artifact_to_local(self, artifact: Any) -> str:
        import torch

        storage_uri, _ = self.storage_client.create_save_path(
            artifact_storage_info=self.artifact_storage_info,
            file_suffix=self.file_suffix,
        )
        torch.save(artifact, storage_uri)

        return storage_uri

    def load_artifact(self, storage_uri: str) -> Dict[str, Any]:
        import torch

        model_path = self.storage_client.list_files(storage_uri=storage_uri)[0]

        if self.storage_client.backend != StorageSystem.LOCAL:
            with tempfile.NamedTemporaryFile(suffix=self.file_suffix) as tmpfile:  # noqa
                self.storage_client.client.download(rpath=model_path, lpath=tmpfile.name)
                return torch.load(tmpfile)

        return torch.load(model_path)

    @staticmethod
    def validate(artifact_type: str) -> bool:
        return artifact_type == ArtifactStorageTypes.PYTORCH


def save_record_artifact_to_storage(
    artifact: Any,
    artifact_storage_info: ArtifactStorageInfo,
    artifact_type: Optional[str] = None,
) -> StoragePath:

    _artifact_type: str = artifact_type or artifact.__class__.__name__

    print(artifact_storage_info.name, _artifact_type)
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
        artifact_storage_info=artifact_storage_info,
        artifact_type=_artifact_type,
    ).save_artifact(artifact=artifact)


def load_record_artifact_from_storage(
    artifact_type: str,
    artifact_storage_info: ArtifactStorageInfo,
):

    if not bool(artifact_storage_info.blob_path):
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
        artifact_storage_info=artifact_storage_info,
    ).load_artifact(storage_uri=artifact_storage_info.blob_path)
