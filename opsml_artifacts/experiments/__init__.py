# pylint: skip-file
# mypy: ignore-errors

from opsml_artifacts.experiments import types

importlib = __import__("importlib")

_optional_deps = ["mlflow"]

for dep in _optional_deps:
    try:
        importlib.import_module(dep)
        if dep == "mlflow":
            from opsml_artifacts.experiments import mlflow
    except ImportError:
        pass


def get_experiment(info: mlflow.ExperimentInfo) -> types.Experiment:
    """Retrieves or creates an experiment.

    Args:
        info: Experiment information. `name` and `team` are required.

    Returns:
        A new or existing experiment.

    """
    if isinstance(info, mlflow.MlFlowExperimentInfo):
        return mlflow.MlFlowExperiment(info)
    else:
        raise ValueError("Unknown experiment type")
