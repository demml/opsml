# pylint: disable=invalid-envvar-value
from typing import Any, Dict, Optional

from opsml.helpers.logging import ArtifactLogger
from opsml.registry import CardRegistries, CardRegistry, RunCard, VersionType, DataCard, ModelCard
from opsml.registry.cards.cards import ArtifactCard
from opsml.registry.cards.types import CardInfo, CardType
from opsml.registry.storage.artifact_storage import save_record_artifact_to_storage
from opsml.registry.storage.storage_system import StorageClientType
from opsml.registry.storage.types import ArtifactStorageSpecs

logger = ArtifactLogger.get_logger(__name__)


# dataclass inheritance doesnt handle default vals well for <= py3.9
class RunInfo:
    def __init__(
        self,
        storage_client: StorageClientType,
        registries: CardRegistries,
        runcard: RunCard,
        run_id: str,
        run_name: Optional[str] = None,
    ):
        self.storage_client = storage_client
        self.registries = registries
        self.runcard = runcard
        self.run_id = run_id
        self.run_name = run_name


class CardHandler:
    """DRY helper class for ActiveRun and MlflowProject"""

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
    def load_card(registries: CardRegistries, card_type: str, info: CardInfo) -> ArtifactCard:
        """Loads an ArtifactCard"""

        registry: CardRegistry = getattr(registries, card_type)
        return registry.load_card(name=info.name, team=info.team, version=info.version, uid=info.uid)

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
        self.runcard.add_tag(key=key, value=value)

    def add_tags(self, tags: Dict[str, str]) -> None:
        """
        Adds a tag to the current run

        Args:
            tags:
                Dictionary of key, value tags

        """
        for key, value in tags.items():
            self.add_tag(key=key, value=value)

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

        # add runuid to card
        if isinstance(card, DataCard) or isinstance(card, ModelCard):
            card.runcard_uids.append(self.runcard.uid)

        CardHandler.register_card(
            registries=self._info.registries,
            card=card,
            version_type=version_type,
        )

        tag_key = f"{card.card_type}-{card.name}"
        self.add_tag(key=tag_key, value=str(card.version))

        # add uid to RunCard
        self.runcard.add_card_uid(card_type=card.card_type, uid=str(card.uid))

    def load_card(self, card_type: str, info: CardInfo) -> ArtifactCard:
        """
        Loads an ArtifactCard.

        Args:
            card_type:
                Type of card to load (data, model, run, pipeline)
            info:
                Card information to retrieve. `uid` takes precedence if it
                exists. If the optional `version` is specified, that version
                will be loaded. If it doesn't exist, the most recent ersion will
                be loaded.

        Returns
            `ArtifactCard`
        """
        card_type = CardType(card_type.lower()).value

        return CardHandler.load_card(
            registries=self._info.registries,
            card_type=card_type,
            info=info,
        )

    def log_artifact(self, name: str, artifact: Any) -> None:
        """
        Append any artifact associated with your run to
        an ActiveRun. Artifact must be pickleable
        (saved with joblib)

        Args:
            name:
                Artifact name
            artifact:
                Artifact
        """
        spec = ArtifactStorageSpecs(save_path="misc", filename=name)
        self._info.storage_client.storage_spec = spec

        storage_path = save_record_artifact_to_storage(
            artifact=artifact,
            storage_client=self._info.storage_client,
            artifact_type="joblib",
        )

        self.runcard.add_artifact_uri(name=name, uri=storage_path.uri)

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
        self.runcard.log_param(key=key, value=value)

    def create_or_update_runcard(self):
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
    def metrics(self) -> dict[str, float]:
        raise self.runcard.metrics

    @property
    def params(self) -> dict[str, str]:
        return self.runcard.params

    @property
    def tags(self) -> dict[str, str]:
        raise self.runcard.tags
