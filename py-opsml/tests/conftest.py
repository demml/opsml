import pytest

from opsml.core import Feature, RustyLogger, LoggingConfig, LogLevel
from opsml.card import RegistryTestHelper

from typing import Tuple, Dict
from pydantic import BaseModel

# Sets up logging for tests
RustyLogger.setup_logging(LoggingConfig(log_level=LogLevel.Debug))


class MockInterface(BaseModel):
    is_interface: bool = True


@pytest.fixture
def card_args() -> Tuple[Dict[str, Feature], Dict[str, str]]:
    Feature_map = {"Feature1": Feature("type1", [1, 2, 3], {"arg1": "value1"})}
    metadata = {"key1": "value1"}
    return Feature_map, metadata


@pytest.fixture
def mock_interface(
    card_args: Tuple[Dict[str, Feature], Dict[str, str]],
) -> MockInterface:
    Feature_map, metadata = card_args
    return MockInterface()


@pytest.fixture
def mock_db():
    helper = RegistryTestHelper()

    helper.setup()

    yield

    helper.cleanup()
