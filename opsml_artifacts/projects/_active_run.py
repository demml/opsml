# pylint: disable=invalid-envvar-value
from typing import Optional, Any, Iterator, cast
from dataclasses import dataclass
from contextlib import contextmanager

from opsml_artifacts import VersionType, CardRegistry
from opsml_artifacts.helpers.logging import ArtifactLogger
from opsml_artifacts.projects.types import CardRegistries, RunInfo

from opsml_artifacts.registry.cards import ArtifactCard, RunCard
from opsml_artifacts.registry.cards.types import CardInfo, CardName

logger = ArtifactLogger.get_logger(__name__)


class CardHandler:
    """DRY helper class for ActiveRun and MlflowProject"""

    @staticmethod
    def register_card(
        registries: CardRegistries,
        card_type: str,
        card: ArtifactCard,
        version_type: VersionType = VersionType.MINOR,
    ) -> None:
        """Registers and ArtifactCard"""
        registry: CardRegistry = getattr(registries, card_type)
        registry.register_card(card=card, version_type=version_type)

    @staticmethod
    def load_card(
        registries: CardRegistries,
        card_type: str,
        info: CardInfo,
    ) -> ArtifactCard:
        """Loads an ArtifactCard"""
        registry: CardRegistry = getattr(registries, card_type)
        return registry.load_card(name=info.name, team=info.team, version=info.version, uid=info.uid)


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
        self.card = RunCard(
            name=run_info.project_info.name,
            team=run_info.project_info.team,
            user_email=run_info.project_info.user_email,
        )

    @property
    def run_id(self) -> str:
        """Run id for current mlflow run"""
        return self._info.run_id

    @property
    def run_name(self) -> Optional[str]:
        """Run id for current mlflow run"""
        return self._info.run_name

    @property
    def active(self) -> bool:
        return self._active

    def _verify_active(self):
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

        raise NotImplementedError

    def register_card(self, card: ArtifactCard, version_type: VersionType = VersionType.MINOR):
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
        card_type = card.__class__.__name__.lower()

        CardHandler.register_card(
            registries=self._info.registries,
            card_type=card_type,
            card=card,
            version_type=version_type,
        )

        tag_key = f"{card_type}-{card.name}"
        self.add_tag(
            key=tag_key,
            value=str(card.version),
        )

    def load_card(self, card_type: str, info: CardInfo) -> ArtifactCard:
        """
        Loads an ArtifactCard.

        Args:
            card_type:
                datacard or modelcard
            info:
                Card information to retrieve. `uid` takes precedence if it
                exists. If the optional `version` is specified, that version
                will be loaded. If it doesn't exist, the most recent ersion will
                be loaded.

        Returns
            `ArtifactCard`
        """
        card_type = CardName(card_type.lower()).name.lower()
        return CardHandler.load_card(
            registries=self._info.registries,
            card_type=card_type,
            info=info,
        )

    def log_artifact(self, local_path: str, artifact_path: Optional[str] = None) -> None:
        """
        Logs an artifact for the current run. All artifacts are loaded
        to a parent directory named "misc".

        Args:
            local_path:
                Local path to object
            artifact_path:
                Artifact directory path in Mlflow to log to. This path will be appended
                to parent directory "misc"
        Returns:
            None
        """
        raise NotImplementedError

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
        self._info.mlflow_client.log_metric(
            run_id=self.run_id,
            key=key,
            value=value,
            timestamp=timestamp,
            step=step,
        )

    def log_param(self, key: str, value: str) -> None:
        """
        Logs a parameter to project run

        Args:
            key:
                Parameter name
            value:
                Parameter value
        """

        self._verify_active()
        # self._info.registries.runcard.
        self._info.mlflow_client.log_param(run_id=self.run_id, key=key, value=value)

    @property
    def run_data(self) -> Any:
        raise NotImplementedError

    @property
    def metrics(self) -> dict[str, float]:
        raise NotImplementedError

    @property
    def params(self) -> dict[str, str]:
        raise NotImplementedError

    @property
    def tags(self) -> dict[str, str]:
        raise NotImplementedError
