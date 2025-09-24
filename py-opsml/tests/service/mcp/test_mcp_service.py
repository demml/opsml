from opsml.mock import OpsmlTestServer
from pathlib import Path
import os
from opsml.cli import lock_service

CURRENT_DIRECTORY = Path(os.getcwd())
ASSETS_DIRECTORY = CURRENT_DIRECTORY / "tests" / "service" / "mcp"


def test_mcp_registration():
    with OpsmlTestServer(True, CURRENT_DIRECTORY):
        mcp_service1 = lock_service(ASSETS_DIRECTORY / "mcpspec1.yml")
