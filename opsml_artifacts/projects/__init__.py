# pylint: skip-file
# mypy: ignore-errors

from opsml_artifacts.projects.base.project import OpsmlProject
from opsml_artifacts.projects.base.types import ProjectInfo

importlib = __import__("importlib")

_optional_deps = ["mlflow"]

for dep in _optional_deps:
    try:
        importlib.import_module(dep)
        if dep == "mlflow":
            from opsml_artifacts.projects import mlflow
    except ImportError as error:
        raise error


def get_project(info: ProjectInfo) -> OpsmlProject:
    """Retrieves or creates a project.

    If the project doesn't exist in the underlying system, a new project will be
    created.

     Args:
        info: Experiment to retrieve. `name` and `team` are required.

    Returns:
        A new or existing experiment.

    """
    if isinstance(info, ProjectInfo):
        from opsml_artifacts.projects.mlflow.project import MlflowProject

        return MlflowProject(info)
    else:
        raise ValueError("Unknown experiment type")
