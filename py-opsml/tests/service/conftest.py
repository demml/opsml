from dataclasses import dataclass
from typing import Iterator
from unittest import mock

import pytest
from opsml.mock import MockConfig


@dataclass
class MockEnvironment:
    mock_config: MockConfig


@pytest.fixture
def mock_environment() -> Iterator[MockEnvironment]:
    """
    Fixture that patches HttpConfig with MockConfig for testing.

    Yields:
        MockEnvironment: Contains the mock configuration.
    """
    with mock.patch("opsml.scouter.HttpConfig", MockConfig):
        yield MockEnvironment(mock_config=MockConfig())
