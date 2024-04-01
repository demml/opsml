from opsml.app.routes.utils import get_registry_type_from_table, calculate_file_size
from opsml.types import RegistryType


def test_get_registry_type_from_table() -> None:
    registry_type = get_registry_type_from_table(registry_type=RegistryType.MODEL.value)
    assert registry_type == RegistryType.MODEL.value

    registry_type = get_registry_type_from_table(table_name="OPSML_MODEL_REGISTRY")
    assert registry_type == RegistryType.MODEL.value

def test_calculate_file_size() -> None:
    file_size = calculate_file_size(1024)
    assert file_size == "1.00 KB"

    file_size = calculate_file_size(1024 * 1024)
    assert file_size == "1.00 MB"

    file_size = calculate_file_size(1024 * 1024 * 1024)
    assert file_size == "1.00 GB"