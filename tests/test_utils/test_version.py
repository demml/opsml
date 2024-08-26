def test_version() -> None:
    from opsml.version import __version__

    assert int(__version__.split(".")[0]) == 3


def test_version_fail() -> None:
    from opsml.version import get_version

    version = get_version("fail")
    assert version == "unknown"
