# pylint: disable=invalid-envvar-value,disable=protected-access
# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import uuid
from typing import Optional, cast

from opsml.helpers.logging import ArtifactLogger
from opsml.projects.base._active_run import ActiveRun, RunInfo
from opsml.projects.base.types import ProjectInfo, Tags
from opsml.projects.base.utils import (
    get_project_id_from_registry,
    verify_runcard_project_match,
)
from opsml.registry import CardRegistries, CardRegistry, RunCard
from opsml.registry.utils.settings import settings

logger = ArtifactLogger.get_logger()


registries = CardRegistries()


class _RunManager:
    def __init__(
        self,
        project_info: ProjectInfo,
    ):
        """
        Manages runs for a given project including storing general attributes and creating, activating and
        ending runs. Also holds storage client needed to store artifacts associated with a run.

        Args:
            project_info:
                ProjectInfo
        """

        self._project_info = project_info
        self._run_id: Optional[str] = None
        self._run_name: Optional[str] = None
        self._active_run: Optional[ActiveRun] = None
        self._version: Optional[str] = None

        # in opsml, storage client comes from settings (created once during runtime)
        # storage and registries are held in run_manager and passed to active run
        self._storage_client = settings.storage_client
        self.registries = registries

        run_id = project_info.run_id
        if run_id is not None:
            self._verify_run_id(run_id)
            self._run_id = run_id

        self._project_id = self._get_project_id()

    @property
    def project_id(self) -> str:
        return self._project_id

    @property
    def storage_client(self):
        return self._storage_client

    @property
    def base_tags(self):
        return {
            Tags.NAME: self._project_info.name,
            Tags.TEAM: self._project_info.team,
            Tags.EMAIL: self._project_info.user_email,
        }

    @property
    def active_run(self) -> ActiveRun:
        if self._active_run is not None:
            return cast(ActiveRun, self._active_run)
        raise ValueError("No active run has been set")

    @active_run.setter
    def active_run(self, active_run: ActiveRun):
        """Sets the active run"""
        self._active_run = active_run

    @property
    def version(self) -> str:
        """Current RunCard version"""
        if self._version is not None:
            return self._version
        return "No version set"

    @version.setter
    def version(self, version: str) -> None:
        """Current RunCard version"""
        self._version = version

    @property
    def run_id(self) -> Optional[str]:
        """Current Run id"""
        return self._run_id

    @run_id.setter
    def run_id(self, run_id: str):
        """Set Run id"""
        self._run_id = run_id

    @property
    def run_name(self) -> Optional[str]:
        """Get current run name"""
        return self._run_name

    @run_name.setter
    def run_name(self, run_name: str) -> None:
        """Get current run name"""
        self._run_name = run_name

    def _card_exists(self, run_id: str) -> bool:
        """Verifies the run exists for the given project."""

        card = self.registries.run._registry.list_cards(uid=run_id)

        if len(card) > 0:
            if not bool(card[0]):
                return False
            return True

        if not bool(card):
            return False
        return True

    def _verify_run_id(self, run_id: str) -> None:
        """Verifies the run exists for the given project."""

        card = self.registries.run._registry.list_cards(uid=run_id)

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

        if self.run_id is not None and self._card_exists(run_id=self.run_id):
            # need run registry with API client
            run_registry = CardRegistry(registry_name="run")
            runcard = run_registry.load_card(uid=self.run_id)

            return cast(RunCard, runcard)

        return RunCard(
            name=self._project_info.name,
            team=self._project_info.team,
            user_email=self._project_info.user_email,
            uid=self.run_id,
            project_id=self._project_info.project_id,
        )

    def _restore_run(self) -> None:
        """Restores a previous RunCard"""

        self._create_active_opsml_run()

    def _create_run(self, run_name: Optional[str] = None) -> None:
        """
        Creates a RunCard

        """
        # Set run and name
        self.run_id = uuid.uuid4().hex
        self.run_name = run_name

        self._create_active_opsml_run()
        self.active_run.add_tags(tags=self.base_tags)

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
        """This fails if ActiveRun is None"""
        if self.active_run is None:
            raise ValueError("No ActiveRun has been set")

    def start_run(self, run_name: Optional[str] = None):
        """
        Starts a project run

        Args:
            run_name:
                Optional run name
        """
        # replace previous version if user is creating a run after finishing another
        self._version = None
        if self._active_run is not None:
            raise ValueError("Could not start run. Another run is currently active")

        self._set_active_run(run_name=run_name)
        logger.info("starting run: {}", self.run_id)

    def _end_run(self) -> None:
        logger.info("ending run: {}", self.run_id)
        self.active_run.create_or_update_runcard()
        self.version = cast(str, self.active_run.runcard.version)

        if self.active_run is not None:
            self.active_run._active = (  # pylint: disable=protected-access
                False  # prevent use of detached run outside of context manager
            )
        self._active_run = None  # detach active run
        # self.run_id = None  # set run manager run_id to None, so run is not accidently restarted

    def end_run(self):
        """Ends a Run"""

        # Remove run id
        self._end_run()
        self.run_id = None  # set run manager run_id to None, so run is not accidently restarted

    def _get_project_id(self) -> str:
        """
        Checks if the name and team exist as a project in the Project registry. A ProjectCard is created if it
        doesn't exist. If a run_id is provided, a check is performed to match the project_id to the run_id.

        Args:
            info:
                Project info

        """

        if self.run_id is not None:
            verify_runcard_project_match(
                project_id=self._project_info.project_id,
                run_id=self.run_id,
                runcard_registry=self.registries.run,
            )
            return self._project_info.project_id

        return get_project_id_from_registry(
            project_registry=self.registries.project,
            info=self._project_info,
        )
