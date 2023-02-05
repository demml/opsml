# pylint: disable=[import-outside-toplevel,import-error]

import tempfile
from typing import Any, Dict, Optional, cast, Type, Union, List

import joblib
import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

# from opsml_artifacts.helpers.settings import settings
from opsml_artifacts.registry.cards.types import (
    DATA_ARTIFACTS,
    ArtifactStorageTypes,
    SaveInfo,
    StoragePath,
)
from opsml_artifacts.registry.cards.storage_system import StorageClient, StorageSystem


class ArtifactStorage:
    def __init__(
        self,
        storage_client: Type[StorageClient],
        artifact_type: str,
        save_info: Optional[SaveInfo] = None,
        file_suffix: Optional[str] = None,
    ):

        self.file_suffix = None
        self.artifact_type = artifact_type
        self.storage_client = storage_client

        if save_info is not None:
            self.save_info = save_info

        if file_suffix is not None:
            self.file_suffix = file_suffix

    def save_artifact(self, artifact: Any) -> StoragePath:
        """Saves data"""
        raise NotImplementedError

    def load_artifact(self, storage_uri: str) -> Any:
        """Loads data"""
        raise NotImplementedError

    @staticmethod
    def validate(artifact_type: str) -> bool:
        """validate table type"""
        raise NotImplementedError


class ParquetStorage(ArtifactStorage):
    def __init__(
        self,
        artifact_type: str,
        storage_client: Type[StorageClient],
        save_info: Optional[SaveInfo] = None,
    ):
        super().__init__(
            artifact_type=artifact_type,
            storage_client=storage_client,
            save_info=save_info,
            file_suffix="parquet",
        )

    def save_artifact(self, artifact: pa.Table) -> StoragePath:
        """Saves pyarrow table to gcs.

        Args:
            data (pa.Table): pyarrow table
        """

        storage_uri, _ = self.storage_client.create_save_path(
            save_info=self.save_info,
            file_suffix=self.file_suffix,
        )
        pq.write_table(
            table=artifact,
            where=storage_uri,
            filesystem=self.storage_client.client,
        )

        return StoragePath(
            uri=storage_uri,
        )

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


class JoblibStorage(ArtifactStorage):
    def __init__(
        self,
        artifact_type: str,
        storage_client: Type[StorageClient],
        save_info: Optional[SaveInfo] = None,
    ):
        super().__init__(
            artifact_type=artifact_type,
            storage_client=storage_client,
            save_info=save_info,
            file_suffix="joblib",
        )

    def save_artifact(self, artifact: Any) -> StoragePath:

        if self.storage_client.backend != StorageSystem.LOCAL.name:
            with tempfile.TemporaryDirectory() as tmpdirname:  # noqa
                storage_uri, local_path = self.storage_client.create_tmp_path(
                    save_info=self.save_info,
                    file_suffix=self.file_suffix,
                    tmp_dir=tmpdirname,
                )
                joblib.dump(artifact, local_path)
                self.storage_client.client.upload(lpath=local_path, rpath=storage_uri)

        else:
            storage_uri, _ = self.storage_client.create_save_path(
                save_info=self.save_info,
                file_suffix=self.file_suffix,
            )
            joblib.dump(artifact, storage_uri)

        return StoragePath(uri=storage_uri)

    def load_artifact(self, storage_uri: str) -> Dict[str, Any]:
        joblib_path = self.storage_client.list_files(storage_uri=storage_uri)[0]
        if self.storage_client.backend != StorageSystem.LOCAL.name:
            with tempfile.NamedTemporaryFile(suffix=self.file_suffix) as tmpfile:  # noqa
                self.storage_client.client.download(rpath=joblib_path, lpath=tmpfile.name)
                return joblib.load(tmpfile)

        return joblib.load(joblib_path)

    @staticmethod
    def validate(artifact_type: str) -> bool:
        return artifact_type not in DATA_ARTIFACTS


class TensorflowModelStorage(ArtifactStorage):
    def __init__(
        self,
        artifact_type: str,
        storage_client: Type[StorageClient],
        save_info: Optional[SaveInfo] = None,
    ):
        super().__init__(
            artifact_type=artifact_type,
            storage_client=storage_client,
            save_info=save_info,
            file_suffix=None,
        )

    def save_artifact(self, artifact: Any) -> StoragePath:

        import tensorflow as tf

        artifact = cast(tf.keras.Model, artifact)

        if self.storage_client.backend != StorageSystem.LOCAL.name:
            with tempfile.TemporaryDirectory() as tmpdirname:  # noqa
                storage_uri, local_path = self.storage_client.create_tmp_path(
                    save_info=self.save_info,
                    file_suffix=self.file_suffix,
                    tmp_dir=tmpdirname,
                )
                artifact.save(local_path)
                self.storage_client.client.upload(lpath=local_path, rpath=f"{storage_uri}/", recursive=True)

        else:
            storage_uri, _ = self.storage_client.create_save_path(
                save_info=self.save_info,
                file_suffix=self.file_suffix,
            )
            artifact.save(storage_uri)

        return StoragePath(uri=storage_uri)

    def load_artifact(self, storage_uri: str) -> Any:

        import tensorflow as tf

        model_path = self.storage_client.list_files(storage_uri=storage_uri)[0]

        if self.storage_client.backend != StorageSystem.LOCAL.name:
            with tempfile.TemporaryDirectory() as tmpdirname:  # noqa
                self.storage_client.client.download(rpath=model_path, lpath=f"{tmpdirname}/", recursive=True)
                return tf.keras.models.load_model(tmpdirname)
        return tf.keras.models.load_model(model_path)

    @staticmethod
    def validate(artifact_type: str) -> bool:
        return artifact_type == ArtifactStorageTypes.TF_MODEL


def save_record_artifact_to_storage(
    artifact: Any,
    save_info: SaveInfo,
    storage_client: Type[StorageClient],
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
        save_info=save_info,
        artifact_type=_artifact_type,
        storage_client=storage_client,
    ).save_artifact(artifact=artifact)


def load_record_artifact_from_storage(
    storage_uri: str,
    artifact_type: str,
    storage_client: Type[StorageClient],
):

    if not bool(storage_uri):
        return None

    storage_type = next(
        storage_type
        for storage_type in ArtifactStorage.__subclasses__()
        if storage_type.validate(
            artifact_type=artifact_type,
        )
    )

    return storage_type(artifact_type=artifact_type, storage_client=storage_client).load_artifact(
        storage_uri=storage_uri,
    )
