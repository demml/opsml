import os
from typing import Any, Dict, cast

from pydantic import BaseModel

from opsml.helpers.logging import ArtifactLogger
from opsml.registry.cards.base import ArtifactCard
from opsml.registry.cards.types import DataCardMetadata, DataCardUris
from opsml.registry.data.formatter import check_data_schema
from opsml.registry.data.types import AllowedDataType
from opsml.registry.image.dataset import ImageDataset
from opsml.registry.storage.artifact_storage import load_record_artifact_from_storage
from opsml.registry.storage.storage_system import StorageClientType
from opsml.registry.storage.types import ArtifactStorageSpecs

logger = ArtifactLogger.get_logger()


class DataCardProto(BaseModel):
    data: Any
    feature_map: Dict[str, str]
    data_type: str
    uris: DataCardUris = DataCardUris()
    metadata: DataCardMetadata


class Downloader:
    def __init__(self, card: ArtifactCard, storage_client: StorageClientType):
        self.storage_client = storage_client
        self._card = card

    def download(self) -> None:
        raise NotImplementedError

    @staticmethod
    def validate(artifact_type: str) -> bool:
        raise NotImplementedError


class DataDownloader(Downloader):
    """Class for downloading data from storage"""

    @property
    def card(self) -> DataCardProto:
        return cast(DataCardProto, self._card)

    def download(self) -> None:
        if self.card.data is not None:
            logger.info("Data already exists")
            return

        data = load_record_artifact_from_storage(
            artifact_type=self.card.data_type,
            storage_client=self.storage_client,
            storage_spec=ArtifactStorageSpecs(
                save_path=self.card.uris.data_uri,
            ),
        )

        data = check_data_schema(
            data,
            self.card.feature_map,
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
    def card(self) -> DataCardProto:
        return cast(DataCardProto, self._card)

    def download(self) -> None:
        data = cast(ImageDataset, self.card.data)
        if os.path.exists(data.image_dir):
            logger.info("Image data already exists")
            return

        kwargs = {"image_dir": data.image_dir}

        record = load_record_artifact_from_storage(
            artifact_type=self.card.data_type,
            storage_client=self.storage_client,
            storage_spec=ArtifactStorageSpecs(
                save_path=self.card.uris.data_uri,
            ),
            **kwargs,
        )
        assert record is not None
        data = cast(ImageDataset, record)

    @staticmethod
    def validate(artifact_type: str) -> bool:
        return AllowedDataType.IMAGE in artifact_type


def download_object(card: ArtifactCard, artifact_type: str, storage_client: StorageClientType) -> None:
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
