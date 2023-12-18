# pylint: disable=too-many-lines
# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
import os
from typing import Any, Dict, List, Optional, Union, cast

import pandas as pd
import polars as pl
from pydantic import field_validator, model_validator

from opsml.helpers.logging import ArtifactLogger
from opsml.helpers.utils import FileUtils
from opsml.profile.profile_data import DataProfiler, ProfileReport
from opsml.registry.cards.base import ArtifactCard
from opsml.registry.cards.types import CardType, DataCardMetadata
from opsml.registry.cards.validator import DataCardValidator
from opsml.registry.data.formatter import check_data_schema
from opsml.registry.data.splitter import DataHolder, DataSplit, DataSplitter
from opsml.registry.data.types import AllowedDataType, ValidData
from opsml.registry.image.dataset import ImageDataset
from opsml.registry.sql.records import DataRegistryRecord, RegistryRecord
from opsml.registry.storage import client
from opsml.registry.storage.artifact import load_artifact_from_storage
from opsml.registry.storage.types import ArtifactStorageSpecs

logger = ArtifactLogger.get_logger()


class DataCard(ArtifactCard):
    """Create a DataCard from your data.

    Args:
        data:
            Data to use for data card. Can be a pyarrow table, pandas dataframe, polars dataframe
            or numpy array
        name:
            What to name the data
        team:
            Team that this data is associated with
        user_email:
            Email to associate with data card
        dependent_vars:
            List of dependent variables. Can be string or index if using numpy
        data_splits:
            Optional list of `DataSplit`
        sql_logic:
            Dictionary of strings containing sql logic or sql files used to create the data
        version:
            DataCard version
        uid:
            Unique id assigned to the DataCard
        data_profile:
            Optional ydata-profiling `ProfileReport`

    Returns:
        DataCard

    """

    data: Optional[ValidData] = None
    data_splits: List[DataSplit] = []
    dependent_vars: List[Union[int, str]] = []
    sql_logic: Dict[str, str] = {}
    data_profile: Optional[ProfileReport] = None
    metadata: DataCardMetadata = DataCardMetadata()

    @model_validator(mode="before")
    @classmethod
    def check_data(cls, card_args: Dict[str, Any]) -> ValidData:
        """Custom data validator to check data type.

        Options for validation are:
            - Card can provide data, a data_uri or sql_logic (and any combination)
            - If a data_uri is present, data and sql_logic are not required (data has already been saved)
            - If data is not present and sql_logic is present, validation passes
            - If data is present, data types are checked
        """

        data = card_args.get("data")
        metadata = card_args.get("metadata")
        sql_logic: Dict[str, str] = card_args.get("sql_logic", {})

        validator = DataCardValidator(
            data=data,
            metadata=metadata,
            sql_logic=sql_logic,
        )

        if validator.has_data_uri:
            return card_args

        card_args["metadata"] = validator.get_metadata()
        return card_args

    @field_validator("data_profile", mode="before")
    @classmethod
    def _check_profile(cls, profile: Optional[ProfileReport]) -> Optional[ProfileReport]:
        if profile is not None:
            from ydata_profiling import ProfileReport as ydata_profile

            assert isinstance(profile, ydata_profile)
        return profile

    @field_validator("sql_logic", mode="before")
    @classmethod
    def _load_sql(cls, sql_logic: Dict[str, str]) -> Dict[str, str]:
        if not bool(sql_logic):
            return sql_logic

        for name, query in sql_logic.items():
            if ".sql" in query:
                try:
                    sql_path = FileUtils.find_filepath(name=query)
                    with open(sql_path, "r", encoding="utf-8") as file_:
                        query_ = file_.read()
                    sql_logic[name] = query_

                except Exception as error:
                    raise ValueError(f"Could not load sql file {query}. {error}") from error

        return sql_logic

    def split_data(self) -> Optional[DataHolder]:
        """
        Loops through data splits and splits data either by indexing or
        column values

        Example:

            ```python
            card_info = CardInfo(name="linnerrud", team="tutorial", user_email="user@email.com")
            data_card = DataCard(
                info=card_info,
                data=data,
                dependent_vars=["Pulse"],
                # define splits
                data_splits=[
                    {"label": "train", "indices": train_idx},
                    {"label": "test", "indices": test_idx},
                ],

            )

            splits = data_card.split_data()
            print(splits.train.X.head())

               Chins  Situps  Jumps
            0    5.0   162.0   60.0
            1    2.0   110.0   60.0
            2   12.0   101.0  101.0
            3   12.0   105.0   37.0
            4   13.0   155.0   58.0
            ```

        Returns
            Class containing data splits
        """
        if self.data is None:
            self.load_data()

        assert not isinstance(self.data, ImageDataset), "ImageDataset splits are not currently supported"

        if len(self.data_splits) > 0:
            data_holder = DataHolder()
            for data_split in self.data_splits:
                label, data = DataSplitter.split(
                    split=data_split,
                    dependent_vars=self.dependent_vars,
                    data=self.data,
                    data_type=self.metadata.data_type,
                )
                setattr(data_holder, label, data)

            return data_holder
        raise ValueError("No data splits provided")

    def load_data(self) -> None:
        """Loads DataCard data from storage"""

        # download data
        download_object(
            card=self,
            artifact_type=self.metadata.data_type,
            storage_client=client.storage_client,
        )

    def load_profile(self) -> None:
        """Loads DataCard data profile from storage"""

        if self.data_profile is not None:
            logger.info("Data profile already exists")
            return

        if self.metadata.uris.profile_uri is None:
            logger.info("DataCard is not associated with a data profile")
            return

        # download data profile
        download_object(
            card=self,
            artifact_type=AllowedDataType.PROFILE,
            storage_client=client.storage_client,
        )

    def create_registry_record(self) -> RegistryRecord:
        """
        Creates required metadata for registering the current data card.
        Implemented with a DataRegistry object.

        Returns:
            Registry metadata

        """
        exclude_attr = {"data"}
        return DataRegistryRecord(**self.model_dump(exclude=exclude_attr))

    def add_info(self, info: Dict[str, Union[float, int, str]]) -> None:
        """
        Adds metadata to the existing DataCard metadata dictionary

        Args:
            info:
                Dictionary containing name (str) and value (float, int, str) pairs
                to add to the current metadata set
        """

        self.metadata.additional_info = {**info, **self.metadata.additional_info}

    def add_sql(
        self,
        name: str,
        query: Optional[str] = None,
        filename: Optional[str] = None,
    ) -> None:
        """
        Adds a query or query from file to the sql_logic dictionary. Either a query or
        a filename pointing to a sql file are required in addition to a name.

        Args:
            name:
                Name for sql query
            query:
                SQL query
            filename:
                Filename of sql query
        """
        if query is not None:
            self.sql_logic[name] = query

        elif filename is not None:
            sql_path = str(FileUtils.find_filepath(name=filename))
            with open(sql_path, "r", encoding="utf-8") as file_:
                query = file_.read()
            self.sql_logic[name] = query

        else:
            raise ValueError("SQL Query or Filename must be provided")

    def create_data_profile(self, sample_perc: float = 1) -> ProfileReport:
        """Creates a data profile report

        Args:
            sample_perc:
                Percentage of data to use when creating a profile. Sampling is recommended for large dataframes.
                Percentage is expressed as a decimal (e.g. 1 = 100%, 0.5 = 50%, etc.)

        """

        if isinstance(self.data, (pl.DataFrame, pd.DataFrame)):
            if self.data_profile is None:
                self.data_profile = DataProfiler.create_profile_report(
                    data=self.data,
                    name=self.name,
                    sample_perc=min(sample_perc, 1),  # max of 1
                )
                return self.data_profile

            logger.info("Data profile already exists")
            return self.data_profile

        raise ValueError("A pandas dataframe type is required to create a data profile")

    @property
    def card_type(self) -> str:
        return CardType.DATACARD.value


