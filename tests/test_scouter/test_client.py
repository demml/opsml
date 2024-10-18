from unittest import mock

from opsml.registry import CardRegistries
from opsml.scouter.client import ScouterApiClient
from starlette.testclient import TestClient
from opsml.scouter.types import ObservabilityMetric


@mock.patch("opsml.scouter.server.ScouterServerClient.healthcheck")
@mock.patch("opsml.scouter.integration.ScouterClient.server_running")
def test_healthcheck(server: mock.MagicMock, mock_request: mock.MagicMock, api_registries: CardRegistries) -> None:
    server.return_value = True
    mock_request.return_value = True
    client = ScouterApiClient()
    assert client.healthcheck() is True


@mock.patch("opsml.scouter.server.ScouterServerClient.update_drift_profile_status")
@mock.patch("opsml.scouter.integration.ScouterClient.server_running")
def test_update_profile_status(server: mock.MagicMock, mock_request: mock.MagicMock, api_registries: CardRegistries) -> None:
    server.return_value = True
    mock_request.return_value = {"status": "success", "message": "Profile updated"}
    client = ScouterApiClient()
    updated = client.update_drift_profile_status("mlops", "model", "0.1.0", True)

    assert updated == {"status": "success", "message": "Profile updated"}


@mock.patch("opsml.scouter.server.ScouterServerClient.request")
@mock.patch("opsml.scouter.integration.ScouterClient.server_running")
def test_scouter_feature_distribution(
    server: mock.MagicMock,
    mock_request: mock.MagicMock,
    test_app: TestClient,
) -> None:
    server.return_value = True
    mock_request.return_value = {
        "name": "string",
        "repository": "string",
        "version": "string",
        "percentile_10": 0,
        "percentile_20": 0,
        "percentile_30": 0,
        "percentile_40": 0,
        "percentile_50": 0,
        "percentile_60": 0,
        "percentile_70": 0,
        "percentile_80": 0,
        "percentile_90": 0,
        "percentile_100": 0,
        "val_10": 0,
        "val_20": 0,
        "val_30": 0,
        "val_40": 0,
        "val_50": 0,
        "val_60": 0,
        "val_70": 0,
        "val_80": 0,
        "val_90": 0,
        "val_100": 0,
    }

    response = test_app.get(
        "/opsml/scouter/feature/distribution",
        params={
            "repository": "mlops",
            "name": "model",
            "version": "0.1.0",
            "time_window": "2day",
            "max_data_points": 10,
            "feature": "col_1",
        },
    )

    assert response.status_code == 200


@mock.patch("opsml.scouter.server.ScouterServerClient.request")
@mock.patch("opsml.scouter.integration.ScouterClient.server_running")
def test_scouter_monitor_alerts(
    server: mock.MagicMock,
    mock_request: mock.MagicMock,
    test_app: TestClient,
) -> None:
    server.return_value = True
    mock_request.return_value = [
        {
            "created_at": "2024-09-18T06:43:12",
            "name": "model",
            "repository": "mlops",
            "version": "0.1.0",
            "feature": "col_1",
            "alert": {"status": "success"},
            "status": "success",
            "id": 1,
        }
    ]

    response = test_app.get(
        "/opsml/scouter/alerts",
        params={
            "repository": "mlops",
            "name": "model",
            "version": "0.1.0",
            "active": True,
            "limit": 10,
        },
    )

    assert response.status_code == 200


@mock.patch("opsml.scouter.server.ScouterServerClient.request")
@mock.patch("opsml.scouter.integration.ScouterClient.server_running")
def test_scouter_update_monitor_alerts(
    server: mock.MagicMock,
    mock_request: mock.MagicMock,
    test_app: TestClient,
) -> None:
    server.return_value = True
    mock_request.return_value = {"status": "success", "message": "Alert updated"}

    response = test_app.put(
        "/opsml/scouter/alerts",
        json={"id": 1, "status": "acknowledged"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert response.json()["message"] == "Alert updated"


@mock.patch("opsml.scouter.server.ScouterServerClient.request")
@mock.patch("opsml.scouter.integration.ScouterClient.server_running")
def test_scouter_get_alert_metrics(
    server: mock.MagicMock,
    mock_request: mock.MagicMock,
    test_app: TestClient,
) -> None:
    server.return_value = True
    mock_request.return_value = {
        "data": {
            "created_at": ["2024-09-18T06:43:12"],
            "alert_count": [1],
            "active": [0],
            "acknowledged": [1],
        }
    }

    response = test_app.get(
        "/opsml/scouter/alerts/metrics",
        params={
            "repository": "mlops",
            "name": "model",
            "version": "0.1.0",
            "time_window": "2day",
            "max_data_points": 10,
        },
    )

    assert response.status_code == 200
    assert response.json()["created_at"] == ["2024-09-18T06:43:12"]
    assert response.json()["alert_count"] == [1]
    assert response.json()["active"] == [0]
    assert response.json()["acknowledged"] == [1]


@mock.patch("opsml.scouter.server.ScouterServerClient.request")
@mock.patch("opsml.scouter.integration.ScouterClient.server_running")
def test_scouter_update_profile_status(
    server: mock.MagicMock,
    mock_request: mock.MagicMock,
    test_app: TestClient,
) -> None:
    server.return_value = True
    mock_request.return_value = {"status": "success", "message": "Profile updated"}

    response = test_app.put(
        "/opsml/scouter/profile/status",
        json={
            "repository": "mlops",
            "name": "model",
            "version": "0.1.0",
            "active": True,
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert response.json()["message"] == "Profile updated"


@mock.patch("opsml.scouter.server.ScouterServerClient.request")
@mock.patch("opsml.scouter.integration.ScouterClient.server_running")
def test_scouter_get_observability_metrics(
    server: mock.MagicMock,
    mock_request: mock.MagicMock,
    test_app: TestClient,
) -> None:
    metric = ObservabilityMetric(
        route_name="string",
        created_at=["2024-09-18T06:43:12"],
        total_request_count=1,
        total_error_count=1,
        p5=[0.0],
        p25=[0.0],
        p50=[0.0],
        p95=[0.0],
        p99=[0.0],
        request_per_sec=[0.0],
        error_per_sec=[0.0],
        error_latency=[0.0],
        status_counts=[{"status": 1}],
    )

    server.return_value = True
    mock_request.return_value = {
        "data": [metric.model_dump()],
    }

    response = test_app.get(
        "/opsml/scouter/observability/metrics",
        params={
            "repository": "mlops",
            "name": "model",
            "version": "0.1.0",
            "time_window": "2day",
            "max_data_points": 10,
        },
    )

    assert response.status_code == 200
    assert response.json()["metrics"][0] == metric.model_dump()
