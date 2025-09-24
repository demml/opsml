from opsml.mock import OpsmlTestServer
from pathlib import Path
import os
from opsml.cli import lock_service
from opsml.genai import list_mcp_servers

CURRENT_DIRECTORY = Path(os.getcwd())
ASSETS_DIRECTORY = CURRENT_DIRECTORY / "tests" / "service" / "mcp"


def test_mcp_registration():
    with OpsmlTestServer(True, CURRENT_DIRECTORY):
        lock_service(ASSETS_DIRECTORY / "mcpspec1.yml")
        lock_service(ASSETS_DIRECTORY / "mcpspec2.yml")

        servers = list_mcp_servers()
        assert len(servers) == 2
