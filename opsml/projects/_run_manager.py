# pylint: disable=invalid-envvar-value,disable=protected-access
# Copyright (c) Shipt, Inc.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import concurrent
import time
import uuid
from typing import Dict, Optional, Union, cast

from opsml.cards import RunCard
from opsml.helpers.logging import ArtifactLogger
from opsml.projects._hw_metrics import HardwareMetricsLogger
from opsml.projects.active_run import ActiveRun, RunInfo
from opsml.projects.types import _DEFAULT_INTERVAL, ProjectInfo, Tags
from opsml.registry import CardRegistries
from opsml.types import CommonKwargs

from queue import Queue

logger = ArtifactLogger.get_logger()


def run_hardware_logger(interval: int, run: "ActiveRun") -> bool:
    hw_logger = HardwareMetricsLogger(interval=interval)

    while run.active: # producer function for hw output
        metrics = hw_logger.get_metrics()
        # add to the queue
        run.queue.put(metrics, block=False)
        logger.info("Metrics in queue: {}", metrics)
        time.sleep(interval)
    # all done
    run.queue.put(None)
    logger.info("Hardware logger stopped")

    return False

def return_hw_metrics(interval: int, run: "ActiveRun"):

    while run.active: # consumer function for hw output
        # get a unit of work
        metrics_unit = run.queue.get()
        # check for stop
        if metrics_unit is None:
            continue
        # report
        logger.info("Got metrics: {}", metrics_unit)
        time.sleep(interval + 0.5)
    
    return metrics_unit

class ActiveRunException(Exception): ...


class _RunManager:
    def __init__(self, project_info: ProjectInfo, registries: CardRegistries):
        """
        Manages runs for a given project including storing general attributes and creating, activating and
        ending runs. Also holds storage client needed to store artifacts associated with a run.

        Args:
            project_info:
                ProjectInfo
            registries:
                CardRegistries
        """

        self._project_info = project_info
        self.active_run: Optional[ActiveRun] = None
        self.registries = registries

        run_id = project_info.run_id
        if run_id is not None:
            self._verify_run_id(run_id)
            self.run_id = run_id
            self._run_exists = self._card_exists(run_id=self.run_id)

        else:
            self.run_id = None
            self._run_exists = False

    @property
    def project_id(self) -> int:
        assert self._project_info.project_id is not None, "project_id should not be None"
        return self._project_info.project_id

    @property
    def run_hash(self) -> str:
        """Returns the first 7 characters of the run_id"""
        assert self.run_id is not None, "run_id should not be None"
        return self.run_id[:7]

    @property
    def base_tags(self) -> Dict[str, Union[str, float, int]]:
        return {
            Tags.NAME.value: self._project_info.name,
            Tags.ID.value: self.project_id,
        }

    def _card_exists(self, run_id: str) -> bool:
        """Verifies the run exists for the given project."""
        assert self.run_id is not None, "run_id should not be None"
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
        # set run_id
        if self.run_id is None:
            self.run_id = uuid.uuid4().hex

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
            contact=self._project_info.contact,
            uid=self.run_id,
            project=self._project_info.name,
        )

    def verify_active(self) -> None:
        """This fails if ActiveRun is None"""
        if self.active_run is None:
            raise ValueError("No ActiveRun has been set")

    def _log_hardware_metrics(self, interval: int) -> None:
        assert self.active_run is not None, "active_run should not be None"

        # run hardware logger in background thread
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=2)
        executor.submit(run_hardware_logger, interval, self.active_run)
        executor.submit(return_hw_metrics, interval, self.active_run)

    def start_run(
        self,
        run_name: Optional[str] = None,
        log_hardware: bool = False,
        hardware_interval: int = _DEFAULT_INTERVAL,
    ) -> ActiveRun:
        """
        Starts a project run

        Args:
            run_name:
                Optional run name
            log_hardware:
                Log hardware metrics
            hardware_interval:
                Interval to log hardware metrics
        """

        if self.active_run is not None:
            raise ActiveRunException("Could not start run. Another run is currently active")

        active_run = self._create_active_opsml_run(run_name)

        # don't need to add tags to already registered card
        if active_run.runcard.version != CommonKwargs.BASE_VERSION.value:
            active_run.add_tags(tags=self.base_tags)

        logger.info("starting run: {}", self.run_hash)

        # Create the RunCard when the run is started to obtain a version and
        # storage path for artifact storage to use.
        active_run.create_or_update_runcard()
        self.active_run = active_run

        if log_hardware:
            _queue = Queue()
            self.active_run._queue = _queue
            self._log_hardware_metrics(hardware_interval)

        return self.active_run

    def end_run(self) -> None:
        """Ends a Run"""

        self.verify_active()

        logger.info("ending run: {}", self.run_hash)
        assert self.active_run is not None, "active_run should not be None"
        self.active_run.create_or_update_runcard()

        #
        # Reset all active run state back to "not running" defaults
        #
        self.active_run._active = (  # pylint: disable=protected-access
            False  # prevent use of detached run outside of context manager
        )
        self.active_run = None
        self.run_id = None
        self._run_exists = False
