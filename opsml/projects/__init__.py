# pylint: skip-file
# mypy: ignore-errors

from opsml.projects.base.project import OpsmlProject
from opsml.projects.base.types import ProjectInfo

importlib = __import__("importlib")

_optional_deps = ["mlflow"]
has_mlflow = False

for dep in _optional_deps:
    try:
        importlib.import_module(dep)
        if dep == "mlflow":
            has_mlflow = True
    except ImportError as error:
        pass

if has_mlflow:
    from opsml.projects.mlflow import MlflowProject


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
        from opsml.projects.mlflow.project import MlflowProject

        return MlflowProject(info)
    else:
        raise ValueError("Unknown experiment type")
