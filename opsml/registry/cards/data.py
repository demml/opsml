# pylint: disable=too-many-lines
# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
from typing import Any, Dict, Optional, Union

from pydantic import field_validator, SerializeAsAny

from opsml.helpers.logging import ArtifactLogger
from opsml.helpers.utils import FileUtils
from opsml.registry.cards.base import ArtifactCard
from opsml.registry.data.interfaces import DataInterface
from opsml.registry.sql.records import DataRegistryRecord, RegistryRecord
from opsml.registry.types import CardType, DataCardMetadata

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

    interface: SerializeAsAny[DataInterface] = None
    metadata: DataCardMetadata = DataCardMetadata()

    def create_registry_record(self, **kwargs: Dict[str, Any]) -> RegistryRecord:
        """
        Creates required metadata for registering the current data card.
        Implemented with a DataRegistry object.

        Returns:
            Registry metadata

        """
        exclude_attr = {"data"}
        return DataRegistryRecord(**{**self.model_dump(exclude=exclude_attr), **kwargs})

    def add_info(self, info: Dict[str, Union[float, int, str]]) -> None:
        """
        Adds metadata to the existing DataCard metadata dictionary

        Args:
            info:
                Dictionary containing name (str) and value (float, int, str) pairs
                to add to the current metadata set
        """

        self.metadata.additional_info = {**info, **self.metadata.additional_info}

    @property
    def card_type(self) -> str:
        return CardType.DATACARD.value


# class Downloader:
#    def __init__(self, card: ArtifactCard):  # pylint: disable=redefined-outer-name
#        self._card = card
#
#    def download(self) -> None:
#        raise NotImplementedError
#
#    @staticmethod
#    def validate(artifact_type: str) -> bool:
#        raise NotImplementedError
#
#
# class DataProfileDownloader(Downloader):
#    @property
#    def card(self) -> DataCard:
#        return cast(DataCard, self._card)
#
#    def download(self) -> None:
#        """Downloads a data profile from storage"""
#
#        # data_profile = load_artifact_from_storage(
#        #    artifact_type=AllowedDataType.DICT,
#        #    storage_request=StorageRequest(
#        #        registry_type=self.card.card_type,
#        #        card_uid=self.card.uid,
#        #        uri_name=UriNames.PROFILE_URI,
#        #    ),
#        # )
#
#    #
#    # setattr(self.card, "data_profile", data_profile)
#
#    @staticmethod
#    def validate(artifact_type: str) -> bool:
#        return AllowedDataType.PROFILE in artifact_type
#
#
# class DataDownloader(Downloader):
#    """Class for downloading data from storage"""
#
#    @property
#    def card(self) -> DataCard:
#        return cast(DataCard, self._card)
#
#    def download(self) -> None:
#        if self.card.data is not None:
#            logger.info("Data already exists")
#            return
#
#    # data = load_artifact_from_storage(
#    #    artifact_type=self.card.metadata.data_type,
#    #    storage_request=StorageRequest(
#    #        registry_type=self.card.card_type,
#    #        card_uid=self.card.uid,
#    #        uri_name=UriNames.DATA_URI,
#    #    ),
#    # )
#
#    # data = check_data_schema(
#    #    data,
#    #    cast(Dict[str, str], self.card.metadata.feature_map),
#    #    self.card.metadata.data_type,
#    # )
#    # setattr(self.card, "data", data)
#
#    @staticmethod
#    def validate(artifact_type: str) -> bool:
#        return artifact_type in [
#            AllowedDataType.NUMPY,
#            AllowedDataType.PANDAS,
#            AllowedDataType.POLARS,
#            AllowedDataType.PYARROW,
#            AllowedDataType.DICT,
#        ]
#
#
# class ImageDownloader(Downloader):
#    @property
#    def card(self) -> DataCard:
#        return cast(DataCard, self._card)
#
#    def download(self) -> None:
#        data = cast(ImageDataset, self.card.data)
#        if os.path.exists(data.image_dir):
#            logger.info("Image data already exists")
#            return
#
#        # kwargs = {"image_dir": data.image_dir}
#
#    #
#    # load_artifact_from_storage(
#    #    artifact_type=self.card.metadata.data_type,
#    #    storage_request=StorageRequest(
#    #        registry_type=self.card.card_type,
#    #        card_uid=self.card.uid,
#    #        uri_name=UriNames.DATA_URI,
#    #    ),
#    #    **kwargs,
#    # )
#
#    @staticmethod
#    def validate(artifact_type: str) -> bool:
#        return AllowedDataType.IMAGE in artifact_type
#
#
# def download_object(
#    card: ArtifactCard,
#    artifact_type: str,
#    storage_client: client.StorageClient,
# ) -> None:
#    """Download data from storage
#
#    Args:
#        card:
#            Artifact Card
#        storage_client:
#            Storage client to use for downloading data
#        artifact_type:
#            Type of artifact to download
#    """
#    downloader = next(
#        downloader
#        for downloader in Downloader.__subclasses__()
#        if downloader.validate(
#            artifact_type=artifact_type,
#        )
#    )
#    return downloader(card=card, storage_client=storage_client).download()
#
