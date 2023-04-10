# pylint: disable=invalid-envvar-value
from typing import Optional

from opsml_artifacts import CardRegistry, RunCard
from opsml_artifacts.helpers.logging import ArtifactLogger
from opsml_artifacts.helpers.settings import settings
from opsml_artifacts.projects.base._active_run import ActiveRun
from opsml_artifacts.projects.base.types import (
    CardRegistries,
    ProjectInfo,
    RunInfo,
    Tags,
)
from opsml_artifacts.registry.storage.storage_system import StorageClientType

logger = ArtifactLogger.get_logger(__name__)


def get_card_registries(storage_client: StorageClientType):

    """Gets CardRegistries to associate with MlFlow experiment"""
    registries = CardRegistries(
        datacard=CardRegistry(registry_name="data"),
        modelcard=CardRegistry(registry_name="model"),
        runcard=CardRegistry(registry_name="run"),
    )

    # ensures proper storage client is set
    registries.set_storage_client(storage_client=storage_client)

    return registries


class _RunManager:
    def __init__(
        self,
        project_id: str,
        project_info: ProjectInfo,
        run_id: Optional[str] = None,
    ):
        """
        Manages runs for a given project including storing general attributes and creating, activating and
        ending runs. Also holds storage client needed to store artifacts associated with a run.

        Args:
            project_id:
                Project identifier
            project_info:
                ProjectInfo
            run_id:
                Optional project run id

        """

        # base attr
        self._project_id = project_id
        self._project_info = project_info
        self._run_id: Optional[str] = None
        self._run_name: Optional[str] = None
        self._active_run: Optional[ActiveRun] = None

        self.storage_client = self._get_storage_client()
        self.registries = get_card_registries(storage_client=self.storage_client)

        if run_id is not None:
            self._verify_run_id(run_id)
            self._run_id = run_id

    @property
    def base_tags(self):
        return {
            Tags.NAME: self._project_info.name,
            Tags.TEAM: self._project_info.team,
            Tags.EMAIL: self._project_info.user_email,
        }

    @property
    def run_id(self) -> Optional[str]:
        """Current Run id"""
        return self._run_id

    @run_id.setter
    def run_id(self, run_id: str):
        """Set Run id"""
        self._run_id = run_id

    @property
    def active_run(self) -> Optional[ActiveRun]:
        """Current active run"""
        return self._active_run

    @active_run.setter
    def active_run(self, active_run: ActiveRun):
        """Sets the active run"""
        self._active_run = active_run

    @property
    def run_name(self) -> Optional[str]:
        """Get current run name"""
        return self._run_name

    @run_name.setter
    def run_name(self, run_name: str) -> None:
        """Get current run name"""
        self._run_name = run_name

    def _get_storage_client(self) -> StorageClientType:
        return settings.storage_client

    def _card_exists(self, run_id: str) -> None:
        """Verifies the run exists for the given project."""

        card = self.registries.runcard.registry.list_cards(uid=run_id)

        if len(card) > 0:
            if not bool(card[0]):
                return False
            return True

        if not bool(card):
            return False
        return True

    def _verify_run_id(self, run_id: str) -> None:
        """Verifies the run exists for the given project."""

        card = self.registries.runcard.registry.list_cards(uid=run_id)

        if len(card) > 0:
            if not bool(card[0]):
                raise ValueError("Invalid run_id")

        else:
            if not bool(card):
                raise ValueError("Invalid run_id")

    def _create_active_opsml_run(self):

        # Create opsml active run
        run_info = RunInfo(
            run_id=self.run_id,
            storage_client=self.storage_client,
            run_name=self.run_name,
            registries=self.registries,
            runcard=self._load_runcard(),
        )

        self.active_run = ActiveRun(run_info=run_info)

    def _load_runcard(self) -> RunCard:
        """Loads a RunCard or creates a new RunCard"""

        if self.run_id is not None:
            if self._card_exists(run_id=self.run_id):
                return self.registries.runcard.load_card(uid=self.run_id)

        return RunCard(
            name=self._project_info.name,
            team=self._project_info.team,
            user_email=self._project_info.user_email,
        )

    def _restore_run(self) -> None:
        """Restores a previous RunCard"""

        self._create_active_opsml_run()

    def _create_run(self, run_name: Optional[str] = None) -> None:
        """
        Creates a RunCard

        """
        self._create_active_opsml_run()
        self._active_run.add_tags(tags=self.base_tags)

    def _set_active_run(self, run_name: Optional[str] = None) -> None:
        """
        Resolves and sets the active run for mlflow

        Args:
            run_name:
                Optional run name
        """

        if self.run_id is not None:
            return self._restore_run()
        return self._create_run(run_name=run_name)

    def verify_active(self) -> None:
        if self.active_run is None:
            raise ValueError("ActiveRun has not been set")

    def start_run(self, run_name: Optional[str] = None):
        """
        Starts an Mlflow run for a given project

        Args:
            run_name:
                Optional run name
        """
        if self.active_run is not None:
            raise ValueError("Could not start run. Another run is currently active")

        self._set_active_run(run_name=run_name)
        logger.info("starting run: %s", self.run_id)

    def _end_run(self) -> None:

        # set to None
        self.active_run.create_or_update_runcard()

        if self.active_run is not None:
            self.active_run._active = (  # pylint: disable=protected-access
                False  # prevent use of detached run outside of context manager
            )
        self.active_run = None  # detach active run

    def end_run(self):
        """Ends a Run"""

        # Remove run id
        logger.info("ending run: %s", self.run_id)
        self._end_run()
