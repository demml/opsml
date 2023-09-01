from typing import cast
import os
from opsml.helpers.logging import ArtifactLogger
from opsml.registry.storage.artifact_storage import load_record_artifact_from_storage
from opsml.registry.storage.storage_system import StorageClientType
from opsml.registry.cards import ArtifactCard, DataCard
from opsml.registry.data.formatter import check_data_schema
from opsml.registry.storage.types import ArtifactStorageSpecs
from opsml.registry.data.types import AllowedTableTypes
from opsml.registry.cards.types import ImageDataset

logger = ArtifactLogger.get_logger(__name__)


class Downloader:
    def __init__(self, card: ArtifactCard, storage_client: StorageClientType):
        self.storage_client = storage_client
        self._card = card

    def download(self):
        raise NotImplementedError

    @staticmethod
    def validate(artifact_type: str) -> bool:
        raise NotImplementedError


class DataDownloader(Downloader):
    """Class for downloading data from storage"""

    @property
    def card(self) -> DataCard:
        return cast(DataCard, self._card)

    def download(self) -> None:
        if self.card.data is not None:
            logger.info("Data already exists")
            return

        self.storage_client.storage_spec = ArtifactStorageSpecs(
            save_path=self.card.uris.data_uri,
        )

        data = load_record_artifact_from_storage(
            storage_client=self.s.storage_client,
            artifact_type=self.card.data_type,
        )
        data = check_data_schema(data, self.feature_map)
        setattr(self, "data", data)

    @staticmethod
    def validate(artifact_type: str) -> bool:
        return artifact_type in [
            AllowedTableTypes.NDARRAY.value,
            AllowedTableTypes.PANDAS_DATAFRAME.value,
            AllowedTableTypes.POLARS_DATAFRAME.value,
            AllowedTableTypes.ARROW_TABLE.value,
            AllowedTableTypes.DICTIONARY.value,
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
        self.storage_client.storage_spec = ArtifactStorageSpecs(
            save_path=self.card.uris.data_uri,
        )

        data = load_record_artifact_from_storage(
            storage_client=self.storage_client,
            artifact_type=self.card.data_type,
            **kwargs,
        )

    @staticmethod
    def validate(artifact_type: str) -> bool:
        return artifact_type == AllowedTableTypes.IMAGE_DATASET.value


def download_object(card: ArtifactCard, artifact_type: str, storage_client: StorageClientType) -> None:
    """Download data from storage

    Args:
        card:
            Artifact Card
        storage_client:
            Storage client to use for downloading data
    """
    downloader = next(
        downloader
        for downloader in Downloader.__subclasses__()
        if downloader.validate(
            artifact_type=artifact_type,
        )
    )
    return downloader(card=card, storage_client=storage_client).download()
