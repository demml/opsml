from opsml.test import OpsmlTestServer
from opsml.card import CardRegistry, RegistryType, RegistryMode


def test_server():
    with OpsmlTestServer() as _server:
        reg = CardRegistry(registry_type=RegistryType.Model)

        assert reg.registry_type == RegistryType.Model
        assert reg.mode == RegistryMode.Client

    a
