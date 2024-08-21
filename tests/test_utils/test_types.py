import pytest

from opsml.types import RegistryTableNames


def test_registry_table_name() -> None:

    for i in ["data", "model", "run", "pipeline", "audit", "project", "metric", "parameter"]:
        table = RegistryTableNames.from_str(i)
        assert "OPSML_" in table.value

    with pytest.raises(NotImplementedError):
        RegistryTableNames.from_str("invalid")
