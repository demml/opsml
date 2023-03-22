import pydantic
import pytest

from opsml_artifacts.projects import types


def test_project_id() -> None:
    with pytest.raises(pydantic.ValidationError):
        types.ProjectInfo(name=None, team=None)

    with pytest.raises(pydantic.ValidationError):
        types.ProjectInfo(name="", team="")

    with pytest.raises(pydantic.ValidationError):
        types.ProjectInfo(name="a", team="")

    with pytest.raises(pydantic.ValidationError):
        types.ProjectInfo(name="", team="a")

    info = types.ProjectInfo(name="a", team="a")
    assert info.project_id == "a:a"
    info = types.ProjectInfo(name="A", team="A")
    assert info.project_id == "a:a"
