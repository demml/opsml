from opsml.app.routes.utils import get_registry_type_from_table, replace_proxy_root
from opsml.registry.cards.types import RegistryType


def test_replace_proxy():
    fake_url = "artifacts:/1/blah/"
    storage_root = "gs://bucket"
    proxy_root = "artifacts:/"

    record = {"name": "test", "modelcard_uri": fake_url}
    new_record = replace_proxy_root(card=record, storage_root=storage_root, proxy_root=proxy_root)

    assert storage_root in new_record["modelcard_uri"]
    assert proxy_root not in new_record["modelcard_uri"]


def test_get_registry_type_from_table():
    registry_type = get_registry_type_from_table(registry_type=RegistryType.MODEL.value)
    assert registry_type == RegistryType.MODEL.value

    registry_type = get_registry_type_from_table(table_name="OPSML_MODEL_REGISTRY")
    assert registry_type == RegistryType.MODEL.value
