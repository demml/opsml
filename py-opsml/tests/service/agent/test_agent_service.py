# Test registering an agent service from the cli
from tests.conftest import WINDOWS_EXCLUDE
import pytest
from pathlib import Path
import os
from opsml.mock import OpsmlTestServer
from opsml.cli import lock_service, install_service

# Set current directory
CURRENT_DIRECTORY = Path(__file__).parent / "assets1"


@pytest.mark.skipif(WINDOWS_EXCLUDE, reason="skipping")
def test_pyproject_app_lock_service():
    """
    Test that the lock service can be run on a pyproject app with a service that has cards with paths.
    """

    with OpsmlTestServer(True, CURRENT_DIRECTORY):
        lock_service(CURRENT_DIRECTORY / "agent_card.yaml")

        # Check if the lock file was created
        lock_file = CURRENT_DIRECTORY / "opsml.lock"
        assert lock_file.exists()

        # download the assets
        install_service(CURRENT_DIRECTORY, CURRENT_DIRECTORY)

        # check if opsml_service was created
        opsml_service = CURRENT_DIRECTORY / "opsml_service"
        assert opsml_service.exists()

        # try and re-lock. This should not fail and should not change the lock file
