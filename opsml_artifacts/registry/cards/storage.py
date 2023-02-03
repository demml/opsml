# pylint: disable=[import-outside-toplevel,import-error]

import tempfile
import uuid
from typing import Any, Dict, List, Optional, Tuple, cast

import gcsfs
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


class FileSystem:

    def create_save_path(self)-> Tuple[str, str]:
        raise NotImplementedError
    
    def create_tmp_path(self, tmp_dir:str):
        raise NotImplementedError
    
    def ist_files(self, storage_uri: str) -> List[str]:
        raise NotImplementedError
    
class GCSFileSystem:
    def __init__(self):
        pass
    storage_client = 
    def create_save_path(self)-> Tuple[str, str]:
        raise NotImplementedError
    
    def create_tmp_path(self, tmp_dir:str):
        raise NotImplementedError
    
    def ist_files(self, storage_uri: str) -> List[str]:
        raise NotImplementedError

class LocalFileSystem:
    def create_save_path(self)-> Tuple[str, str]:
        raise NotImplementedError
    
    def create_tmp_path(self, tmp_dir:str):
        raise NotImplementedError
    
    def ist_files(self, storage_uri: str) -> List[str]:
        raise NotImplementedError


# this become files system
class ArtifactStorage:
    def __init__(
        self,
        gcs_bucket: str,
        gcp_project: str,
        gcsfs_creds: str,
        save_info: Optional[SaveInfo] = None,
        file_suffix: Optional[str] = None,
        # storage_type: str # depends on client info local or gcs at the moment
    ):
        self.gcs_bucket = gcs_bucket
        self.storage_client = gcsfs.GCSFileSystem(
            project=gcp_project,
            token=gcsfs_creds,
        )
        self.file_suffix = None

        if save_info is not None:
            self.save_info = save_info

        if file_suffix is not None:
            self.file_suffix = file_suffix

    # create_storage_path
    def create_gcs_path(self) -> Tuple[str, str]:
        filename = uuid.uuid4().hex
        if self.file_suffix is not None:
            filename = f"{filename}.{self.file_suffix}"
        gcs_base_path = f"gs://{self.gcs_bucket}/{self.save_info.blob_path}"
        data_path = f"/{self.save_info.team}/{self.save_info.name}/version-{self.save_info.version}"

        return gcs_base_path + data_path + f"/{filename}", filename

    def create_tmp_path(self, tmp_dir: str):
        gcs_path, filename = self.create_gcs_path()
        local_path = f"{tmp_dir}/{filename}"

        return gcs_path, local_path

    def list_files(self, storage_uri: str) -> List[str]:
        bucket = storage_uri.split("/")[2]
        file_path = "/".join(storage_uri.split("/")[3:])
        files = [
            "gs://" + path
            for path in self.storage_client.ls(
                path=bucket,
                prefix=file_path,
            )
        ]

        return files

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
        save_info: Optional[SaveInfo] = None,
    ):
        super().__init__(save_info=save_info, file_suffix="parquet")

    def save_artifact(self, artifact: pa.Table) -> StoragePath:
        """Saves pyarrow table to gcs.

        Args:
            data (pa.Table): pyarrow table
        """

        gcs_uri, _ = self.create_gcs_path()
        pq.write_table(
            table=artifact,
            where=gcs_uri,
            filesystem=self.storage_client,
        )

        return StoragePath(
            uri=gcs_uri,
        )

    def load_artifact(self, storage_uri: str) -> pd.DataFrame:

        files = self.list_files(storage_uri=storage_uri)

        dataframe = (
            pq.ParquetDataset(
                path_or_paths=files,
                filesystem=self.storage_client,
            )
            .read()
            .to_pandas()
        )

        return dataframe

    @staticmethod
    def validate(artifact_type: str) -> bool:
        return artifact_type in [ArtifactStorageTypes.ARROW_TABLE, ArtifactStorageTypes.DATAFRAME]


