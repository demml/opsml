from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union, cast

from opsml.helpers.logging import ArtifactLogger
from opsml.helpers.utils import experimental_feature
from opsml.registry.cards.cards import ModelCard, RunCard
from opsml.registry.cards.types import CardInfo, Metric
from opsml.registry.sql.registry import CardRegistries

logger = ArtifactLogger.get_logger(__name__)


@dataclass
class BattleReport:
    champion_name: str
    champion_version: str
    challenger_win: bool


# eventually find a way to tell if a model has been deployed and use that for comparison as well
class ModelChallenger:
    @experimental_feature
    def __init__(self, challenger: ModelCard):
        """
        Instantiates ModelChallenger class

        Args:
            challenger:
                ModelCard of challenger

        """
        self._challenger = challenger
        self._registries = CardRegistries()
        self._challenger_metric: Optional[Metric] = None
        self._lower_is_better = True

    @property
    def challenger_metric(self) -> Metric:
        if self._challenger_metric is not None:
            return self._challenger_metric
        raise ValueError("Challenger metric not set")

    @challenger_metric.setter
    def challenger_metric(self, metric: Metric):
        self._challenger_metric = metric

    @property
    def lower_is_better(self) -> bool:
        return self._lower_is_better

    @lower_is_better.setter
    def lower_is_better(self, lower_is_better: bool) -> None:
        self._lower_is_better = lower_is_better

    def _get_last_champion_record(self) -> Optional[Dict[str, Any]]:
        # probably a better way to do this using tilde, caret or star
        """Gets the previous champion record"""

        champion_records = self._registries.model.list_cards(
            name=self._challenger.name,
            team=self._challenger.team,
            as_dataframe=False,
        )

        if not bool(champion_records):
            return None

        # indicates challenger has been registered
        if self._challenger.version is not None and len(champion_records) > 1:
            return champion_records[1]

        # account for cases where challenger is only model in registry
        champion_record = champion_records[0]
        if champion_record.get("version") == self._challenger.version:
            return None

        return champion_record

    def _get_runcard_metric(self, runcard_uid: str) -> Metric:
        """
        Loads a RunCard from uid

        Args:
            runcard_uid:
                RunCard uid

        """
        runcard: RunCard = self._registries.run.load_card(uid=runcard_uid)

        return cast(Metric, runcard.get_metric(name=self.challenger_metric.name))

    def battle(self, champion: CardInfo, champion_metric: Metric) -> BattleReport:
        """
        Runs a battle between champion and current challenger

        Args:
            champion:
                Champion record
            champion_metric:
                Champion metric from a runcard
            lower_is_better:
                Whether lower metric is preferred

        Returns:
            `BattleReport`

        """

        if self.lower_is_better:
            challenger_win = self.challenger_metric.value < champion_metric.value
        else:
            challenger_win = self.challenger_metric.value > champion_metric.value

        return BattleReport(
            champion_name=str(champion.name),
            champion_version=str(champion.version),
            challenger_win=challenger_win,
        )

    def _challenge_last_model_version(self) -> BattleReport:
        """Compares the last champion model to the current challenger"""

        champion_record = self._get_last_champion_record()

        if champion_record is None:
            logger.info("No previous model found. Challenger wins")

            return BattleReport(
                champion_name="No model",
                champion_version="No version",
                challenger_win=True,
            )

        runcard_id = champion_record.get("runcard_uid")
        if runcard_id is None:
            raise ValueError(f"No RunCard is associated with champion: {champion_record}")

        champion_metric = self._get_runcard_metric(runcard_uid=runcard_id)

        return self.battle(
            champion=CardInfo(
                name=champion_record.get("name"),
                version=champion_record.get("version"),
            ),
            champion_metric=champion_metric,
        )

    def _challenge_champions(self, champions: List[CardInfo]) -> List[BattleReport]:
        battle_reports = []
        for champion in champions:
            champion_record = self._registries.model.list_cards(info=champion, as_dataframe=False)

            if not bool(champion_record):
                raise ValueError(f"Champion model does not exist. {champion}")

            if champion_record[0].get("runcard_uid") is None:
                raise ValueError(f"No RunCard associated with champion: {champion}")

            champion_metric = self._get_runcard_metric(
                runcard_uid=champion_record[0].get("runcard_uid"),
            )

            battle_reports.append(
                self.battle(
                    champion=champion,
                    champion_metric=champion_metric,
                )
            )
        return battle_reports

    def challenge_champion(
        self,
        metric_name: str,
        metric_value: Union[int, float],
        lower_is_better: bool,
        champions: Optional[List[CardInfo]] = None,
    ) -> Union[BattleReport, List[BattleReport]]:
        """
        Challenges n champion models against the challenger model. If no champion is provided,
        the latest model version is used as a champion.

        Args:
            champions:
                Optional list of champion CardInfo
            metric_name:
                Name of metric to evaluate
            metric_value:
                Challenger metric value
            lower_is_better:
                Whether a lower metric value is better or not

        Returns
            `BattleReport`
        """
        # set lower is better
        self.lower_is_better = lower_is_better

        # get challenger metric
        self.challenger_metric = Metric(name=metric_name, value=metric_value)

        if champions is None:
            return self._challenge_last_model_version()

        battle_reports = self._challenge_champions(champions=champions)

        if len(battle_reports) > 1:
            return battle_reports
        return battle_reports[0]
