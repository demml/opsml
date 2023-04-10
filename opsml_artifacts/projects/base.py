# pylint: disable=invalid-envvar-value
from typing import Optional, Any, Iterator, cast
from contextlib import contextmanager
import os

from opsml_artifacts.helpers.logging import ArtifactLogger

from opsml_artifacts.projects.types import RunInfo, ProjectInfo
from opsml_artifacts.projects._active_run import ActiveRun, CardHandler
from opsml_artifacts.projects._run_manager import _RunManager
from opsml_artifacts.registry.cards import ArtifactCard
from opsml_artifacts.registry.cards.types import CardInfo, CardType
from opsml_artifacts.helpers.types import OpsmlUri

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

        tracking_uri = info.tracking_uri or os.getenv(OpsmlUri.TRACKING_URI)

        # Set the run manager
        self._run_mgr = _RunManager(
            run_id=info.run_id,
            project_id=info.project_id,
            project_info=info,
        )
