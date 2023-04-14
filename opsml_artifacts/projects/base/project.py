# pylint: disable=invalid-envvar-value
from contextlib import contextmanager
from typing import Iterator, List, Optional, cast

from opsml_artifacts.helpers.logging import ArtifactLogger
from opsml_artifacts.projects.base._active_run import ActiveRun, CardHandler
from opsml_artifacts.projects.base._run_manager import _RunManager
from opsml_artifacts.projects.base.types import ProjectInfo
from opsml_artifacts.registry.cards import ArtifactCard, RunCard
from opsml_artifacts.registry.cards.types import CardInfo, CardType

logger = ArtifactLogger.get_logger(__name__)


class OpsmlProject:
    def __init__(self, info: ProjectInfo):
        """
        Instantiates a project which log cards, metrics and params to
        the opsml registry via a "run" object.

        If info.run_id is set, that run_id will be loaded as read only. In read
        only mode, you can retrieve cards, metrics, and params, however you
        cannot write new data. If you wish to record data/create a new run, you will
        need to enter the run context.

        Example:

            project: OpsmlProject = get_project(
                ProjectInfo(
                    name="test-project",
                    team="devops-ml",
                    # If run_id is omitted, a new run is created.
                    run_id="123ab123kaj8u8naskdfh813",
                )
            )
            # the project is in "read only" mode. all read operations will work
            for k, v in project.params:
                logger.info("%s = %s", k, v)

            # creating a project run
            with project.run() as run:
                # Now that the run context is entered, it's in read/write mode
                # You can write cards, params, and metrics to the project.
                run.log_param(key="my_param", value="12.34")

        Args:
            info:
                Run information. if a run_id is given, that run is set
                as the project's current run.
        """
        # Set the run manager and project_id (creates ProjectCard if project doesn't exist)
        self._run_mgr = _RunManager(project_info=info)

    @property
    def run_id(self) -> str:
        """Current run id associated with project"""
        if self._run_mgr.run_id is not None:
            return self._run_mgr.run_id
        raise ValueError("Run id not set for current project")

    @run_id.setter
    def run_id(self, run_id: str):
        """Set the run_id to use with the active project"""
        self._run_mgr.run_id = run_id

    @property
    def project_id(self) -> str:
        return self._run_mgr.project_id

    @contextmanager
    def run(self, run_name: Optional[str] = None) -> Iterator[ActiveRun]:
        """
        Starts mlflow run for project

        Args:
            run_name:
                Optional run name
        """

        self._run_mgr.start_run(run_name=run_name)

        yield cast(ActiveRun, self._run_mgr.active_run)

        self._run_mgr.end_run()

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
        card_type = CardType(card_type.lower()).value
        return CardHandler.load_card(
            registries=self._run_mgr.registries,
            card_type=card_type,
            info=info,
        )

    @property
    def run_data(self):
        return cast(RunCard, self._run_mgr.registries.run.load_card(uid=self.run_id))

    @property
    def metrics(self) -> dict[str, float]:
        return self.run_data.metrics

    @property
    def params(self) -> dict[str, str]:
        return self.run_data.params

    @property
    def tags(self) -> dict[str, str]:
        return self.run_data.tags

    @property
    def datacard_uids(self) -> List[str]:
        """DataCards associated with the current run"""
        return self.run_data.datacard_uids

    @property
    def modelcard_uids(self) -> List[str]:
        """ModelCards associated with the current run"""
        return self.run_data.modelcard_uids
