import pytest
from opsml.registry.sql.registry_base import VersionType
from opsml.registry.sql.semver import get_version_to_search
from pytest_lazyfixture import lazy_fixture


def test_semvar(db_registries):
    model_registry = db_registries["model"]

    for i in range(0, 10):
        expected_version = f"1.{i+1}.0"
        new_version = model_registry.registry._increment_version(version=f"1.{i}.0", version_type=VersionType.MINOR)

        assert expected_version == new_version


def test_version_caret():
    version = "^1.1.0"

    parsed_version = get_version_to_search(version=version)
    assert parsed_version == "1"


def test_version_tilde():
    version = "~1.1.0"

    parsed_version = get_version_to_search(version=version)
    assert parsed_version == "1.1"


def test_version_star():
    version = "1.*.*"

    parsed_version = get_version_to_search(version=version)
    assert parsed_version == "1"

    version = "1.2.*"

    parsed_version = get_version_to_search(version=version)
    assert parsed_version == "1.2"


def test_version_fail():
    version = "~1.*.*"

    with pytest.raises(ValueError) as ve:
        parsed_version = get_version_to_search(version=version)
    assert ve.match("SemVer")
