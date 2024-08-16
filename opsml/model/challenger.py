# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
from typing import Any, Dict, List, Optional, Union, cast

from pydantic import BaseModel, ConfigDict, ValidationInfo, field_validator

from opsml.cards.model import ModelCard
from opsml.cards.run import RunCard
from opsml.helpers.logging import ArtifactLogger
from opsml.registry.registry import CardRegistries
from opsml.types import CardInfo, Metric

logger = ArtifactLogger.get_logger()

# User interfaces should primarily be checked at runtime


class BattleReport(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    champion_name: str
    champion_version: str
    champion_metric: Optional[Metric] = None
    challenger_metric: Optional[Metric] = None
    challenger_win: bool


MetricName = Union[str, List[str]]
MetricValue = Union[int, float, List[Union[int, float]]]


class ChallengeInputs(BaseModel):
    metric_name: MetricName
    metric_value: Optional[MetricValue] = None
    lower_is_better: Union[bool, List[bool]] = True

    @property
    def metric_names(self) -> List[str]:
        return cast(List[str], self.metric_name)

    @property
    def metric_values(self) -> List[Optional[Union[int, float]]]:
        return cast(List[Optional[Union[int, float]]], self.metric_value)

    @property
    def thresholds(self) -> List[bool]:
        return cast(List[bool], self.lower_is_better)

    @field_validator("metric_name")
    @classmethod
    def convert_name(cls, name: Union[List[str], str]) -> List[str]:
        if not isinstance(name, list):
            return [name]
        return name

    @field_validator("metric_value")
    @classmethod
    def convert_value(cls, value: Optional[MetricValue], info: ValidationInfo) -> List[Any]:
        data = info.data
        metric = cast(MetricName, data["metric_name"])
        nbr_metrics = len(metric)

        if value is not None:
            if not isinstance(value, list):
                metric_value = [value]
            else:
                metric_value = value
        else:
            metric_value = [None] * nbr_metrics  # type: ignore

        if len(metric_value) != nbr_metrics:
            raise ValueError("List of metric values must be the same length as metric names")

        return metric_value

    @field_validator("lower_is_better")
    @classmethod
    def convert_threshold(cls, threshold: Union[bool, List[bool]], info: ValidationInfo) -> List[bool]:
        data = info.data
        metric = cast(MetricName, data["metric_name"])
        nbr_metrics = len(metric)

        if not isinstance(threshold, list):
            _threshold = [threshold] * nbr_metrics
        else:
            _threshold = threshold

        if len(_threshold) != nbr_metrics:
            if len(_threshold) == 1:
                _threshold = _threshold * nbr_metrics
            else:
                raise ValueError("Length of lower_is_better must be the same length as number of metrics")

        return _threshold


class ModelChallenger:
    def __init__(self, challenger: ModelCard):
        """
        Instantiates ModelChallenger class

        Args:
            challenger:
                ModelCard of challenger

        """
        self._challenger = challenger
        self._challenger_metric: Optional[Metric] = None
        self._registries = CardRegistries()

    @property
    def challenger_metric(self) -> Metric:
        if self._challenger_metric is not None:
            return self._challenger_metric
        raise ValueError("Challenger metric not set")

    @challenger_metric.setter
    def challenger_metric(self, metric: Metric) -> None:
        self._challenger_metric = metric

    def _get_last_champion_record(self) -> Optional[Dict[str, Any]]:
        """Gets the previous champion record"""

        champion_records = self._registries.model.list_cards(
            name=self._challenger.name,
            repository=self._challenger.repository,
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

    def _get_runcard_metric(self, runcard_uid: str, metric_name: str) -> Metric:
        """
        Loads a RunCard from uid

        Args:
            runcard_uid:
                RunCard uid
            metric_name:
                Name of metric

        """
        runcard = cast(RunCard, self._registries.run.load_card(uid=runcard_uid))
        metric = runcard.get_metric(name=metric_name)

        if isinstance(metric, list):
            metric = metric[0]

        return metric

    def _battle(self, champion: CardInfo, champion_metric: Metric, lower_is_better: bool) -> BattleReport:
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
        if lower_is_better:
            challenger_win = self.challenger_metric.value < champion_metric.value
        else:
            challenger_win = self.challenger_metric.value > champion_metric.value
        return BattleReport.model_construct(
            champion_name=str(champion.name),
            champion_version=str(champion.version),
            champion_metric=champion_metric,
            challenger_metric=self.challenger_metric.model_copy(deep=True),
            challenger_win=challenger_win,
        )

    def _battle_last_model_version(self, metric_name: str, lower_is_better: bool) -> BattleReport:
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

        champion_metric = self._get_runcard_metric(runcard_uid=runcard_id, metric_name=metric_name)

        return self._battle(
            champion=CardInfo(
                name=champion_record.get("name"),
                version=champion_record.get("version"),
            ),
            champion_metric=champion_metric,
            lower_is_better=lower_is_better,
        )

    def _battle_champions(
        self,
        champions: List[CardInfo],
        metric_name: str,
        lower_is_better: bool,
    ) -> List[BattleReport]:
        """Loops through and creates a `BattleReport` for each champion"""
        battle_reports = []

        for champion in champions:
            champion_record = self._registries.model.list_cards(
                info=champion,
            )

            if not bool(champion_record):
                raise ValueError(f"Champion model does not exist. {champion}")

            champion_card = champion_record[0]
            runcard_uid = champion_card.get("runcard_uid")
            if runcard_uid is None:
                raise ValueError(f"No RunCard associated with champion: {champion}")

            champion_metric = self._get_runcard_metric(
                runcard_uid=runcard_uid,
                metric_name=metric_name,
            )

            # update name, repository and version in case of None
            champion.name = champion.name or champion_card.get("name")
            champion.repository = champion.repository or champion_card.get("repository")
            champion.version = champion.version or champion_card.get("version")

            battle_reports.append(
                self._battle(
                    champion=champion,
                    champion_metric=champion_metric,
                    lower_is_better=lower_is_better,
                )
            )
        return battle_reports

    def challenge_champion(
        self,
        metric_name: MetricName,
        metric_value: Optional[MetricValue] = None,
        champions: Optional[List[CardInfo]] = None,
        lower_is_better: Union[bool, List[bool]] = True,
    ) -> Dict[str, List[BattleReport]]:
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

        # validate inputs
        inputs = ChallengeInputs(
            metric_name=metric_name,
            metric_value=metric_value,
            lower_is_better=lower_is_better,
        )

        report_dict = {}

        for name, value, _lower_is_better in zip(
            inputs.metric_names,
            inputs.metric_values,
            inputs.thresholds,
        ):
            # get challenger metric
            if value is None:
                if self._challenger.metadata.runcard_uid is not None:
                    self.challenger_metric = self._get_runcard_metric(
                        self._challenger.metadata.runcard_uid, metric_name=name
                    )
                else:
                    raise ValueError("Challenger and champions must be associated with a registered RunCard")
            else:
                self.challenger_metric = Metric(name=name, value=value)

            if champions is None:
                report_dict[name] = [
                    self._battle_last_model_version(
                        metric_name=name,
                        lower_is_better=_lower_is_better,
                    )
                ]

            else:
                report_dict[name] = self._battle_champions(
                    champions=champions,
                    metric_name=name,
                    lower_is_better=_lower_is_better,
                )

        return report_dict
