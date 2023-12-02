import pydantic
import pytest

from opsml.projects import types


def test_project_id() -> None:
    with pytest.raises(pydantic.ValidationError):
        types.ProjectInfo(name=None, team=None, tracking_uri="test")

    with pytest.raises(pydantic.ValidationError):
        types.ProjectInfo(name="", team="", tracking_uri="test")

    with pytest.raises(pydantic.ValidationError):
        types.ProjectInfo(name="a", team="", tracking_uri="test")

    with pytest.raises(pydantic.ValidationError):
        types.ProjectInfo(name="", team="a", tracking_uri="test")

    info = types.ProjectInfo(name="a", team="a", tracking_uri="test")
    assert info.project_id == "a:a"

    info = types.ProjectInfo(name="A", team="A", tracking_uri="test")
    assert info.project_id == "a:a"
