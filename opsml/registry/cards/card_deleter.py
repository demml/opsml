from functools import cached_property
from typing import cast

from opsml.registry.cards.base import ArtifactCard
from opsml.registry.cards.data import DataCard
from opsml.registry.cards.model import ModelCard
from opsml.registry.cards.run import RunCard
from opsml.registry.cards.types import CardType
from opsml.registry.storage.client import StorageClientType


#
# TODO(@damon): This entire class can go - move to ArtifactCard.delete.
#
# TODO(@damon); Just delete the tree under the card (also note that linked URIs
# are going to be invalidated as well (i.e., models "data_card_uri" should be
# zero'd out if the data card associated with the model is deleted - no idea how
# to do this yet..
#
class CardArtifactDeleter:
    def __init__(self, card: ArtifactCard, storage_client: StorageClientType):
        """
        Parent class for deleting artifacts belonging to cards

        Args:
            card:
                ArtifactCard with artifacts to delete

            storage_client:
                The client which will perform the actual deletion
        """

        self._card = card
        self.storage_client = storage_client

    @cached_property
    def card(self) -> ArtifactCard:
        return self._card

    def delete_artifacts(self) -> None:
        raise NotImplementedError

    def _delete_artifacts(self, read_path: str) -> None:
        """Find common directory from path and delete files"""

        # TODO(@damon): Delete everything under the card's uri

        path_split = read_path.split("/")
        version_index = path_split.index(f"v{self.card.version}")
        dir_path = "/".join(path_split[: version_index + 1])
        self.storage_client.delete(dir_path)

    @staticmethod
    def validate(card_type: str) -> bool:
        raise NotImplementedError


class DataCardArtifactDeleter(CardArtifactDeleter):
    @cached_property
    def card(self) -> DataCard:
        return cast(DataCard, self._card)

    @staticmethod
    def validate(card_type: str) -> bool:
        return CardType.DATACARD.value in card_type

    def delete_artifacts(self) -> None:
        """
        Delete artifacts for a DataCard from the common directory path
        """
        self._delete_artifacts(
            read_path=str(self.card.metadata.uris.datacard_uri),
        )


class ModelArtifactDeleter(CardArtifactDeleter):
    @cached_property
    def card(self) -> ModelCard:
        return cast(ModelCard, self._card)

    @staticmethod
    def validate(card_type: str) -> bool:
        return CardType.MODELCARD.value in card_type

    def delete_artifacts(self) -> None:
        """
        Delete artifacts for a DataCard from the common directory path
        """
        self._delete_artifacts(
            read_path=str(self.card.metadata.uris.modelcard_uri),
        )


class RunCardArtifactDeleter(CardArtifactDeleter):
    @cached_property
    def card(self) -> RunCard:
        return cast(RunCard, self._card)

    def delete_artifacts(self) -> None:
        """
        Delete artifacts for a RunCard
        """

        self._delete_artifacts(read_path=cast(str, self.card.runcard_uri))

    @staticmethod
    def validate(card_type: str) -> bool:
        return CardType.RUNCARD.value in card_type


def delete_card_artifacts(card: ArtifactCard, storage_client: StorageClientType) -> None:
    """Deletes a given ArtifactCard's artifacts from a file system

    Args:
        card:
            ArtifactCard to save
        storage_client:
            StorageClient to use to save artifacts

    """
    card_deleter = next(
        (
            card_deleter
            for card_deleter in CardArtifactDeleter.__subclasses__()
            if card_deleter.validate(card_type=card.__class__.__name__.lower())
        ),
        None,
    )

    if card_deleter is not None:
        deleter = card_deleter(card=card, storage_client=storage_client)
        deleter.delete_artifacts()
