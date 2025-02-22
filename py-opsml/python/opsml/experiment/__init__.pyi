from typing import Optional
from pathlib import Path
from datetime import datetime

class Experiment:
    def start_experiment(
        self,
        repository: Optional[str] = None,
        name: Optional[str] = None,
        code_dir: Optional[Path] = None,
        log_hardware: bool = False,
        experiment_uid: Optional[str] = None,
    ) -> "Experiment":
        """
        Start an Experiment

        Args:
            repository (str | None):
                Repository to associate with `ExperimentCard`
            name (str | None):
                Name to associate with `ExperimentCard`
            code_dir (Path | None):
                Directory to log code from
            log_hardware (bool):
                Whether to log hardware information or not
            experiment_uid (str | None):
                Experiment UID. If provided, the experiment will be loaded from the server.

        Returns:
            Experiment
        """

    def __enter__(self) -> "Experiment":
        pass

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        pass

def start_experiment(
    repository: Optional[str] = None,
    name: Optional[str] = None,
    code_dir: Optional[Path] = None,
    log_hardware: bool = False,
    experiment_uid: Optional[str] = None,
) -> Experiment:
    """
    Start an Experiment

    Args:
        repository (str | None):
            Repository to associate with `ExperimentCard`
        name (str | None):
            Name to associate with `ExperimentCard`
        code_dir (Path | None):
            Directory to log code from
        log_hardware (bool):
            Whether to log hardware information or not
        experiment_uid (str | None):
            Experiment UID. If provided, the experiment will be loaded from the server.

    Returns:
        Experiment
    """

class Metric:
    def __init__(
        self,
        name: str,
        value: float,
        step: Optional[int] = None,
        timestamp: Optional[int] = None,
        created_at: Optional[datetime] = None,
    ) -> None:
        """
        Initialize a Metric

        Args:
            name (str):
                Name of the metric
            value (float):
                Value of the metric
            step (int | None):
                Step of the metric
            timestamp (int | None):
                Timestamp of the metric
            created_at (datetime | None):
                Created at of the metric
        """

    @property
    def name(self) -> str:
        """
        Name of the metric
        """

    @property
    def value(self) -> float:
        """
        Value of the metric
        """

    @property
    def step(self) -> Optional[int]:
        """
        Step of the metric
        """

    @property
    def timestamp(self) -> Optional[int]:
        """
        Timestamp of the metric
        """

    @property
    def created_at(self) -> Optional[datetime]:
        """
        Created at of the metric
        """