class Downloader:
    def __init__(
        self, card: ArtifactCard, storage_client: client.StorageClientType
    ):  # pylint: disable=redefined-outer-name
        self.storage_client = storage_client
        self._card = card

    def download(self) -> None:
        raise NotImplementedError

    @staticmethod
    def validate(artifact_type: str) -> bool:
        raise NotImplementedError


class DataProfileDownloader(Downloader):
    @property
    def card(self) -> DataCard:
        return cast(DataCard, self._card)

    def download(self) -> None:
        """Downloads a data profile from storage"""
        data_profile = load_artifact_from_storage(
            artifact_type=AllowedDataType.DICT,
            storage_client=self.storage_client,
            storage_spec=ArtifactStorageSpecs(
                save_path=self.card.metadata.uris.profile_uri,
            ),
        )

        setattr(self.card, "data_profile", data_profile)

    @staticmethod
    def validate(artifact_type: str) -> bool:
        return AllowedDataType.PROFILE in artifact_type


class DataDownloader(Downloader):
    """Class for downloading data from storage"""

    @property
    def card(self) -> DataCard:
        return cast(DataCard, self._card)

    def download(self) -> None:
        if self.card.data is not None:
            logger.info("Data already exists")
            return

        data = load_artifact_from_storage(
            artifact_type=self.card.metadata.data_type,
            storage_client=self.storage_client,
            storage_spec=ArtifactStorageSpecs(
                save_path=self.card.metadata.uris.data_uri,
            ),
        )

        data = check_data_schema(
            data,
            cast(Dict[str, str], self.card.metadata.feature_map),
            self.card.metadata.data_type,
        )
        setattr(self.card, "data", data)

    @staticmethod
    def validate(artifact_type: str) -> bool:
        return artifact_type in [
            AllowedDataType.NUMPY,
            AllowedDataType.PANDAS,
            AllowedDataType.POLARS,
            AllowedDataType.PYARROW,
            AllowedDataType.DICT,
        ]


class ImageDownloader(Downloader):
    @property
    def card(self) -> DataCard:
        return cast(DataCard, self._card)

    def download(self) -> None:
        data = cast(ImageDataset, self.card.data)
        if os.path.exists(data.image_dir):
            logger.info("Image data already exists")
            return

        kwargs = {"image_dir": data.image_dir}

        load_artifact_from_storage(
            artifact_type=self.card.metadata.data_type,
            storage_client=self.storage_client,
            storage_spec=ArtifactStorageSpecs(
                save_path=self.card.metadata.uris.data_uri,
            ),
            **kwargs,
        )

    @staticmethod
    def validate(artifact_type: str) -> bool:
        return AllowedDataType.IMAGE in artifact_type


def download_object(
    card: ArtifactCard,
    artifact_type: str,
    storage_client: client.StorageClientType,  # pylint: disable=redefined-outer-name
) -> None:
    """Download data from storage

    Args:
        card:
            Artifact Card
        storage_client:
            Storage client to use for downloading data
        artifact_type:
            Type of artifact to download
    """
    downloader = next(
        downloader
        for downloader in Downloader.__subclasses__()
        if downloader.validate(
            artifact_type=artifact_type,
        )
    )
    return downloader(card=card, storage_client=storage_client).download()
