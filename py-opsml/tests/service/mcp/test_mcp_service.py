from opsml.mock import OpsmlTestServer
from pathlib import Path
import os
from opsml.cli import register_service
from opsml.genai import list_mcp_servers
import time

CURRENT_DIRECTORY = Path(os.getcwd())
ASSETS_DIRECTORY = CURRENT_DIRECTORY / "tests" / "service" / "mcp"


def test_mcp_registration():
    with OpsmlTestServer(True, CURRENT_DIRECTORY):
        register_service(ASSETS_DIRECTORY / "mcpspec1.yml")
        register_service(ASSETS_DIRECTORY / "mcpspec2.yml")

        # register mcpspec1 again to verify new version handling
        time.sleep(1)  # ensure timestamp difference
        register_service(ASSETS_DIRECTORY / "mcpspec1.yml")

        # servers = list_mcp_servers()
        # assert len(servers) == 2
        #
        # print(servers)
        #
        # servers = list_mcp_servers(name="mcp-service1")
        # assert servers[0].version == "0.2.0"

        # list servers by tag
        servers = list_mcp_servers(tags=["blah"])
        assert len(servers) == 1
        assert servers[0].name == "mcp-service2"
