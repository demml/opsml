# Test registering an agent service from the cli
from tests.conftest import WINDOWS_EXCLUDE
import pytest
from pathlib import Path
import os
from opsml.mock import OpsmlTestServer
from opsml.cli import lock_service, install_service
from opsml.app import AppState
import shutil
import yaml

# Set current directory
CURRENT_DIRECTORY = Path(__file__).parent / "assets1"


def append_message_to_prompt(prompt_path: Path, message: str):
    with open(prompt_path, "r") as f:
        prompt_data = yaml.safe_load(f)
    prompt_data["prompt"]["messages"].append(message)

    with open(prompt_path, "w") as f:
        yaml.safe_dump(prompt_data, f)


@pytest.mark.skipif(WINDOWS_EXCLUDE, reason="skipping")
def test_pyproject_app_lock_service():
    """
    Test that the lock service can be run on a pyproject app with a service that has cards with paths.
    Also check to ensure that locking with same content does not increment service version
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

        # Check if the lock file version is correct
        app_state1 = AppState.from_path(opsml_service)
        assert app_state1.service.version == "0.1.0"
        shutil.rmtree(opsml_service)
        os.remove(lock_file)

        assert not lock_file.exists()

        # lock the service again. This should not fail and should not change the lock file
        lock_service(CURRENT_DIRECTORY / "agent_card.yaml")
        install_service(CURRENT_DIRECTORY, CURRENT_DIRECTORY)
        app_state2 = AppState.from_path(opsml_service)
        assert app_state2.service.version == "0.1.0"
        assert app_state1.service.uid == app_state2.service.uid

        # remove
        shutil.rmtree(opsml_service)
        os.remove(lock_file)


@pytest.mark.skipif(WINDOWS_EXCLUDE, reason="skipping")
def test_pyproject_app_lock_service_change():
    """
    Test that the lock service can be run on a pyproject app with a service that has cards with paths.
    Also check to ensure that locking with same content does not increment service version
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

        # Check if the lock file version is correct
        app_state1 = AppState.from_path(opsml_service)
        assert app_state1.service.version == "0.1.0"
        shutil.rmtree(opsml_service)
        os.remove(lock_file)
        assert not lock_file.exists()

        prompt_file_yaml = CURRENT_DIRECTORY / "prompts" / "my_prompt.yaml"
        # make copy of prompt file to revert back to later
        prompt_file_yaml_copy = CURRENT_DIRECTORY / "prompts" / "my_prompt_copy.yaml"
        shutil.copy(prompt_file_yaml, prompt_file_yaml_copy)

        # append message to prompt yaml to change the content hash
        append_message_to_prompt(
            prompt_file_yaml, "This is a new message to change the prompt content hash"
        )

        # lock the service again. This should trigger a new prompt and agent service
        lock_service(CURRENT_DIRECTORY / "agent_card.yaml")
        install_service(CURRENT_DIRECTORY, CURRENT_DIRECTORY)
        app_state2 = AppState.from_path(opsml_service)
        assert app_state2.service.version == "0.2.0"
        assert app_state1.service.uid != app_state2.service.uid

        # remove
        shutil.rmtree(opsml_service)
        os.remove(lock_file)

        # revert the prompt file to original state
        shutil.move(prompt_file_yaml_copy, prompt_file_yaml)
