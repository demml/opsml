import pytest
from opsml.registry.sql.semver import get_version_to_search, CardVersion, SemVerUtils, VersionType
from pytest_lazyfixture import lazy_fixture


def test_semver(db_registries):
    model_registry = db_registries["model"]

    for i in range(0, 10):
        expected_version = f"1.{i+1}.0"
        new_version = SemVerUtils.increment_version(
            version=f"1.{i}.0",
            version_type=VersionType.MINOR,
            pre_tag="rc",
            build_tag="build",
        )

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


def test_card_version():
    version = "1.0.0"

    version = CardVersion(version=version)
    assert version.major == "1"
    assert version.minor == "0"
    assert version.patch == "0"
    assert version.is_full_semver == True

    assert version.has_major_minor == True


def test_card_version_fail():
    version = "1.0"

    version = CardVersion(version=version)
    assert version.major == "1"
    assert version.minor == "0"

    with pytest.raises(IndexError) as ve:
        assert version.patch == "0"


def test_tags():
    version = SemVerUtils.add_tags(
        version="1.0.0",
        pre_tag="rc",
        build_tag="build",
    )

    assert version == "1.0.0-rc+build"
