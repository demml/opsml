from typing import Dict, cast

from opsml_artifacts.registry.cards.cards import PipelineCard
from opsml_artifacts.registry.cards.types import NON_PIPELINE_CARDS, CardNames
from opsml_artifacts.registry.sql.registry import ArtifactCardTypes, CardRegistry


class PipelineLoader:
    def __init__(self, pipeline_card_uid: str):
        """Loads all cards assoicated with a PipelineCard.

        Args:
            pipeline_card_uid (str) Uid of a PipelineCard
        """
        self.pipline_card = self._load_pipeline_card(uid=pipeline_card_uid)
        self._card_deck: Dict[str, ArtifactCardTypes] = {}

    def _load_pipeline_card(self, uid: str) -> PipelineCard:
        registry = CardRegistry(registry_name=CardNames.PIPELINE.value)
        loaded_card = registry.load_card(uid=uid)
        return cast(PipelineCard, loaded_card)

    def _load_cards(self, cards: Dict[str, str], card_type: str):
        registry = CardRegistry(registry_name=card_type)
        for card_name, card_uid in cards.items():
            self._card_deck[card_name] = registry.load_card(uid=card_uid)

    def load_cards(self):
        for card_type in NON_PIPELINE_CARDS:
            cards = getattr(self.pipline_card, f"{card_type}_card_uids")
            if bool(cards):
                self._load_cards(cards=cards, card_type=card_type)

        return self._card_deck
