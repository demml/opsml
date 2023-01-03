import tempfile
import uuid
from typing import List, Union

import gcsfs
import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from opsml_data.helpers.exceptions import NotOfCorrectType
from opsml_data.helpers.settings import settings
from opsml_data.registry.models import DataStoragePath


class RegistryDataStorage:
    def __init__(self):
        self.gcs_bucket = settings.gcs_bucket
        self.blob_path = "data_registry"
        self.storage_client = gcsfs.GCSFileSystem(
            project=settings.gcp_project,
            token=settings.gcsfs_creds,
        )

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
        data: Union[pa.Table, np.ndarray],
        data_name: str,
        version: int,
        team: str,
    ):
        """Saves data"""

    def load_data(self, storage_uri: str):
        """Loads data"""

    @staticmethod
    def validate_type(data_type: str):
        """validate table type"""


class ParquetStorage(RegistryDataStorage):
    def save_data(
        self,
        data: pa.Table,
        data_name: str,
        version: int,
        team: str,
    ) -> DataStoragePath:
        """Saves pyarrow table to gcs.

        Args:
            data (pa.Table): pyarrow table
            data_name (str): Table name
            version (int): Version number
            team (str): Data science team
        """

        filename = f"{uuid.uuid4().hex}.parquet"
        gcs_uri = f"gs://{self.gcs_bucket}/{self.blob_path}/{team}/{data_name}/version-{version}/{filename}"  # noqa
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
    def save_data(
        self,
        data: np.ndarray,
        data_name: str,
        version: int,
        team: str,
    ) -> DataStoragePath:

        with tempfile.TemporaryDirectory() as tmpdirname:  # noqa
            filename = f"{uuid.uuid4().hex}.npy"
            gcs_uri = f"gs://{self.gcs_bucket}/{self.blob_path}/{team}/{data_name}/version-{version}/{filename}"
            local_path = f"{tmpdirname}/{filename}"
            np.save(file=local_path, arr=data)
            self.storage_client.upload(lpath=local_path, rpath=gcs_uri)

        return DataStoragePath(
            gcs_uri=gcs_uri,
        )

    def load_data(self, storage_uri: str):

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


def save_record_data_to_storage(
    data: Union[pa.Table, np.ndarray],
    data_name: str,
    version: int,
    team: str,
):

    data_type = data.__class__.__name__
    storage_type = next(
        (
            storage_type
            for storage_type in RegistryDataStorage.__subclasses__()
            if storage_type.validate_type(
                data_type=data_type,
            )
        ),
        None,
    )

    if not bool(storage_type):
        raise NotOfCorrectType(f"""Data type of {data_type} is not supported""")

    return storage_type().save_data(
        data=data,
        data_name=data_name,
        version=version,
        team=team,
    )


def load_record_data_from_storage(
    storage_uri: str,
    data_type: str,
):
    if not bool(storage_uri):
        return None

    storage_type = next(
        (
            storage_type
            for storage_type in RegistryDataStorage.__subclasses__()
            if storage_type.validate_type(
                data_type=data_type,
            )
        ),
        None,
    )

    if not bool(storage_type):
        raise NotOfCorrectType(f"""Data type of {data_type} is not supported""")

    return storage_type().load_data(storage_uri=storage_uri)
