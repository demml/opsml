from typing import cast
from dataclasses import asdict
from functools import cached_property
from opsml.registry.cards import ArtifactCard, RunCard
from opsml.registry.storage.storage_system import StorageClientType

from opsml.registry.cards.types import CardType


class CardArtifactDeleter:
    def __init__(self, card: ArtifactCard, storage_client: StorageClientType):
        """
        Parent class for saving artifacts belonging to cards

        Args:
            card:
                ArtifactCard with artifacts to save
            card_storage_info:
                Extra info to use with artifact storage
        """

        self._card = card
        self.storage_client = storage_client

    @cached_property
    def card(self):
        return self._card

    def delete_artifacts(self) -> None:
        """
        Delete artifacts for an ArtifactCard
        """
        for _, uri in asdict(self.card.metadata.uris).items():
            if uri is not None:
                self.storage_client.delete(uri)

    @staticmethod
    def validate(card_type: str) -> bool:
        raise NotImplementedError


class DataCardArtifactDeleter(CardArtifactDeleter):
    @staticmethod
    def validate(card_type: str) -> bool:
        return CardType.DATACARD.value in card_type


class ModelArtifactDeleter(CardArtifactDeleter):
    @staticmethod
    def validate(card_type: str) -> bool:
        return CardType.DATACARD.value in card_type


class RunCardArtifactDeleter(CardArtifactDeleter):
    @cached_property
    def card(self):
        return cast(RunCard, self._card)

    def delete_artifacts(self) -> None:
        """
        Delete artifacts for a RunCard
        """

        for _, uri in self.card.artifact_uris.items():
            if uri is not None:
                self.storage_client.delete(uri)

        if self.card.runcard_uri is not None:
            self.storage_client.delete(self.card.runcard_uri)

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
