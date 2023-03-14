from pathlib import Path
from unittest.mock import patch
import pytest


# need to overwrite the mocked pathlib from root
@pytest.fixture(scope="session", autouse=True)
def mock_pathlib():
    with patch("pathlib.Path", Path) as mocked_pathlib:
        yield mocked_pathlib
