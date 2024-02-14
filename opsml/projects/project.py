# pylint: disable=invalid-envvar-value
# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
# pylint: disable=protected-access

from contextlib import contextmanager
from typing import Any, Dict, Iterator, List, Optional, Union, cast

from opsml.cards.base import ArtifactCard
from opsml.cards.project import ProjectCard
from opsml.cards.run import RunCard
from opsml.helpers.logging import ArtifactLogger
from opsml.projects._run_manager import ActiveRunException, _RunManager
from opsml.projects.active_run import ActiveRun, CardHandler
from opsml.projects.types import ProjectInfo
from opsml.registry import CardRegistries
from opsml.registry.sql.base.client import ClientProjectCardRegistry
from opsml.types import CardInfo, CardType, Metric, Metrics, Param, Params

logger = ArtifactLogger.get_logger()


class _ProjectRegistrar:
    def __init__(self, project_info: ProjectInfo):
        self._project_info = project_info
        self.registries = CardRegistries()

    @property
    def project_registry(self) -> ClientProjectCardRegistry:
        # both server and client registries are the same for methods
        return cast(ClientProjectCardRegistry, self.registries.project._registry)

    def register_project(self) -> int:
        """
        Checks if the project name exists in the project registry. A ProjectCard is created if it
        doesn't exist.

        Returns:
            project_id: int
        """

        card = ProjectCard(
            name=self._project_info.name,
            repository=self._project_info.repository,
            contact=self._project_info.contact,
        )
        self.registries.project.register_card(card=card)

        return card.project_id


class OpsmlProject:
    def __init__(self, info: ProjectInfo):
        """
        Instantiates a project which creates cards, metrics and parameters to
        the opsml registry via a "run" object.

        If info.run_id is set, that run_id will be loaded as read only. In read
        only mode, you can retrieve cards, metrics, and parameters, however you
        cannot write new data. If you wish to record data/create a new run, you will
        need to enter the run context.

        In order to create new cards, you need to create a run using the `run`
        context manager.

        Example:

            project: OpsmlProject = OpsmlProject(
                ProjectInfo(
                    name="test-project",
                    # If run_id is omitted, a new run is created.
                    run_id="123ab123kaj8u8naskdfh813",
                )
            )
            # the project is in "read only" mode. all read operations will work
            for k, v in project.parameters:
                logger.info("{} = {}", k, v)

            # creating a project run
            with project.run() as run:
                # Now that the run context is entered, it's in read/write mode
                # You can write cards, parameters, and metrics to the project.
                run.log_parameter(key="my_param", value="12.34")

        Args:
            info:
                Run information. if a run_id is given, that run is set
                as the project's current run.
        """
        # Set the run manager and project_id (creates ProjectCard if project doesn't exist)
        registrar = _ProjectRegistrar(project_info=info)

        # get project id or register new project
        info.project_id = registrar.register_project()

        # crete run manager
        self._run_mgr = _RunManager(project_info=info, registries=registrar.registries)

    @property
    def run_id(self) -> str:
        """Current run id associated with project"""
        if self._run_mgr.run_id is not None:
            return self._run_mgr.run_id
        raise ValueError("Run id not set for current project")

    @run_id.setter
    def run_id(self, run_id: str) -> None:
        """Set the run_id to use with the active project"""
        self._run_mgr.run_id = run_id

    @property
    def project_id(self) -> int:
        return self._run_mgr.project_id

    @property
    def project_name(self) -> str:
        return self._run_mgr._project_info.name  # pylint: disable=protected-access

    @contextmanager
    def run(self, run_name: Optional[str] = None) -> Iterator[ActiveRun]:
        """
        Starts a new run for the project

        Args:
            run_name:
                Optional run name
        """

        try:
            yield self._run_mgr.start_run(run_name=run_name)  # self._run_mgr.active_run

        except ActiveRunException as error:
            logger.error("Run already active. Ending run.")
            raise error

        except Exception as error:
            logger.error("Error encountered. Ending run. {}", error)
            self._run_mgr.end_run()
            raise error

        self._run_mgr.end_run()

    def load_card(self, registry_name: str, info: CardInfo) -> ArtifactCard:
        """
        Loads an ArtifactCard.

        Args:
            registry_name:
                Name of registry to load card from
            info:
                Card information to retrieve. `uid` takes precedence if it
                exists. If the optional `version` is specified, that version
                will be loaded. If it doesn't exist, the most recent ersion will
                be loaded.

        Returns
            `ArtifactCard`
        """
        card_type = CardType(registry_name.lower()).value
        return CardHandler.load_card(
            registries=self._run_mgr.registries,
            registry_name=card_type,
            info=info,
        )

    def list_runs(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Lists all runs for the current project, sorted by timestamp

        Returns:
            List of RunCard
        """
        logger.info("Listing runs for project {}", self.project_name)

        project_runs = self._run_mgr.registries.run._registry.list_cards(  # pylint: disable=protected-access
            limit=limit,
            query_terms={"project": self.project_name},
        )

        return sorted(project_runs, key=lambda k: k["timestamp"], reverse=True)

    @property
    def runcard(self) -> RunCard:
        return cast(RunCard, self._run_mgr.registries.run.load_card(uid=self.run_id))

    @property
    def metrics(self) -> Metrics:
        runcard = self.runcard
        runcard.load_metrics()
        return runcard.metrics

    def get_metric(self, name: str) -> Union[List[Metric], Metric]:
        """
        Get metric by name

        Args:
            name: str

        Returns:
            List of Metric or Metric

        """
        return self.runcard.get_metric(name=name)

    @property
    def parameters(self) -> Params:
        return self.runcard.parameters

    def get_parameter(self, name: str) -> Union[List[Param], Param]:
        """
        Get param by name

        Args:
            name: str

        Returns:
            List of Param or Param

        """
        return self.runcard.get_parameter(name=name)

    @property
    def tags(self) -> Dict[str, Union[str, int]]:
        return self.runcard.tags

    @property
    def datacard_uids(self) -> List[str]:
        """DataCards associated with the current run"""
        return self.runcard.datacard_uids

    @property
    def modelcard_uids(self) -> List[str]:
        """ModelCards associated with the current run"""
        return self.runcard.modelcard_uids
