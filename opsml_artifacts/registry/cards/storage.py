import tempfile
import uuid
from typing import Any, Dict, List, Optional, Tuple, Union

import gcsfs
import joblib
import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from pydantic import BaseModel

from opsml_artifacts.drift.data_drift import DriftReport
from opsml_artifacts.helpers.settings import settings


class StoragePath(BaseModel):
    gcs_uri: str


class SaveInfo(BaseModel):
    blob_path: str
    name: str
    version: int
    team: str


class ArtifactStorage:
    def __init__(
        self,
        save_info: Optional[SaveInfo] = None,
        file_suffix: Optional[str] = None,
    ):
        self.gcs_bucket = settings.gcs_bucket
        self.storage_client = gcsfs.GCSFileSystem(
            project=settings.gcp_project,
            token=settings.gcsfs_creds,
        )
        self.file_suffix = "placeholder"

        if save_info is not None:
            self.save_info = save_info

        if file_suffix is not None:
            self.file_suffix = file_suffix

    def create_gcs_path(self) -> Tuple[str, str]:
        filename = f"{uuid.uuid4().hex}.{self.file_suffix}"
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

    def save_artifact(
        self,
        artifact: Any,
    ):
        """Saves data"""

    def load_artifact(self, storage_uri: str):
        """Loads data"""

    @staticmethod
    def validate(artifact_type: str):
        """validate table type"""


class ParquetStorage(ArtifactStorage):
    def __init__(
        self,
        save_info: Optional[SaveInfo] = None,
    ):
        super().__init__(save_info=save_info, file_suffix="parquet")

    def save_artifact(
        self,
        artifact: pa.Table,
    ) -> StoragePath:
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
            gcs_uri=gcs_uri,
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
    def validate(artifact_type: str):
        if artifact_type in ["Table", "DataFrame"]:
            return True
        return False


class NumpyStorage(ArtifactStorage):
    def __init__(self, save_info: Optional[SaveInfo] = None):
        super().__init__(save_info=save_info, file_suffix="npy")

    def save_artifact(  # type: ignore
        self,
        artifact: np.ndarray,
    ) -> StoragePath:

        with tempfile.TemporaryDirectory() as tmpdirname:  # noqa
            gcs_uri, local_path = self.create_tmp_path(tmp_dir=tmpdirname)
            np.save(file=local_path, arr=artifact)
            self.storage_client.upload(lpath=local_path, rpath=gcs_uri)

        return StoragePath(
            gcs_uri=gcs_uri,
        )

    def load_artifact(self, storage_uri: str) -> np.ndarray:

        np_path = self.list_files(storage_uri=storage_uri)[0]
        with tempfile.NamedTemporaryFile(suffix=".npy") as tmpfile:  # noqa
            self.storage_client.download(rpath=np_path, lpath=tmpfile.name)
            data = np.load(tmpfile)

        return data

    @staticmethod
    def validate(artifact_type: str):
        if artifact_type == "ndarray":
            return True
        return False


class DictionaryStorage(ArtifactStorage):
    def __init__(self, save_info: Optional[SaveInfo] = None):
        super().__init__(save_info=save_info, file_suffix="joblib")

    def save_artifact(  # type: ignore
        self,
        artifact: Dict[str, DriftReport],
    ) -> StoragePath:

        with tempfile.TemporaryDirectory() as tmpdirname:  # noqa
            gcs_uri, local_path = self.create_tmp_path(tmp_dir=tmpdirname)
            joblib.dump(artifact, local_path)
            self.storage_client.upload(lpath=local_path, rpath=gcs_uri)

        return StoragePath(
            gcs_uri=gcs_uri,
        )

    def load_artifact(self, storage_uri: str) -> Dict[str, Any]:
        joblib_path = self.list_files(storage_uri=storage_uri)[0]
        with tempfile.NamedTemporaryFile(suffix=self.file_suffix) as tmpfile:  # noqa
            self.storage_client.download(rpath=joblib_path, lpath=tmpfile.name)
            data = joblib.load(tmpfile)

        return data

    @staticmethod
    def validate(artifact_type: str):
        if artifact_type == "dict":
            return True
        return False


def save_record_artifact_to_storage(
    artifact: Union[pa.Table, np.ndarray, Dict[str, DriftReport]],
    blob_path: str,
    name: str,
    version: int,
    team: str,
) -> StoragePath:

    artifact_type = artifact.__class__.__name__
    storage_type = next(
        storage_type
        for storage_type in ArtifactStorage.__subclasses__()
        if storage_type.validate(
            artifact_type=artifact_type,
        )
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
