from unittest import mock

from opsml.registry import CardRegistries
from opsml.scouter.client import ScouterApiClient


@mock.patch("opsml.scouter.server.ScouterServerClient.healthcheck")
@mock.patch("opsml.scouter.integration.ScouterClient.server_running")
def test_healthcheck(server: mock.MagicMock, mock_request: mock.MagicMock, api_registries: CardRegistries) -> None:
    server.return_value = True
    mock_request.return_value = True
    client = ScouterApiClient()
    assert client.healthcheck() is True


@mock.patch("opsml.scouter.server.ScouterServerClient.update_drift_profile_status")
@mock.patch("opsml.scouter.integration.ScouterClient.server_running")
def test_update_profile_status(
    server: mock.MagicMock, mock_request: mock.MagicMock, api_registries: CardRegistries
) -> None:
    server.return_value = True
    mock_request.return_value = {"status": "success", "message": "Profile updated"}
    client = ScouterApiClient()
    updated = client.update_drift_profile_status("mlops", "model", "0.1.0", True)

    assert updated == {"status": "success", "message": "Profile updated"}
