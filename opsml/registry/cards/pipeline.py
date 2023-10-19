# pylint: disable=too-many-lines
# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
from typing import List, Optional


from opsml.helpers.logging import ArtifactLogger
from opsml.registry.cards.base import ArtifactCard
from opsml.registry.cards.types import (
    CardType,
)
from opsml.registry.sql.records import (
    PipelineRegistryRecord,
    RegistryRecord,
)
from opsml.registry.utils.settings import settings

logger = ArtifactLogger.get_logger()
storage_client = settings.storage_client


class PipelineCard(ArtifactCard):
    """Create a PipelineCard from specified arguments

    Args:
        name:
            Pipeline name
        team:
            Team that this card is associated with
        user_email:
            Email to associate with card
        uid:
            Unique id (assigned if card has been registered)
        version:
            Current version (assigned if card has been registered)
        pipeline_code_uri:
            Storage uri of pipeline code
        datacard_uids:
            Optional list of DataCard uids to associate with pipeline
        modelcard_uids:
            Optional list of ModelCard uids to associate with pipeline
        runcard_uids:
            Optional list of RunCard uids to associate with pipeline

    """

    pipeline_code_uri: Optional[str] = None
    datacard_uids: List[Optional[str]] = []
    modelcard_uids: List[Optional[str]] = []
    runcard_uids: List[Optional[str]] = []

    def add_card_uid(self, uid: str, card_type: str):
        """
        Adds Card uid to appropriate card type attribute

        Args:
            uid:
                Card uid
            card_type:
                Card type. Accepted values are "data", "model", "run"
        """
        card_type = card_type.lower()
        if card_type.lower() not in [CardType.DATACARD.value, CardType.RUNCARD.value, CardType.MODELCARD.value]:
            raise ValueError("""Only 'model', 'run' and 'data' are allowed values for card_type""")

        current_ids = getattr(self, f"{card_type}card_uids")
        new_ids = [*current_ids, *[uid]]
        setattr(self, f"{card_type}card_uids", new_ids)

    def load_pipeline_code(self):
        raise NotImplementedError

    def create_registry_record(self) -> RegistryRecord:
        """Creates a registry record from the current PipelineCard"""
        return PipelineRegistryRecord(**self.model_dump())

    @property
    def card_type(self) -> str:
        return CardType.PIPELINECARD.value
