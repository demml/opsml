from typing import Optional

class Experiment:
    def start_run(
        self,
        repository: Optional[str] = None,
        name: Optional[str] = None,
        code_dir: Optional[str] = None,
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
            code_dir (str | None):
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

def start_run(
    repository: Optional[str] = None,
    name: Optional[str] = None,
    code_dir: Optional[str] = None,
    log_hardware: bool = False,
) -> Experiment:
    """
    Start an Experiment

    Args:
        repository (str | None):
            Repository to associate with `ExperimentCard`
        name (str | None):
            Name to associate with `ExperimentCard`
        code_dir (str | None):
            Directory to log code from
        log_hardware (bool):
            Whether to log hardware information or not
        experiment_uid (str | None):
            Experiment UID. If provided, the experiment will be loaded from the server.

    Returns:
        Experiment
    """
