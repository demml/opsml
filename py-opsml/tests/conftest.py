import pytest

from opsml.data import DataInterface
# from opsml.core import SchemaFeature

from opsml._opsml import RegistryTestHelper
from typing import Tuple, Dict
from pydantic import BaseModel


class MockInterface(BaseModel):
    is_interface: bool = True


@pytest.fixture
def card_args() -> Tuple[Dict[str, SchemaFeature], Dict[str, str]]:
    SchemaFeature_map = {
        "SchemaFeature1": SchemaFeature("type1", [1, 2, 3], {"arg1": "value1"})
    }
    metadata = {"key1": "value1"}
    return SchemaFeature_map, metadata


@pytest.fixture
def mock_interface(
    card_args: Tuple[Dict[str, SchemaFeature], Dict[str, str]],
) -> MockInterface:
    SchemaFeature_map, metadata = card_args
    return MockInterface()


@pytest.fixture
def mock_db():
    helper = RegistryTestHelper()

    helper.setup()

    yield

    helper.cleanup()
