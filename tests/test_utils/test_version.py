def test_version():
    from opsml.version import __version__

    assert int(__version__.split(".")[0]) == 1
