from typing import List, Tuple
from opsml.registry.cards.cards import ArtifactCard, ModelCard, RunCard
from opsml.registry.cards.types import CardInfo
from opsml.registry.sql.registry import CardRegistries


class ModelAnalyzer:
    def __init__(self):
        self._registries = CardRegistries()
        self.model_deck = {}

    def _get_model(self, info: CardInfo) -> Tuple[ModelCard, str]:
        """
        Loads a model from CardInfo

        Args:
            info:
                ModelCard CardInfo

        Returns:
            `ModelCard` and unique name

        """
        modelcard: ModelCard = self._registry.load_card(info=info)
        unique_name = f"{modelcard.name}-{modelcard.team}-{modelcard.version}"
        self.model_deck[unique_name] = {"metrics": []}

        return modelcard, unique_name

    def _get_runcard_metrics(self, runcard_uid: str, name: str):
        """
        Loads a RunCard from uid

        Args:
            runcard_uid:
                RunCard uid

            name:
                Unique name of ModelCard that was loaded

        """

        runcard: RunCard = self._registries.run.load_card(uid=runcard_uid)
        for _, metric in runcard.metrics.items():
            if len(metric) == 1:  # only looking at single step metrics as of right now
                self.model_deck[name]["metrics"] = {
                    "name": metric.name,
                    "value": metric.value,
                }

    def compare_models(self, models: List[CardInfo]):
        """
        Takes a list of CardInfo pertaining to n models and compares their metrics.
        Provided CardInfo is used to load the ModelCard and it's associated RunCard where
        it's metrics are stored. RunCard metrics are parsed and added to a comparison object.

        Args:
            models:
                List of CardInfo related to models to compare.
        """
        # def parse model metrics
        for info in models:
            modelcard, unique_name = self._get_model(info=info)
            if modelcard.runcard_uid is not None:
                self._get_runcard_metrics(
                    runcard_uid=modelcard.runcard_uid,
                    name=unique_name,
                )

        # add comparison logic
