def test_version():
    from opsml.version import __version__

    assert int(__version__.split(".")[0]) == 2


def test_version_fail():
    from opsml.version import get_version

    version = get_version("fail")
    assert version == "unknown"