class NumpyStorage(ArtifactStorage):
    def __init__(self, save_info: Optional[SaveInfo] = None):
        super().__init__(save_info=save_info, file_suffix="npy")

    def save_artifact(self, artifact: np.ndarray) -> StoragePath:  # type: ignore

        with tempfile.TemporaryDirectory() as tmpdirname:  # noqa
            gcs_uri, local_path = self.create_tmp_path(tmp_dir=tmpdirname)
            np.save(file=local_path, arr=artifact)
            self.storage_client.upload(lpath=local_path, rpath=gcs_uri)

        return StoragePath(
            uri=gcs_uri,
        )

    def load_artifact(self, storage_uri: str) -> np.ndarray:

        np_path = self.list_files(storage_uri=storage_uri)[0]
        with tempfile.NamedTemporaryFile(suffix=".npy") as tmpfile:  # noqa
            self.storage_client.download(rpath=np_path, lpath=tmpfile.name)
            data = np.load(tmpfile)

        return data

    @staticmethod
    def validate(artifact_type: str) -> bool:
        return artifact_type == ArtifactStorageTypes.NDARRAY


class JoblibStorage(ArtifactStorage):
    def __init__(self, save_info: Optional[SaveInfo] = None):
        super().__init__(save_info=save_info, file_suffix="joblib")

    def save_artifact(self, artifact: Any) -> StoragePath:

        with tempfile.TemporaryDirectory() as tmpdirname:  # noqa
            gcs_uri, local_path = self.create_tmp_path(tmp_dir=tmpdirname)
            joblib.dump(artifact, local_path)
            self.storage_client.upload(lpath=local_path, rpath=gcs_uri)

        return StoragePath(uri=gcs_uri)

    def load_artifact(self, storage_uri: str) -> Dict[str, Any]:
        joblib_path = self.list_files(storage_uri=storage_uri)[0]
        with tempfile.NamedTemporaryFile(suffix=self.file_suffix) as tmpfile:  # noqa
            self.storage_client.download(rpath=joblib_path, lpath=tmpfile.name)
            data = joblib.load(tmpfile)

        return data

    @staticmethod
    def validate(artifact_type: str) -> bool:
        return artifact_type not in DATA_ARTIFACTS


class TensorflowModelStorage(ArtifactStorage):
    def __init__(self, save_info: Optional[SaveInfo] = None):
        super().__init__(save_info=save_info, file_suffix=None)

    def save_artifact(self, artifact: Any) -> StoragePath:

        import tensorflow as tf

        artifact = cast(tf.keras.Model, artifact)

        with tempfile.TemporaryDirectory() as tmpdirname:  # noqa
            gcs_uri, local_path = self.create_tmp_path(tmp_dir=tmpdirname)
            artifact.save(local_path)
            self.storage_client.upload(lpath=local_path, rpath=f"{gcs_uri}/", recursive=True)

        return StoragePath(uri=gcs_uri)

    def load_artifact(self, storage_uri: str) -> Any:

        import tensorflow as tf

        model_path = self.list_files(storage_uri=storage_uri)[0]
        with tempfile.TemporaryDirectory() as tmpdirname:  # noqa
            self.storage_client.download(rpath=model_path, lpath=f"{tmpdirname}/", recursive=True)
            model = tf.keras.models.load_model(tmpdirname)

        return model

    @staticmethod
    def validate(artifact_type: str) -> bool:
        return artifact_type == ArtifactStorageTypes.TF_MODEL


def save_record_artifact_to_storage(
    artifact: Any,
    blob_path: str,
    name: str,
    version: int,
    team: str,
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
    save_info = SaveInfo(
        blob_path=blob_path,
        name=name,
        version=version,
        team=team,
    )
    return storage_type(save_info=save_info).save_artifact(artifact=artifact)


def load_record_artifact_from_storage(
    storage_uri: str,
    artifact_type: str,
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

    return storage_type().load_artifact(
        storage_uri=storage_uri,
    )
