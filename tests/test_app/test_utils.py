from opsml.app.routes.utils import get_registry_type_from_table
from opsml.types import RegistryType


def test_get_registry_type_from_table():
    registry_type = get_registry_type_from_table(registry_type=RegistryType.MODEL.value)
    assert registry_type == RegistryType.MODEL.value

    registry_type = get_registry_type_from_table(table_name="OPSML_MODEL_REGISTRY")
    assert registry_type == RegistryType.MODEL.value
