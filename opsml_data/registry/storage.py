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

from opsml_data.drift.data_drift import DriftReport
from opsml_data.helpers.settings import settings


class DataStoragePath(BaseModel):
    gcs_uri: str


class DataSaveInfo(BaseModel):
    blob_path: str
    data_name: str
    version: int
    team: str


class RegistryDataStorage:
    def __init__(
        self,
        save_info: Optional[DataSaveInfo] = None,
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
        data_path = f"/{self.save_info.team}/{self.save_info.data_name}/version-{self.save_info.version}"

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

    def save_data(
        self,
        data: Any,
    ):
        """Saves data"""

    def load_data(self, storage_uri: str):
        """Loads data"""

    @staticmethod
    def validate_type(data_type: str):
        """validate table type"""


class ParquetStorage(RegistryDataStorage):
    def __init__(
        self,
        save_info: Optional[DataSaveInfo] = None,
    ):
        super().__init__(save_info=save_info, file_suffix="parquet")

    def save_data(
        self,
        data: pa.Table,
    ) -> DataStoragePath:
        """Saves pyarrow table to gcs.

        Args:
            data (pa.Table): pyarrow table
        """

        gcs_uri, _ = self.create_gcs_path()
        pq.write_table(
            table=data,
            where=gcs_uri,
            filesystem=self.storage_client,
        )

        return DataStoragePath(
            gcs_uri=gcs_uri,
        )

    def load_data(self, storage_uri: str) -> pd.DataFrame:

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
    def validate_type(data_type: str):
        if data_type.lower() in ["table", "dataframe"]:
            return True
        return False


class NumpyStorage(RegistryDataStorage):
    def __init__(self, save_info: Optional[DataSaveInfo] = None):
        super().__init__(save_info=save_info, file_suffix="npy")

    def save_data(  # type: ignore
        self,
        data: np.ndarray,
    ) -> DataStoragePath:

        with tempfile.TemporaryDirectory() as tmpdirname:  # noqa
            gcs_uri, local_path = self.create_tmp_path(tmp_dir=tmpdirname)
            np.save(file=local_path, arr=data)
            self.storage_client.upload(lpath=local_path, rpath=gcs_uri)

        return DataStoragePath(
            gcs_uri=gcs_uri,
        )

    def load_data(self, storage_uri: str) -> np.ndarray:

        np_path = self.list_files(storage_uri=storage_uri)[0]
        with tempfile.NamedTemporaryFile(suffix=".npy") as tmpfile:  # noqa
            self.storage_client.download(rpath=np_path, lpath=tmpfile.name)
            data = np.load(tmpfile)

        return data

    @staticmethod
    def validate_type(data_type: str):
        if data_type.lower() == "ndarray":
            return True
        return False


class DriftStorage(RegistryDataStorage):
    def __init__(self, save_info: Optional[DataSaveInfo] = None):
        super().__init__(save_info=save_info, file_suffix="joblib")

    def save_data(  # type: ignore
        self,
        data: Dict[str, DriftReport],
    ) -> DataStoragePath:

        with tempfile.TemporaryDirectory() as tmpdirname:  # noqa
            gcs_uri, local_path = self.create_tmp_path(tmp_dir=tmpdirname)
            joblib.dump(data, local_path)
            self.storage_client.upload(lpath=local_path, rpath=gcs_uri)

        return DataStoragePath(
            gcs_uri=gcs_uri,
        )

    def load_data(self, storage_uri: str) -> Dict[str, DriftReport]:
        joblib_path = self.list_files(storage_uri=storage_uri)[0]
        with tempfile.NamedTemporaryFile(suffix=self.file_suffix) as tmpfile:  # noqa
            self.storage_client.download(rpath=joblib_path, lpath=tmpfile.name)
            data = joblib.load(tmpfile)

        return data

    @staticmethod
    def validate_type(data_type: str):
        if data_type.lower() == "dict":
            return True
        return False


def save_record_data_to_storage(
    data: Union[pa.Table, np.ndarray, Dict[str, DriftReport]],
    blob_path: str,
    data_name: str,
    version: int,
    team: str,
) -> DataStoragePath:

    data_type = data.__class__.__name__
    storage_type = next(
        storage_type
        for storage_type in RegistryDataStorage.__subclasses__()
        if storage_type.validate_type(
            data_type=data_type,
        )
    )
    save_info = DataSaveInfo(
        blob_path=blob_path,
        data_name=data_name,
        version=version,
        team=team,
    )
    return storage_type(save_info=save_info).save_data(data=data)


def load_record_data_from_storage(
    storage_uri: str,
    data_type: str,
):

    if not bool(storage_uri):
        return None

    storage_type = next(
        storage_type
        for storage_type in RegistryDataStorage.__subclasses__()
        if storage_type.validate_type(
            data_type=data_type,
        )
    )

    return storage_type().load_data(
        storage_uri=storage_uri,
    )
