from opsml.test import OpsmlTestServer
from opsml.card import CardRegistry, RegistryType


def test_server():
    with OpsmlTestServer() as _server:
        reg = CardRegistry(registry_type=RegistryType.Model)

    a
