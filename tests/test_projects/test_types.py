import pydantic
import pytest

from opsml.projects.base import types


def test_project_id() -> None:
    with pytest.raises(pydantic.ValidationError):
        types.ProjectInfo(name=None, repository=None, tracking_uri="test")

    with pytest.raises(pydantic.ValidationError):
        types.ProjectInfo(name="", repository="", tracking_uri="test")

    with pytest.raises(pydantic.ValidationError):
        types.ProjectInfo(name="a", repository="", tracking_uri="test")

    with pytest.raises(pydantic.ValidationError):
        types.ProjectInfo(name="", repository="a", tracking_uri="test")

    info = types.ProjectInfo(name="a", repository="a", tracking_uri="test")
    assert info.project_id == "a:a"

    info = types.ProjectInfo(name="A", repository="A", tracking_uri="test")
    assert info.project_id == "a:a"
