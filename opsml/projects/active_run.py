# pylint: disable=invalid-envvar-value
# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from pathlib import Path
from typing import Any, Dict, Optional, Union, cast

from opsml.cards.base import ArtifactCard
from opsml.cards.data import DataCard
from opsml.cards.model import ModelCard
from opsml.cards.run import RunCard
from opsml.helpers.logging import ArtifactLogger
from opsml.registry.registry import CardRegistries, CardRegistry
from opsml.registry.semver import VersionType
from opsml.storage import client
from opsml.types import ArtifactUris, CardInfo, CardType, Metrics, Params, SaveName

logger = ArtifactLogger.get_logger()


# dataclass inheritance doesnt handle default vals well for <= py3.9
class RunInfo:
    def __init__(
        self,
        runcard: RunCard,
        run_id: str,
        run_name: Optional[str] = None,
    ):
        self.storage_client = client.storage_client
        self.registries = CardRegistries()
        self.runcard = runcard
        self.run_id = run_id
        self.run_name = run_name


class CardHandler:
    """DRY helper class for ActiveRun and OpsmlProject"""

    @staticmethod
    def register_card(
        registries: CardRegistries,
        card: ArtifactCard,
        version_type: VersionType = VersionType.MINOR,
    ) -> None:
        """Registers and ArtifactCard"""

        registry: CardRegistry = getattr(registries, card.card_type)
        registry.register_card(card=card, version_type=version_type)

    @staticmethod
    def load_card(registries: CardRegistries, registry_name: str, info: CardInfo) -> ArtifactCard:
        """Loads an ArtifactCard"""

        registry: CardRegistry = getattr(registries, registry_name)
        return registry.load_card(name=info.name, version=info.version, uid=info.uid)

    @staticmethod
    def update_card(registries: CardRegistries, card: ArtifactCard) -> None:
        """Updates an ArtifactCard"""
        registry: CardRegistry = getattr(registries, card.card_type)
        registry.update_card(card=card)


class ActiveRun:
    def __init__(self, run_info: RunInfo):
        """
        Run object that handles logging artifacts, metrics, cards, and tags for a given run of a Project

        Args:
            run_info:
                Run info for a given active run
        """
        self._info = run_info
        self._active = True  # should be active upon instantiation
        self.runcard = run_info.runcard

    @property
    def run_id(self) -> str:
        """Id for current run"""
        return self._info.run_id

    @property
    def run_name(self) -> Optional[str]:
        """Name for current run"""
        return self._info.run_name

    @property
    def active(self) -> bool:
        return self._active

    def _verify_active(self) -> None:
        if not self.active:
            raise ValueError("""Run is not active""")

    def add_tag(self, key: str, value: str) -> None:
        """
        Adds a tag to the current run

        Args:
            key:
                Name of the tag
            value:
                Value to associate with tag
        """
        self.runcard.add_tag(key=key, value=value)

    def add_tags(self, tags: Dict[str, Union[str, Optional[str]]]) -> None:
        """
        Adds a tag to the current run

        Args:
            tags:
                Dictionary of key, value tags

        """
        for key, value in tags.items():
            self.add_tag(key=key, value=cast(str, value))

    def register_card(self, card: ArtifactCard, version_type: VersionType = VersionType.MINOR) -> None:
        """
        Register a given artifact card.

        Args:
            card:
                The card to register
            version_type:
                Version type for increment. Options are "major", "minor" and
                "patch". Defaults to "minor".
        """
        self._verify_active()

        # add runuid to card
        if isinstance(card, (DataCard, ModelCard)):
            card.metadata.runcard_uid = self.runcard.uid

        CardHandler.register_card(
            registries=self._info.registries,
            card=card,
            version_type=version_type,
        )

        tag_key = f"{card.card_type}:{card.name}"
        self.add_tag(key=tag_key, value=str(card.version))

        # add uid to RunCard
        self.runcard.add_card_uid(card_type=card.card_type, uid=str(card.uid))

    def load_card(self, registry_name: str, info: CardInfo) -> ArtifactCard:
        """
        Loads an ArtifactCard.

        Args:
            registry_name:
                Type of card to load (data, model, run, pipeline)
            info:
                Card information to retrieve. `uid` takes precedence if it
                exists. If the optional `version` is specified, that version
                will be loaded. If it doesn't exist, the most recent version will
                be loaded.

        Returns
            `ArtifactCard`
        """
        card_type = CardType(registry_name.lower()).value

        return CardHandler.load_card(registries=self._info.registries, registry_name=card_type, info=info)

    def log_artifact_from_file(
        self,
        name: str,
        local_path: Union[str, Path],
        artifact_path: Optional[Union[str, Path]] = None,
    ) -> None:
        """
        Log a local file or directory to the opsml server and associate with the current run.

        Args:
            name:
                Name to assign to artifact(s)
            local_path:
                Local path to file or directory. Can be string or pathlike object
            artifact_path:
                Optional path to store artifact in opsml server. If not provided, 'artifacts' will be used
        """

        self._verify_active()

        lpath = Path(local_path)
        rpath = self.runcard.uri / (artifact_path or SaveName.ARTIFACTS.value)

        if lpath.is_file():
            rpath = rpath / lpath.name

        self._info.storage_client.put(lpath, rpath)
        self.runcard._add_artifact_uri(  # pylint: disable=protected-access
            name=name,
            local_path=lpath.as_posix(),
            remote_path=rpath.as_posix(),
        )

    def log_metric(
        self,
        key: str,
        value: float,
        timestamp: Optional[int] = None,
        step: Optional[int] = None,
    ) -> None:
        """
        Log a metric for a given run

        Args:
            key:
                Metric name
            value:
                Metric value
            timestamp:
                Optional time indicating metric creation time
            step:
                Optional step in training when metric was created

        """
        self._verify_active()
        self.runcard.log_metric(
            key=key,
            value=value,
            timestamp=timestamp,
            step=step,
        )

    def log_metrics(
        self,
        metrics: Dict[str, Union[float, int]],
        step: Optional[int] = None,
    ) -> None:
        """Logs a collection of metrics for a run

        Args:
            metrics:
                Dictionary of metrics
            step:
                step the metrics are associated with

        """
        self._verify_active()
        self.runcard.log_metrics(metrics=metrics, step=step)

    def log_parameter(self, key: str, value: str) -> None:
        """
        Logs a parameter to project run

        Args:
            key:
                Parameter name
            value:
                Parameter value
        """

        self._verify_active()
        self.runcard.log_parameter(key=key, value=value)

    def create_or_update_runcard(self) -> None:
        """Creates or updates an active RunCard"""

        self._verify_active()

        if self.runcard.uid is not None and self.runcard.version is not None:
            CardHandler.update_card(registries=self._info.registries, card=self.runcard)
        else:
            CardHandler.register_card(registries=self._info.registries, card=self.runcard)

    @property
    def run_data(self) -> Any:
        raise NotImplementedError

    @property
    def metrics(self) -> Metrics:
        return self.runcard.metrics

    @property
    def parameters(self) -> Params:
        return self.runcard.parameters

    @property
    def tags(self) -> dict[str, Union[str, int]]:
        return self.runcard.tags

    @property
    def artifact_uris(self) -> ArtifactUris:
        return self.runcard.artifact_uris
