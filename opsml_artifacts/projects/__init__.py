# pylint: skip-file
# mypy: ignore-errors

from opsml_artifacts.projects import types

importlib = __import__("importlib")

_optional_deps = ["mlflow"]

for dep in _optional_deps:
    try:
        importlib.import_module(dep)
        if dep == "mlflow":
            from opsml_artifacts.projects import mlflow
    except ImportError:
        pass


def get_project(info: mlflow.ProjectInfo) -> types.Project:
    """Retrieves or creates a project.

    If the project doesn't exist in the underlying system, a new project will be
    created.

     Args:
        info: Experiment to retrieve. `name` and `team` are required.

    Returns:
        A new or existing experiment.

    """
    if isinstance(info, mlflow.MlFlowProjectInfo):
        return mlflow.MlFlowProject(info)
    else:
        raise ValueError("Unknown experiment type")
