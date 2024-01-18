# pylint: disable=invalid-envvar-value,disable=protected-access
# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import uuid
from typing import Dict, Optional, Union, cast

from opsml.cards import ProjectCard, RunCard
from opsml.helpers.logging import ArtifactLogger
from opsml.projects.active_run import ActiveRun, RunInfo
from opsml.projects.types import ProjectInfo, Tags
from opsml.registry import CardRegistries

logger = ArtifactLogger.get_logger()


class ActiveRunException(Exception):
    ...


class _RunManager:
    def __init__(self, project_info: ProjectInfo):
        """
        Manages runs for a given project including storing general attributes and creating, activating and
        ending runs. Also holds storage client needed to store artifacts associated with a run.

        Args:
            project_info:
                ProjectInfo
        """

        self._project_info = project_info
        self._active_run: Optional[ActiveRun] = None

        self.registries = CardRegistries()

        run_id = project_info.run_id
        if run_id is not None:
            self._verify_run_id(run_id)
            self.run_id = run_id
        else:
            self.run_id = uuid.uuid4().hex

        self._project_id = self._get_project_id()
        self._run_exists = self._card_exists(run_id=self.run_id)

    @property
    def project_id(self) -> int:
        return self._project_id

    @property
    def base_tags(self) -> Dict[str, Union[str, Optional[str], int]]:
        return {
            Tags.NAME.value: self._project_info.name,
            Tags.ID.value: self.project_id,
        }

    @property
    def active_run(self) -> ActiveRun:
        if self._active_run is not None:
            return self._active_run
        raise ValueError("No active run has been set")

    @active_run.setter
    def active_run(self, active_run: ActiveRun) -> None:
        """Sets the active run"""
        self._active_run = active_run

    def _card_exists(self, run_id: str) -> bool:
        """Verifies the run exists for the given project."""

        card = self.registries.run._registry.list_cards(uid=run_id)
        if card:
            return True
        return False

    def _verify_run_id(self, run_id: str) -> None:
        """Verifies the run exists for the given project."""

        card = self.registries.run._registry.list_cards(uid=run_id)

        if not card:
            raise ValueError("Invalid run_id")

    def _create_active_opsml_run(self, run_name: Optional[str]) -> ActiveRun:
        # Create opsml active run
        runcard = self._load_runcard(run_name)

        # create run_info
        run_info = RunInfo(run_id=self.run_id, run_name=runcard.name, runcard=runcard)

        # start active run
        return ActiveRun(run_info=run_info)

    def _load_runcard(self, run_name: Optional[str]) -> RunCard:
        """Loads a RunCard or creates a new RunCard"""

        if self._run_exists:
            runcard = self.registries.run.load_card(uid=self.run_id)
            return cast(RunCard, runcard)

        return RunCard(
            name=run_name or self.run_id[:7],  # use short run_id if no name
            repository=self._project_info.repository,
            contact="",
            uid=self.run_id,
            project=self._project_info.name,
        )

    def verify_active(self) -> None:
        """This fails if ActiveRun is None"""
        if self.active_run is None:
            raise ValueError("No ActiveRun has been set")

    def start_run(self, run_name: Optional[str] = None) -> ActiveRun:
        """
        Starts a project run

        Args:
            run_name:
                Optional run name
        """

        if self._active_run is not None:
            raise ActiveRunException("Could not start run. Another run is currently active")

        active_run = self._create_active_opsml_run(run_name)

        # don't need to add tags to already registered card
        if active_run.runcard.version is None:
            active_run.add_tags(tags=self.base_tags)

        logger.info("starting run: {}", self.run_id)

        # Create the RunCard when the run is started to obtain a version and
        # storage path for artifact storage to use.
        active_run.create_or_update_runcard()
        self.active_run = active_run

        return self.active_run

    def end_run(self) -> None:
        """Ends a Run"""

        self.verify_active()

        logger.info("ending run: {}", self.run_id)
        self.active_run.create_or_update_runcard()

        #
        # Reset all active run state back to "not running" defaults
        #
        self.active_run._active = (  # pylint: disable=protected-access
            False  # prevent use of detached run outside of context manager
        )
        self._active_run = None
        self.run_id = None

    def _get_project_id(self) -> int:
        """
        Checks if the project name exists int the project registry. A ProjectCard is created if it
        doesn't exist.

        Args:
            info:
                Project info

        """

        projects = self.registries.project.list_cards(name=self._project_info.name)
        if bool(projects):
            return int(projects[0]["project_id"])

        # get nbr of unique projects
        cards = self.registries.project.list_cards()

        if cards:
            max_project = max(card["project_id"] for card in cards)
        else:
            max_project = 0

        card = ProjectCard(
            name=self._project_info.name,
            repository=self._project_info.repository,
            contact="",
            project_id=max_project + 1,
        )
        self.registries.project.register_card(card=card)

        return card.project_id
