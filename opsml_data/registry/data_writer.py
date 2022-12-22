import pyarrow.parquet as pq
import gcsfs
from typing import List, Union
from opsml_data.helpers.exceptions import NotOfCorrectType
from opsml_data.helpers.defaults import params
from opsml_data.registry.data_model import DataStoragePath, DataArtifacts
import pyarrow as pa
import numpy as np
import tempfile
import pandas as pd
import uuid


class DataWriter:
    def __init__(self):
        self.gcs_bucket = params.gcs_bucket
        self.blob_path = "data_registry"
        self.storage_client = gcsfs.GCSFileSystem(
            project=params.gcp_project,
            token=params.gcsfs_creds,
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
        pass

    def load_data(self, storage_uri: str):
        """Loads data"""
        pass

    def validate_type(data_type: str):
        """validate table type"""
        pass


class ParquetWriter(DataWriter):
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

        df = (
            pq.ParquetDataset(
                path_or_paths=files,
                filesystem=self.storage_client,
            )
            .read()
            .to_pandas()
        )

        return df

    def validate_type(data_type: str):
        if data_type == pa.Table:
            return True
        return False


class NumpyWriter(DataWriter):
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

    def validate_type(data_type: str):
        if data_type == np.ndarray:
            return True
        return False


class DataStorage:
    @staticmethod
    def save(
        data: Union[pa.Table, np.ndarray],
        data_name: str,
        version: int,
        team: str,
    ):

        data_type = type(data)
        writer = next(
            (
                writer
                for writer in DataWriter.__subclasses__()
                if writer.validate_type(
                    data_type=data_type,
                )
            ),
            None,
        )

        if not bool(writer):
            raise NotOfCorrectType(f"""Data type of {data_type} is not supported""")

        return writer().save_data(
            data=data,
            data_name=data_name,
            version=version,
            team=team,
        )

    @staticmethod
    def load(storage_uri: str, data_type: str):

        loader = next(
            (
                loader
                for loader in DataWriter.__subclasses__()
                if loader.validate_type(
                    data_type=data_type,
                )
            ),
            None,
        )

        if not bool(loader):
            raise NotOfCorrectType(f"""Data type of {data_type} is not supported""")

        return loader().load_data(storage_uri=storage_uri)
